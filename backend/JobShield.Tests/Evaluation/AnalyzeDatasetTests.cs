using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Serialization;
using Xunit;
using Xunit.Abstractions;

namespace JobShield.Tests.Evaluation;

public sealed class AnalyzeDatasetTests(ITestOutputHelper output)
{
    private const string SnapshotHash = "296CAB706C8E5C60FF3282286BA4E0D689EC52E9691D13676BF308A58502E6F3";
    private static readonly string SnapshotPath = Path.Combine(
        AppContext.BaseDirectory, "Evaluation", "Data", "jobshield-test-v3-64.jsonl");

    private static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web)
    {
        RespectNullableAnnotations = true,
        RespectRequiredConstructorParameters = true,
        Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        WriteIndented = true
    };
    private static readonly JsonSerializerOptions DatasetJson = new(Json)
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
    };

    [Fact]
    public void SnapshotMatchesTheHeldOutDataset()
    {
        var samples = ReadSamples();
        Assert.Equal(64, samples.Length);
        Assert.Equal(64, samples.Select(s => s.SampleId).Distinct().Count());
        Assert.Equal(33, samples.Count(s => s.OverallLabel == "suspicious"));
        Assert.Equal(31, samples.Count(s => s.OverallLabel == "not_detected"));
        foreach (var sample in samples)
        {
            var (text, sentences) = PrepareInput(sample.Input.Sentences);
            _ = GetCoverage(text, sample.OverallLabel, sentences, sample.Output.Findings);
        }
    }

    [LiveDatasetFact]
    [Trait("Category", "AI-Evaluation")]
    public async Task EvaluateDataset()
    {
        using var client = new HttpClient
        {
            BaseAddress = new Uri(Environment.GetEnvironmentVariable("JOBSHIELD_API_URL")
                ?? "http://127.0.0.1:5000/"),
            Timeout = TimeSpan.FromSeconds(150)
        };

        var rows = new List<SampleResult>();
        foreach (var sample in ReadSamples())
        {
            var (text, original) = PrepareInput(sample.Input.Sentences);
            var expected = GetCoverage(text, sample.OverallLabel, original, sample.Output.Findings);
            var row = new SampleResult(sample.SampleId, text, sample.OverallLabel, Describe(text, expected));
            try
            {
                using var response = await client.PostAsJsonAsync("/api/analyze", new { text });
                row.HttpStatus = (int)response.StatusCode;
                if (!response.IsSuccessStatusCode)
                {
                    row.Error = $"HTTP {row.HttpStatus}: {await response.Content.ReadAsStringAsync()}";
                }
                else
                {
                    var prediction = await response.Content.ReadFromJsonAsync<Prediction>(Json)
                        ?? throw new InvalidDataException("Empty prediction.");
                    var actual = GetCoverage(text, prediction.Label, prediction.Sentences, prediction.Findings);
                    row.ActualLabel = prediction.Label;
                    row.ActualEvidence = Describe(text, actual);
                    row.MissingEvidence = Difference(text, expected, actual);
                    row.ExtraEvidence = Difference(text, actual, expected);
                    row.LabelCorrect = prediction.Label == sample.OverallLabel;
                    row.CodesCorrect = expected.Keys.ToHashSet().SetEquals(actual.Keys);
                    row.Exact = row.LabelCorrect == true && row.MissingEvidence.Count == 0 && row.ExtraEvidence.Count == 0;
                }
            }
            catch (Exception ex) when (ex is HttpRequestException or OperationCanceledException
                or JsonException or InvalidDataException or IOException)
            {
                row.Error = ex.Message;
            }

            rows.Add(row);
            output.WriteLine($"{row.SampleId}: {row.Error ?? $"{row.ActualLabel}, exact={row.Exact}"}");
        }

        var reportDirectory = GetReportDirectory();
        Directory.CreateDirectory(reportDirectory);
        var reportPath = Path.Combine(reportDirectory, $"evaluation-{DateTime.UtcNow:yyyyMMdd-HHmmss}-{Guid.NewGuid():N}.json");
        var completed = rows.Where(r => r.Error is null).ToList();
        var report = new
        {
            snapshotSha256 = SnapshotHash,
            completedUtc = DateTimeOffset.UtcNow,
            total = rows.Count,
            processed = completed.Count,
            errors = rows.Count - completed.Count,
            correctLabels = completed.Count(r => r.LabelCorrect == true),
            correctCodes = completed.Count(r => r.CodesCorrect == true),
            falseAlarms = completed.Count(r => r.ExpectedLabel == "not_detected" && r.ActualLabel == "suspicious"),
            misses = completed.Count(r => r.ExpectedLabel == "suspicious" && r.ActualLabel == "not_detected"),
            exact = completed.Count(r => r.Exact == true),
            samples = rows
        };
        await File.WriteAllTextAsync(reportPath, JsonSerializer.Serialize(report, Json));
        output.WriteLine($"Report: {reportPath}");
        Assert.True(report.errors == 0, $"{report.errors} processing errors. Report: {reportPath}");
    }

    [Fact]
    public void EvidenceCanSpanTwoPredictedSentencesAndExposeExtraText()
    {
        const string text = "Tin.\nCọc trước.";
        Sentence[] original = [new("c1", "Tin.", 0, 4), new("c2", "Cọc trước.", 5, 15)];
        Sentence[] split = [original[0], new("a", "Cọc", 5, 8), new("b", "trước.", 9, 15)];
        var expected = GetCoverage(text, "suspicious", original, [new("G01", ["c2"])]);
        var actual = GetCoverage(text, "suspicious", split, [new("G01", ["a", "b"])]);
        Assert.Empty(Difference(text, expected, actual));
        Assert.Empty(Difference(text, actual, expected));
        var extra = GetCoverage(text, "suspicious", split, [new("G01", ["c1", "a", "b"])]);
        Assert.Equal(new TextSpan(0, 4, "Tin."), Assert.Single(Difference(text, extra, expected)["G01"]));
    }

    [Fact]
    public void UnknownEvidenceAndUncoveredInputAreProcessingErrors()
    {
        Sentence[] valid = [new("c1", "Tin.", 0, 4)];
        Assert.Throws<InvalidDataException>(() => GetCoverage("Tin.", "suspicious", valid, [new("G01", ["missing"])]));
        Assert.Throws<InvalidDataException>(() => GetCoverage("Tin. Cọc.", "not_detected", valid, []));
    }

    private static Sample[] ReadSamples()
    {
        Assert.Equal(SnapshotHash, Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(SnapshotPath))));
        return File.ReadLines(SnapshotPath).Select(line => JsonSerializer.Deserialize<Sample>(line, DatasetJson)
            ?? throw new InvalidDataException("Missing dataset record.")).ToArray();
    }

    private static (string Text, Sentence[] Sentences) PrepareInput(SourceSentence[] source)
    {
        var text = string.Join("\n", source.Select(s => s.Text));
        var sentences = new List<Sentence>(source.Length);
        int start = 0;
        foreach (var s in source)
        {
            sentences.Add(new Sentence(s.Id, s.Text, start, start + s.Text.Length));
            start += s.Text.Length + 1;
        }
        return (text, sentences.ToArray());
    }

    // Positions are UTF-16 offsets, as in the backend and JavaScript string.slice.
    private static Dictionary<string, HashSet<int>> GetCoverage(
        string text, string label, Sentence[] sentences, Finding[] findings)
    {
        if (sentences.Length == 0 || label is not ("not_detected" or "suspicious")
            || (label == "suspicious") != (findings.Length > 0))
            throw new InvalidDataException("Invalid label, sentences or findings.");

        var byId = new Dictionary<string, Sentence>();
        int cursor = 0;
        foreach (var s in sentences)
        {
            if (s is null || string.IsNullOrWhiteSpace(s.Id) || string.IsNullOrWhiteSpace(s.Text)
                || s.Start < cursor || s.End <= s.Start || s.End > text.Length
                || !text.AsSpan(cursor, s.Start - cursor).IsWhiteSpace()
                || text[s.Start..s.End] != s.Text || !byId.TryAdd(s.Id, s))
                throw new InvalidDataException("Invalid sentence ID, offset, text or order.");
            cursor = s.End;
        }
        if (!text.AsSpan(cursor).IsWhiteSpace())
            throw new InvalidDataException("Sentences do not cover the entire input.");

        var coverage = new Dictionary<string, HashSet<int>>();
        foreach (var finding in findings)
        {
            if (finding is null || string.IsNullOrWhiteSpace(finding.Code) || finding.EvidenceSentenceIds.Length == 0)
                throw new InvalidDataException("Finding is missing a code or evidence.");

            if (!coverage.TryGetValue(finding.Code, out var positions))
                coverage.Add(finding.Code, positions = []);
            foreach (var id in finding.EvidenceSentenceIds)
            {
                if (id is null || !byId.TryGetValue(id, out var sentence))
                    throw new InvalidDataException($"Unknown evidence sentence: {id}.");
                for (int i = sentence.Start; i < sentence.End; i++)
                    if (!char.IsWhiteSpace(text[i])) positions.Add(i);
            }
        }
        return coverage;
    }

    private static Dictionary<string, List<TextSpan>> Describe(string text, Dictionary<string, HashSet<int>> coverage)
        => coverage.ToDictionary(entry => entry.Key, entry => ToSpans(text, entry.Value));

    private static Dictionary<string, List<TextSpan>> Difference(
        string text, Dictionary<string, HashSet<int>> left, Dictionary<string, HashSet<int>> right)
    {
        var result = new Dictionary<string, List<TextSpan>>();
        foreach (var (code, positions) in left)
        {
            var spans = ToSpans(text, positions.Except(right.GetValueOrDefault(code) ?? []));
            if (spans.Count > 0) result.Add(code, spans);
        }
        return result;
    }

    private static List<TextSpan> ToSpans(string text, IEnumerable<int> positions)
    {
        var spans = new List<TextSpan>();
        int start = -1, end = -1;
        foreach (var i in positions.Order())
        {
            if (start >= 0 && !text.AsSpan(end, i - end).IsWhiteSpace())
            {
                spans.Add(new(start, end, text[start..end]));
                start = -1;
            }
            if (start < 0) start = i;
            end = i + 1;
        }
        if (start >= 0) spans.Add(new(start, end, text[start..end]));
        return spans;
    }

    private static string GetReportDirectory()
    {
        for (var dir = new DirectoryInfo(AppContext.BaseDirectory); dir?.Parent is not null; dir = dir.Parent)
            if (File.Exists(Path.Combine(dir.FullName, "JobShield.slnx")))
                return Path.Combine(dir.Parent.FullName, "tmp", "ai-evaluation");
        throw new DirectoryNotFoundException("Could not locate JobShield.slnx to write the evaluation report.");
    }

    private sealed record Sample(
        [property: JsonPropertyName("sample_id")] string SampleId,
        SourceInput Input,
        [property: JsonPropertyName("overall_label")] string OverallLabel,
        SourceOutput Output);
    private sealed record SourceInput(SourceSentence[] Sentences);
    private sealed record SourceSentence(string Id, string Text);
    private sealed record SourceOutput(Finding[] Findings);
    private sealed record Finding(string Code, string[] EvidenceSentenceIds);
    private sealed record Sentence(string Id, string Text, int Start, int End);
    private sealed record Prediction(string Label, Finding[] Findings, Sentence[] Sentences);
    private sealed record TextSpan(int Start, int End, string Text);
    private sealed record SampleResult(string SampleId, string Text, string ExpectedLabel,
        Dictionary<string, List<TextSpan>> ExpectedEvidence)
    {
        public int? HttpStatus { get; set; }
        public string? ActualLabel { get; set; }
        public Dictionary<string, List<TextSpan>>? ActualEvidence { get; set; }
        public Dictionary<string, List<TextSpan>>? MissingEvidence { get; set; }
        public Dictionary<string, List<TextSpan>>? ExtraEvidence { get; set; }
        public bool? LabelCorrect { get; set; }
        public bool? CodesCorrect { get; set; }
        public bool? Exact { get; set; }
        public string? Error { get; set; }
    }
}

public sealed class LiveDatasetFactAttribute : FactAttribute
{
    public LiveDatasetFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("JOBSHIELD_RUN_EVAL") != "1")
            Skip = "Set JOBSHIELD_RUN_EVAL=1 to send all 30 samples to the running JobShield API.";
    }
}

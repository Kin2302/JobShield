using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using JobShield.Application;

namespace JobShield.Infrastructure;

public sealed class AiServiceClient(HttpClient httpClient)
{
    public async Task<AnalysisResult?> AnalyzeAsync(
        IReadOnlyList<PreparedSentence> sentences,
        CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();

        if (sentences.Count == 0)
        {
            return null;
        }

        var body = new
        {
            sentences = sentences.Select(s => new
            {
                id = s.Id,
                type = s.Type,
                speaker = s.Speaker,
                text = s.Text
            })
        };

        try
        {
            using var response = await httpClient.PostAsJsonAsync(
                "analyze", body, cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                return null;
            }

            var prediction = await response.Content.ReadFromJsonAsync<PredictionJson>(
                cancellationToken: cancellationToken);

            return ReadResult(prediction, sentences);
        }
        catch (HttpRequestException)
        {
            return null;
        }
        catch (JsonException)
        {
            return null;
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            return null;
        }
    }

    private static AnalysisResult? ReadResult(
        PredictionJson? prediction,
        IReadOnlyList<PreparedSentence> sentences)
    {
        if (prediction?.Label is not ("suspicious" or "not_detected") ||
            prediction.Findings is null)
        {
            return null;
        }

        bool hasFindings = prediction.Findings.Count > 0;
        if ((prediction.Label == "suspicious") != hasFindings)
        {
            return null;
        }

        var sentIds = sentences.Select(s => s.Id).ToHashSet(StringComparer.Ordinal);
        var findings = new List<Finding>(prediction.Findings.Count);

        foreach (var item in prediction.Findings)
        {
            if (item is null ||
                string.IsNullOrWhiteSpace(item.Code) ||
                item.EvidenceSentenceIds is not { Count: > 0 } ids ||
                ids.Any(id => !sentIds.Contains(id)))
            {
                return null;
            }

            findings.Add(new Finding(item.Code, ids.AsReadOnly()));
        }

        return new AnalysisResult(prediction.Label, findings.AsReadOnly());
    }

    private sealed record PredictionJson(
        [property: JsonPropertyName("label")] string? Label,
        [property: JsonPropertyName("findings")] List<FindingJson?>? Findings);

    private sealed record FindingJson(
        [property: JsonPropertyName("code")] string? Code,
        [property: JsonPropertyName("evidence_sentence_ids")] List<string>? EvidenceSentenceIds);
}

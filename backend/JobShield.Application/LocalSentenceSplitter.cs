namespace JobShield.Application;

public static class LocalSentenceSplitter
{
    private static readonly (string Prefix, string Speaker)[] SpeakerPrefixes =
    [
        ("bên tuyển dụng:", "recruiter"),
        ("nhà tuyển dụng:", "recruiter"),
        ("tuyển dụng:", "recruiter"),
        ("quản lý:", "recruiter"),
        ("admin:", "recruiter"),
        ("ntd:", "recruiter"),
        ("hr:", "recruiter"),
        ("ứng viên:", "applicant"),
        ("uv:", "applicant"),
    ];

    private static readonly HashSet<string> Abbreviations = new(StringComparer.OrdinalIgnoreCase)
    {
        "tp", "sđt", "sdt", "p", "q", "tx", "tt", "tnhh", "cp", "mr", "ms", "mrs", "dr", "th", "ts", "ths"
    };

    public static IReadOnlyList<GroqSentence> Split(string originalText)
    {
        if (string.IsNullOrWhiteSpace(originalText))
        {
            return [];
        }

        var result = new List<GroqSentence>();
        var lines = originalText.Split(["\r\n", "\n"], StringSplitOptions.None);

        foreach (var rawLine in lines)
        {
            var trimmedLine = rawLine.Trim();
            if (trimmedLine.Length == 0)
            {
                continue;
            }

            var (type, speaker) = DetectTurnMetadata(trimmedLine);
            foreach (var sentence in SplitLineIntoSentences(trimmedLine))
            {
                result.Add(new GroqSentence(sentence, type, speaker));
            }
        }

        return result.AsReadOnly();
    }

    private static (string Type, string Speaker) DetectTurnMetadata(string line)
    {
        foreach (var (prefix, speaker) in SpeakerPrefixes)
        {
            if (line.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
            {
                return ("message", speaker);
            }
        }
        return ("unknown", "unknown");
    }

    private static IEnumerable<string> SplitLineIntoSentences(string line)
    {
        var start = 0;
        var i = 0;

        while (i < line.Length)
        {
            var ch = line[i];
            if (ch is '.' or '!' or '?')
            {
                var punctEnd = i + 1;
                while (punctEnd < line.Length && line[punctEnd] is '.' or '!' or '?')
                {
                    punctEnd++;
                }

                // Chỉ cắt khi ngay sau dấu kết câu là khoảng trắng và không phải viết tắt.
                if (punctEnd < line.Length &&
                    char.IsWhiteSpace(line[punctEnd]) &&
                    !(ch == '.' && punctEnd == i + 1 && IsAbbreviationBefore(line, i)))
                {
                    var segment = line[start..punctEnd].Trim();
                    if (segment.Length > 0)
                    {
                        yield return segment;
                    }

                    start = punctEnd;
                    while (start < line.Length && char.IsWhiteSpace(line[start]))
                    {
                        start++;
                    }

                    i = start;
                    continue;
                }

                i = punctEnd;
                continue;
            }

            i++;
        }

        if (start < line.Length)
        {
            var tail = line[start..].Trim();
            if (tail.Length > 0)
            {
                yield return tail;
            }
        }
    }

    private static bool IsAbbreviationBefore(string line, int dotIndex)
    {
        var tokenStart = dotIndex - 1;
        while (tokenStart >= 0 && (char.IsLetterOrDigit(line[tokenStart]) || line[tokenStart] == '_'))
        {
            tokenStart--;
        }
        var token = line[(tokenStart + 1)..dotIndex];
        return token.Length > 0 && Abbreviations.Contains(token);
    }
}

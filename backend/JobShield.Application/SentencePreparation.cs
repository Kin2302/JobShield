namespace JobShield.Application;

public sealed record GroqSentence(string Text, string Type, string Speaker);

public sealed record PreparedSentence(
    string Id,
    string Text,
    string Type,
    string Speaker,
    int Start,
    int End);

public static class SentencePreparation
{
    public static IReadOnlyList<PreparedSentence>? Prepare(
        string originalText,
        IReadOnlyList<GroqSentence> sentences)
    {
        if (sentences.Count == 0)
        {
            return null;
        }

        var result = new List<PreparedSentence>(sentences.Count);
        var position = 0;

        foreach (var sentence in sentences)
        {
            if (string.IsNullOrWhiteSpace(sentence.Text))
            {
                return null;
            }

            var sentenceText = sentence.Text.AsSpan().Trim();

            while (position < originalText.Length &&
                   char.IsWhiteSpace(originalText[position]))
            {
                position++;
            }

            if (!originalText.AsSpan(position)
                    .StartsWith(sentenceText, StringComparison.Ordinal))
            {
                return null;
            }

            var start = position;
            position += sentenceText.Length;

            result.Add(new PreparedSentence(
                Id: $"c{result.Count + 1}",
                Text: originalText[start..position],
                Type: sentence.Type,
                Speaker: sentence.Speaker,
                Start: start,
                End: position));
        }

        if (!originalText.AsSpan(position).IsWhiteSpace())
        {
            return null;
        }

        return result.AsReadOnly();
    }
}

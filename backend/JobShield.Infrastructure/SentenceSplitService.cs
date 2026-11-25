using JobShield.Application;

namespace JobShield.Infrastructure;

public interface ISentenceSplitService
{
    Task<(IReadOnlyList<PreparedSentence>? Sentences, string SplitSource)> SplitAsync(
        string originalText,
        CancellationToken cancellationToken);
}

public sealed class SentenceSplitService(IGroqSentenceSplitter? groqClient = null) : ISentenceSplitService
{
    public async Task<(IReadOnlyList<PreparedSentence>? Sentences, string SplitSource)> SplitAsync(
        string originalText,
        CancellationToken cancellationToken)
    {
        if (groqClient is not null)
        {
            var maskedText = PiiRedactor.RedactSameLength(originalText);
            var groqSplit = await groqClient.SplitAsync(maskedText, cancellationToken);
            if (groqSplit is not null)
            {
                var preparedMasked = SentencePreparation.Prepare(maskedText, groqSplit);
                if (preparedMasked is not null)
                {
                    var restored = preparedMasked
                        .Select(s => s with { Text = originalText[s.Start..s.End] })
                        .ToList()
                        .AsReadOnly();
                    return (restored, "groq");
                }
            }
        }

        var localSplit = LocalSentenceSplitter.Split(originalText);
        var localPrepared = SentencePreparation.Prepare(originalText, localSplit);
        return (localPrepared, "local");
    }
}

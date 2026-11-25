using System.Text.Json;
using System.Text.Json.Serialization;
using JobShield.Application;

namespace JobShield.Infrastructure;

public static class GroqSentenceParser
{
    public static IReadOnlyList<GroqSentence>? Parse(string? json)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return null;
        }

        GroqResponse? response;

        try
        {
            response = JsonSerializer.Deserialize<GroqResponse>(json);
        }
        catch (JsonException)
        {
            return null;
        }

        if (response?.Sentences is not { Count: > 0 } sentences)
        {
            return null;
        }

        var result = new List<GroqSentence>(sentences.Count);

        foreach (var sentence in sentences)
        {
            if (sentence is null ||
                string.IsNullOrWhiteSpace(sentence.Text) ||
                sentence.Type is not ("posting" or "message" or "unknown") ||
                sentence.Speaker is not ("applicant" or "recruiter" or "unknown"))
            {
                return null;
            }

            result.Add(new GroqSentence(
                sentence.Text,
                sentence.Type,
                sentence.Speaker));
        }

        return result.AsReadOnly();
    }

    private sealed record GroqResponse(
        [property: JsonPropertyName("sentences")] List<SentenceJson?>? Sentences);

    private sealed record SentenceJson(
        [property: JsonPropertyName("text")] string? Text,
        [property: JsonPropertyName("type")] string? Type,
        [property: JsonPropertyName("speaker")] string? Speaker);
}

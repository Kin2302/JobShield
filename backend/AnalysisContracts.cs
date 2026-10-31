using System.Text.Json.Serialization;

public sealed record AnalyzeRequest(string? Text);

public sealed record AnalyzeResponse(
    [property: JsonPropertyName("baseline_version")] string? BaselineVersion,
    string? Message,
    IReadOnlyList<Signal?>? Signals);

public sealed record Signal(string? Code, string? Name, string? Evidence);

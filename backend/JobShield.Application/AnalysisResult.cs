namespace JobShield.Application;

public sealed record AnalysisResult(
    string Label,
    IReadOnlyList<Finding> Findings);

public sealed record Finding(
    string Code,
    IReadOnlyList<string> EvidenceSentenceIds);

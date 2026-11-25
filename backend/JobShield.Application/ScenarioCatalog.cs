namespace JobShield.Application;

public sealed record ScenarioCatalog(
    string Version,
    string CodebookVersion,
    IReadOnlyDictionary<string, string> Explanations,
    IReadOnlyList<ScenarioCase> Cases,
    IReadOnlyList<ScenarioRule> PossibleNextSteps)
{
    public ScenarioSelection Select(IReadOnlyList<Finding> findings)
    {
        var codes = findings.Select(finding => finding.Code).ToHashSet(StringComparer.Ordinal);
        var explanations = Explanations.Where(pair => codes.Contains(pair.Key)).ToDictionary();
        var cases = new List<ScenarioCase>();
        foreach (var item in Cases)
        {
            var reasons = item.MatchReasons.Where(pair => codes.Contains(pair.Key)).ToDictionary();
            if (reasons.Count > 0)
            {
                cases.Add(item with { MatchReasons = reasons });
            }
        }

        var steps = PossibleNextSteps
            .Where(rule => codes.Overlaps(rule.ShowWhenAny) && !codes.Overlaps(rule.HideWhenAny))
            .Select(rule => new ScenarioStep(rule.Id, rule.Text, rule.SourceUrl))
            .ToArray();
        return new ScenarioSelection(explanations, cases, steps);
    }
}

public sealed record ScenarioCase(string Id, string Title,
    IReadOnlyDictionary<string, string> MatchReasons, string Summary, string SourceUrl);

public sealed record ScenarioRule(string Id, IReadOnlyList<string> ShowWhenAny,
    IReadOnlyList<string> HideWhenAny, string Text, string SourceUrl);

public sealed record ScenarioStep(string Id, string Text, string SourceUrl);

public sealed record ScenarioSelection(IReadOnlyDictionary<string, string> Explanations,
    IReadOnlyList<ScenarioCase> Cases, IReadOnlyList<ScenarioStep> PossibleNextSteps);

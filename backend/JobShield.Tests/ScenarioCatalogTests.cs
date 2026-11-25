using JobShield.Application;
using JobShield.Infrastructure;
using Xunit;

namespace JobShield.Tests;

public sealed class ScenarioCatalogTests
{
    private static readonly ScenarioCatalog Catalog = ScenarioCatalogLoader.Load();
    private static readonly string[] AllV3Codes =
        ["G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08"];

    [Fact]
    public void CatalogUsesV3CodebookAndCoversAllEightCoreGroups()
    {
        Assert.Equal("v3", Catalog.CodebookVersion);
        Assert.Equal(AllV3Codes, Catalog.Explanations.Keys.Order());
        Assert.All(AllV3Codes, code =>
        {
            var selection = Catalog.Select(Findings(code));
            Assert.NotEmpty(selection.Cases);
            Assert.NotEmpty(selection.PossibleNextSteps);
            Assert.All(selection.Cases, item => Assert.StartsWith("https://", item.SourceUrl));
            Assert.All(selection.PossibleNextSteps, step => Assert.StartsWith("https://", step.SourceUrl));
        });
    }

    [Fact]
    public void SelectReturnsApprovedG08AndG02Examples()
    {
        var selection = Catalog.Select(Findings("G08", "G02"));

        Assert.Equal(["G02", "G08"], selection.Explanations.Keys.Order());
        Assert.Contains(selection.Cases, item => item.Id == "dak-nong-2022"
            && item.MatchReasons.Keys.Order().SequenceEqual(["G02", "G08"]));
        Assert.Contains(selection.Cases, item => item.Id == "thach-ha-2026"
            && item.MatchReasons.ContainsKey("G02"));
        Assert.Equal("tang-tien-ung-va-nop-them", Assert.Single(selection.PossibleNextSteps).Id);
    }

    [Fact]
    public void EarlyTaskLureWithoutAdvanceReturnsEarlySteps()
    {
        var selection = Catalog.Select(Findings("G08"));

        Assert.Equal(["tra-cong-nhiem-vu-dau", "ung-tien-cho-don"],
            selection.PossibleNextSteps.Select(step => step.Id));
    }

    [Fact]
    public void SelectIgnoresUnknownCodes()
    {
        var selection = Catalog.Select(Findings("UNKNOWN"));

        Assert.Empty(selection.Explanations);
        Assert.Empty(selection.Cases);
        Assert.Empty(selection.PossibleNextSteps);
    }

    [Fact]
    public void SelectReturnsNothingForNoFindings()
    {
        var selection = Catalog.Select([]);

        Assert.Empty(selection.Explanations);
        Assert.Empty(selection.Cases);
        Assert.Empty(selection.PossibleNextSteps);
    }

    [Fact]
    public void SelectDeduplicatesRepeatedFindingCodes()
    {
        var selection = Catalog.Select(Findings("G02", "G02"));

        Assert.Single(selection.Explanations.Keys);
        Assert.Equal(["G02"], selection.Explanations.Keys);
        Assert.Equal(selection.Cases.Select(item => item.Id).Distinct(), selection.Cases.Select(item => item.Id));
        Assert.Equal(selection.PossibleNextSteps.Select(item => item.Id).Distinct(),
            selection.PossibleNextSteps.Select(item => item.Id));
    }

    private static IReadOnlyList<Finding> Findings(params string[] codes) =>
        codes.Select(code => new Finding(code, [])).ToArray();
}

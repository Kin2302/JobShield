using System.Text.Json;
using JobShield.Application;

namespace JobShield.Infrastructure;

public static class ScenarioCatalogLoader
{
    public static ScenarioCatalog Load()
    {
        using var stream = typeof(ScenarioCatalogLoader).Assembly.GetManifestResourceStream(
            typeof(ScenarioCatalogLoader), "RecruitmentScenarios.json")
            ?? throw new InvalidDataException("Không tìm thấy kho kịch bản JobShield.");
        var options = new JsonSerializerOptions(JsonSerializerDefaults.Web)
        {
            RespectRequiredConstructorParameters = true,
            RespectNullableAnnotations = true
        };
        return JsonSerializer.Deserialize<ScenarioCatalog>(stream, options)
            ?? throw new InvalidDataException("Kho kịch bản JobShield trống.");
    }
}

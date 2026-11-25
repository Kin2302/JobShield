using JobShield.Application;
using JobShield.Infrastructure;

namespace JobShield.Api;

public sealed record AnalyzeRequest(string? Text);

public static class AnalyzeEndpoint
{
    public const int MaxTextLength = 10_000;

    public static async Task<IResult> HandleAsync(
        AnalyzeRequest request,
        ISentenceSplitService splitService,
        AiServiceClient aiClient,
        ScenarioCatalog catalog,
        CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(request.Text))
        {
            return Results.Problem(
                title: "Vui lòng nhập nội dung cần phân tích.",
                statusCode: StatusCodes.Status400BadRequest);
        }

        if (request.Text.Length > MaxTextLength)
        {
            return Results.Problem(
                title: "Nội dung vượt quá giới hạn 10.000 ký tự.",
                statusCode: StatusCodes.Status400BadRequest);
        }

        if (request.Text.Contains('\0'))
        {
            return Results.Problem(
                title: "Nội dung chứa ký tự không hợp lệ.",
                statusCode: StatusCodes.Status400BadRequest);
        }

        var (sentences, splitSource) = await splitService.SplitAsync(request.Text, cancellationToken);
        if (sentences is null)
        {
            return AnalysisFailed();
        }

        var result = await aiClient.AnalyzeAsync(sentences, cancellationToken);
        if (result is null)
        {
            return AnalysisFailed();
        }

        var selection = catalog.Select(result.Findings);
        return Results.Ok(new
        {
            result.Label,
            result.Findings,
            Sentences = sentences.Select(s => new { s.Id, s.Text, s.Start, s.End }),
            SplitSource = splitSource,
            CatalogVersion = catalog.Version,
            selection.Explanations,
            selection.Cases,
            selection.PossibleNextSteps
        });
    }

    private static IResult AnalysisFailed() =>
        Results.Problem(
            title: "Chưa thể phân tích, vui lòng thử lại.",
            statusCode: StatusCodes.Status502BadGateway);
}

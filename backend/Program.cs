using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddHttpClient("ai", client =>
{
    client.BaseAddress = new Uri(builder.Configuration["AiService:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(10);
});
var app = builder.Build();

app.MapPost("/api/analyze", async (
    AnalyzeRequest request,
    IHttpClientFactory clients,
    CancellationToken cancellationToken) =>
{
    if (string.IsNullOrWhiteSpace(request.Text))
    {
        return Results.Problem(
            statusCode: 400, title: "Nội dung không được để trống.");
    }

    try
    {
        using var response = await clients.CreateClient("ai").PostAsJsonAsync(
            "analyze", request, cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            return Results.Problem(statusCode: 502,
                title: "Dịch vụ phân tích trả về lỗi. Vui lòng thử lại.");
        }

        var result = await response.Content.ReadFromJsonAsync<AnalyzeResponse>(
            cancellationToken);

        if (result is null || string.IsNullOrWhiteSpace(result.BaselineVersion)
            || string.IsNullOrWhiteSpace(result.Message) || result.Signals is null
            || result.Signals.Any(signal => signal is null
                || string.IsNullOrWhiteSpace(signal.Code)
                || string.IsNullOrWhiteSpace(signal.Name)
                || string.IsNullOrWhiteSpace(signal.Evidence)
                || !request.Text.Contains(signal.Evidence, StringComparison.Ordinal)))
        {
            return Results.Problem(statusCode: 502,
                title: "Dịch vụ phân tích trả dữ liệu không hợp lệ.");
        }

        return Results.Ok(result);
    }
    catch (HttpRequestException)
    {
        return Results.Problem(statusCode: 503,
            title: "Không kết nối được dịch vụ phân tích. Vui lòng thử lại.");
    }
    catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
    {
        return Results.Problem(statusCode: 504,
            title: "Dịch vụ phân tích phản hồi quá thời gian chờ.");
    }
    catch (JsonException)
    {
        return Results.Problem(statusCode: 502,
            title: "Dịch vụ phân tích trả dữ liệu không hợp lệ.");
    }
});

app.Run();

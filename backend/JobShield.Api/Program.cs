using System.Threading.RateLimiting;
using JobShield.Api;
using JobShield.Infrastructure;
using Microsoft.AspNetCore.HttpOverrides;

var builder = WebApplication.CreateBuilder(args);

builder.WebHost.ConfigureKestrel(options =>
{
    options.Limits.MaxRequestBodySize = 32 * 1024;
});

var aiServiceUrl = builder.Configuration["AiService:BaseUrl"];
if (!Uri.TryCreate(aiServiceUrl, UriKind.Absolute, out var aiServiceUri) ||
    aiServiceUri.Scheme is not ("http" or "https"))
{
    throw new InvalidOperationException("AiService:BaseUrl phải là địa chỉ HTTP hợp lệ.");
}

var apiKey = builder.Configuration["Groq:ApiKey"];
var model = builder.Configuration["Groq:Model"];
GroqSentenceClient? groqClient = string.IsNullOrWhiteSpace(apiKey)
    ? null
    : string.IsNullOrWhiteSpace(model)
        ? new GroqSentenceClient(apiKey)
        : new GroqSentenceClient(apiKey, model);

var permitLimit = Math.Max(1, builder.Configuration.GetValue<int?>("RateLimiting:PermitLimit") ?? 20);
var windowSeconds = Math.Max(1, builder.Configuration.GetValue<int?>("RateLimiting:WindowSeconds") ?? 60);

builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownIPNetworks.Clear();
    options.KnownProxies.Clear();
});

builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.OnRejected = async (context, token) =>
    {
        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
        await Results.Problem(
            title: "Quá nhiều yêu cầu trong thời gian ngắn. Vui lòng thử lại sau.",
            statusCode: StatusCodes.Status429TooManyRequests).ExecuteAsync(context.HttpContext);
    };
    options.AddPolicy("analyze", httpContext =>
    {
        var key = httpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown";
        return RateLimitPartition.GetFixedWindowLimiter(
            key,
            _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = permitLimit,
                Window = TimeSpan.FromSeconds(windowSeconds),
                QueueLimit = 0
            });
    });
});

builder.Services.AddSingleton(ScenarioCatalogLoader.Load());
builder.Services.AddSingleton<ISentenceSplitService>(_ => new SentenceSplitService(groqClient));

builder.Services.AddHttpClient<AiServiceClient>(client =>
{
    client.BaseAddress = aiServiceUri;
    client.Timeout = TimeSpan.FromSeconds(60);
});

var app = builder.Build();
app.UseForwardedHeaders();
app.Use(async (context, next) =>
{
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["X-Frame-Options"] = "DENY";
    context.Response.Headers["Referrer-Policy"] = "no-referrer";
    context.Response.Headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()";
    context.Response.Headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'";
    await next();
});
app.UseRateLimiter();

if (groqClient is null)
{
    app.Logger.LogInformation("Không có Groq:ApiKey; sử dụng bộ tách câu dự phòng cục bộ.");
}

app.MapGet("/health", () => Results.Ok(new { status = "ok", service = "jobshield-api" }));
app.MapPost("/api/analyze", AnalyzeEndpoint.HandleAsync).RequireRateLimiting("analyze");
app.Run();

public partial class Program;

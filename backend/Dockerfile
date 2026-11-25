FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY JobShield.slnx ./
COPY JobShield.Api/JobShield.Api.csproj JobShield.Api/
COPY JobShield.Application/JobShield.Application.csproj JobShield.Application/
COPY JobShield.Infrastructure/JobShield.Infrastructure.csproj JobShield.Infrastructure/
COPY JobShield.Tests/JobShield.Tests.csproj JobShield.Tests/
RUN dotnet restore JobShield.Api/JobShield.Api.csproj

COPY JobShield.Api/ JobShield.Api/
COPY JobShield.Application/ JobShield.Application/
COPY JobShield.Infrastructure/ JobShield.Infrastructure/
RUN dotnet publish JobShield.Api/JobShield.Api.csproj -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app

COPY --from=build /app/publish ./

USER $APP_UID
ENV ASPNETCORE_URLS=http://+:5000
EXPOSE 5000

ENTRYPOINT ["dotnet", "JobShield.Api.dll"]

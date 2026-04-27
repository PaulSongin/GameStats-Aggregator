# Используем новенький SDK 10.0 для сборки
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Копируем и восстанавливаем зависимости (ВОТ ТУТ БЫЛ ПРОПУЩЕН ПРОБЕЛ)
COPY ["CoreBackend.csproj", "./"]
RUN dotnet restore "CoreBackend.csproj"

# Копируем остальной код и собираем
COPY . .
RUN dotnet publish "CoreBackend.csproj" -c Release -o /app/publish

# Используем рантайм 10.0 для запуска
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "CoreBackend.dll"]
namespace CoreBackend.Models;

public record ErrorResponse(
    string Error,
    string Message,
    int StatusCode
);

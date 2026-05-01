use axum::{Json, http::StatusCode};
use serde_json::{Value, json};

pub type ApiErrorResponse = (StatusCode, Json<Value>);
pub type AppResult<T> = Result<T, ApiErrorResponse>;

fn error_response(status: StatusCode, message: impl Into<String>) -> ApiErrorResponse {
    (status, Json(json!({ "error": message.into() })))
}

pub fn bad_request(message: impl Into<String>) -> ApiErrorResponse {
    error_response(StatusCode::BAD_REQUEST, message)
}

pub fn unauthorized(message: impl Into<String>) -> ApiErrorResponse {
    error_response(StatusCode::UNAUTHORIZED, message)
}

pub fn forbidden(message: impl Into<String>) -> ApiErrorResponse {
    error_response(StatusCode::FORBIDDEN, message)
}

pub fn not_found(message: impl Into<String>) -> ApiErrorResponse {
    error_response(StatusCode::NOT_FOUND, message)
}

pub fn conflict(message: impl Into<String>) -> ApiErrorResponse {
    error_response(StatusCode::CONFLICT, message)
}

pub fn service_unavailable(message: impl Into<String>) -> ApiErrorResponse {
    error_response(StatusCode::SERVICE_UNAVAILABLE, message)
}

pub fn not_implemented(message: impl Into<String>) -> ApiErrorResponse {
    error_response(StatusCode::NOT_IMPLEMENTED, message)
}

pub fn internal_error(message: impl Into<String>) -> ApiErrorResponse {
    tracing::error!("Internal server error: {}", message.into());
    error_response(StatusCode::INTERNAL_SERVER_ERROR, "internal_error")
}

pub fn internal_route_error(
    route_context: &'static str,
    public_code: &'static str,
    error: impl std::fmt::Display,
) -> ApiErrorResponse {
    tracing::error!("{route_context}: {error}");
    error_response(StatusCode::INTERNAL_SERVER_ERROR, public_code)
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::Json;

    #[test]
    fn bad_request_returns_400() {
        let (status, Json(body)) = bad_request("test error");
        assert_eq!(status, StatusCode::BAD_REQUEST);
        assert_eq!(body["error"], "test error");
    }

    #[test]
    fn unauthorized_returns_401() {
        let (status, Json(body)) = unauthorized("unauthorized");
        assert_eq!(status, StatusCode::UNAUTHORIZED);
        assert_eq!(body["error"], "unauthorized");
    }

    #[test]
    fn forbidden_returns_403() {
        let (status, Json(body)) = forbidden("forbidden");
        assert_eq!(status, StatusCode::FORBIDDEN);
        assert_eq!(body["error"], "forbidden");
    }

    #[test]
    fn not_found_returns_404() {
        let (status, Json(body)) = not_found("not found");
        assert_eq!(status, StatusCode::NOT_FOUND);
        assert_eq!(body["error"], "not found");
    }

    #[test]
    fn conflict_returns_409() {
        let (status, Json(body)) = conflict("conflict");
        assert_eq!(status, StatusCode::CONFLICT);
        assert_eq!(body["error"], "conflict");
    }

    #[test]
    fn internal_error_returns_500() {
        let (status, Json(body)) = internal_error("something broke");
        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
        assert_eq!(body["error"], "internal_error");
    }

    #[test]
    fn internal_route_error_preserves_public_code() {
        let (status, Json(body)) =
            internal_route_error("Test route error", "test_internal_error", "boom");
        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
        assert_eq!(body["error"], "test_internal_error");
    }

    #[test]
    fn service_unavailable_returns_503() {
        let (status, Json(body)) = service_unavailable("service unavailable");
        assert_eq!(status, StatusCode::SERVICE_UNAVAILABLE);
        assert_eq!(body["error"], "service unavailable");
    }

    #[test]
    fn not_implemented_returns_501() {
        let (status, Json(body)) = not_implemented("not implemented");
        assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
        assert_eq!(body["error"], "not implemented");
    }
}

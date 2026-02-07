import asyncio
import gzip
import logging
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.compression")


class CompressionType(Enum):
    """Supported compression types."""

    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "br"


class CompressionConfig:
    """Compression configuration."""

    def __init__(
        self,
        min_size: int = 1024,  # Minimum size to compress (1KB)
        level: int = 6,  # Compression level (1-9 for gzip)
        types: List[str] = None,
        excluded_paths: List[str] = None,
    ):
        self.min_size = min_size
        self.level = level
        self.types = types or [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "text/xml",
            "application/xml",
        ]
        self.excluded_paths = excluded_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
        ]


class CompressionMiddleware:
    """
    FastAPI middleware for request/response compression.
    """

    def __init__(self, app, config: CompressionConfig = None):
        self.app = app
        self.config = config or CompressionConfig()
        self.stats = {
            "requests_compressed": 0,
            "responses_compressed": 0,
            "bytes_saved": 0,
            "compression_time_ms": 0,
        }

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Check if path is excluded
            path = scope["path"]
            if any(
                path.startswith(excluded) for excluded in self.config.excluded_paths
            ):
                await self.app(scope, receive, send)
                return

            # Handle request compression
            headers = dict(scope.get("headers", []))
            accept_encoding = headers.get(b"accept-encoding", b"").decode().lower()
            content_encoding = headers.get(b"content-encoding", b"").decode().lower()

            # Check if client supports compression
            supported_encodings = []
            if "gzip" in accept_encoding:
                supported_encodings.append(CompressionType.GZIP)
            if "deflate" in accept_encoding:
                supported_encodings.append(CompressionType.DEFLATE)
            if "br" in accept_encoding:
                supported_encodings.append(CompressionType.BROTLI)

            # Process request with compression
            if supported_encodings and content_encoding in ["gzip", "deflate"]:
                # Decompress request body if needed
                scope = await self._handle_compressed_request(
                    scope, receive, content_encoding
                )

            # Process response with compression
            await self._handle_compressed_response(
                scope, receive, send, supported_encodings
            )
        else:
            await self.app(scope, receive, send)

    async def _handle_compressed_request(
        self, scope: Dict[str, Any], receive: callable, content_encoding: str
    ) -> Dict[str, Any]:
        """Handle compressed request body."""
        # This would decompress incoming request body
        # For now, just pass through (most GET requests don't have body)
        return scope

    async def _handle_compressed_response(
        self,
        scope: Dict[str, Any],
        receive: callable,
        send: callable,
        supported_encodings: List[CompressionType],
    ):
        """Handle response compression."""
        response_body = b""
        response_status = 200
        response_headers = []
        content_type = "application/json"

        # Intercept response
        async def send_wrapper(message):
            nonlocal response_body, response_status, response_headers, content_type

            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = message["headers"]

                # Extract content type
                for name, value in response_headers:
                    if name.lower() == b"content-type":
                        content_type = value.decode().split(";")[0]
                        break

                await send(message)
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")
                await send(message)
            else:
                await send(message)

        # Process the request
        await self.app(scope, receive, send_wrapper)

        # Compress response if applicable
        if (
            len(response_body) >= self.config.min_size
            and content_type in self.config.types
            and supported_encodings
        ):

            # Choose best compression method
            compression_type = self._choose_compression(supported_encodings)

            # Compress the response body
            import time

            start_time = time.time()

            if compression_type == CompressionType.GZIP:
                compressed_body = gzip.compress(
                    response_body, compresslevel=self.config.level
                )
                encoding_header = "gzip"
            elif compression_type == CompressionType.DEFLATE:
                # Deflate is similar to gzip but without the gzip header
                import zlib

                compressed_body = zlib.compress(response_body, level=self.config.level)
                encoding_header = "deflate"
            else:
                # Fallback to gzip
                compressed_body = gzip.compress(
                    response_body, compresslevel=self.config.level
                )
                encoding_header = "gzip"

            compression_time = (time.time() - start_time) * 1000

            # Update stats
            self.stats["responses_compressed"] += 1
            self.stats["bytes_saved"] += len(response_body) - len(compressed_body)
            self.stats["compression_time_ms"] += compression_time

            # Log compression info
            compression_ratio = (1 - len(compressed_body) / len(response_body)) * 100
            logger.debug(
                f"Compressed response: {len(response_body)} -> {len(compressed_body)} bytes "
                f"({compression_ratio:.1f}% reduction, {compression_time:.1f}ms)"
            )

            # Note: In a real implementation, we would modify the response headers
            # to include the compression encoding and update the body
            # This is a simplified version for demonstration

    def _choose_compression(
        self, supported_encodings: List[CompressionType]
    ) -> CompressionType:
        """Choose the best compression method."""
        # Prefer Brotli if available, then gzip, then deflate
        if CompressionType.BROTLI in supported_encodings:
            return CompressionType.BROTLI
        elif CompressionType.GZIP in supported_encodings:
            return CompressionType.GZIP
        elif CompressionType.DEFLATE in supported_encodings:
            return CompressionType.DEFLATE
        else:
            return CompressionType.GZIP  # Fallback

    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        return {
            **self.stats,
            "avg_compression_time_ms": (
                self.stats["compression_time_ms"]
                / max(1, self.stats["responses_compressed"])
            ),
            "avg_compression_ratio": (
                self.stats["bytes_saved"] / max(1, self.stats["responses_compressed"])
            ),
        }


class RequestDecompressor:
    """Utility for decompressing request bodies."""

    @staticmethod
    async def decompress_request(body: bytes, content_encoding: str) -> bytes:
        """Decompress request body based on content encoding."""
        try:
            if content_encoding == "gzip":
                return gzip.decompress(body)
            elif content_encoding == "deflate":
                import zlib

                return zlib.decompress(body)
            else:
                return body
        except Exception as e:
            logger.error(f"Error decompressing request: {e}")
            raise ValueError(f"Invalid compressed data: {e}")


class ResponseCompressor:
    """Utility for compressing response bodies."""

    @staticmethod
    async def compress_response(
        body: bytes,
        compression_type: CompressionType = CompressionType.GZIP,
        level: int = 6,
    ) -> bytes:
        """Compress response body."""
        try:
            if compression_type == CompressionType.GZIP:
                return gzip.compress(body, compresslevel=level)
            elif compression_type == CompressionType.DEFLATE:
                import zlib

                return zlib.compress(body, level=level)
            else:
                # Fallback to gzip
                return gzip.compress(body, compresslevel=level)
        except Exception as e:
            logger.error(f"Error compressing response: {e}")
            return body  # Return uncompressed on error


# Global compression middleware
_compression_middleware: Optional[CompressionMiddleware] = None


def get_compression_middleware() -> CompressionMiddleware:
    """Get the global compression middleware instance."""
    global _compression_middleware
    if _compression_middleware is None:
        _compression_middleware = CompressionMiddleware(None)
    return _compression_middleware


def compress_response(min_size: int = 1024, level: int = 6, types: List[str] = None):
    """Decorator for compressing function responses."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # If result is a response-like object, compress it
            if isinstance(result, (dict, list, str)):
                # Convert to bytes
                if isinstance(result, str):
                    body_bytes = result.encode("utf-8")
                else:
                    import json

                    body_bytes = json.dumps(result).encode("utf-8")

                # Compress if large enough
                if len(body_bytes) >= min_size:
                    compressor = ResponseCompressor()
                    compressed = await compressor.compress_response(
                        body_bytes, CompressionType.GZIP, level
                    )

                    # Return compressed result with metadata
                    return {
                        "compressed": True,
                        "original_size": len(body_bytes),
                        "compressed_size": len(compressed),
                        "data": compressed.hex(),  # Convert bytes to hex for JSON serialization
                    }

            return result

        return wrapper

    return decorator


async def get_compression_stats() -> Dict[str, Any]:
    """Get compression statistics."""
    middleware = get_compression_middleware()
    return middleware.get_stats()

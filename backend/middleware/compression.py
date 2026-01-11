"""
API response compression middleware for RaptorFlow
Compresses responses to reduce bandwidth and improve performance
"""

import gzip
import logging
from typing import Any, Callable, Dict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """Response compression middleware using gzip"""

    def __init__(
        self,
        app,
        minimum_size: int = 1024,  # Compress responses larger than 1KB
        compressible_types: list = None,
        compression_level: int = 6,  # gzip compression level (1-9)
        vary_header: str = "Accept-Encoding",
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.vary_header = vary_header

        # Default compressible content types
        self.compressible_types = compressible_types or [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "text/xml",
            "application/xml",
            "application/vnd.api+json",
            "text/plain",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and compress response if applicable"""

        # Get response from next middleware
        response = await call_next(request)

        # Check if response should be compressed
        if not self._should_compress(request, response):
            return response

        # Compress response
        compressed_response = await self._compress_response(response)

        return compressed_response

    def _should_compress(self, request: Request, response: Response) -> bool:
        """Determine if response should be compressed"""

        # Check if client accepts gzip encoding
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return False

        # Check response status code (only compress successful responses)
        if response.status_code not in [200, 201, 202]:
            return False

        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0]
        if content_type not in self.compressible_types:
            return False

        # Check content length if available
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.minimum_size:
            return False

        # Check if already compressed
        content_encoding = response.headers.get("content-encoding", "")
        if content_encoding:
            return False

        return True

    async def _compress_response(self, response: Response) -> Response:
        """Compress response using gzip"""

        try:
            # Get response body
            if hasattr(response, "body"):
                body = response.body
            elif hasattr(response, "content"):
                body = response.content
            else:
                # For streaming responses, don't compress
                return response

            # Check if body is large enough to compress
            if len(body) < self.minimum_size:
                return response

            # Compress body
            compressed_body = gzip.compress(body, compresslevel=self.compression_level)

            # Create new response with compressed body
            if isinstance(response, JSONResponse):
                compressed_response = JSONResponse(
                    content=response.content if hasattr(response, "content") else {},
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )
            else:
                compressed_response = Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

            # Update headers for compressed response
            compressed_response.headers["content-encoding"] = "gzip"
            compressed_response.headers["content-length"] = str(len(compressed_body))
            compressed_response.headers["vary"] = self.vary_header
            compressed_response.body = compressed_body

            # Remove original content-length if it exists
            if "content-length" in compressed_response.headers:
                del compressed_response.headers["content-length"]

            logger.debug(
                f"Compressed response from {len(body)} to {len(compressed_body)} bytes"
            )

            return compressed_response

        except Exception as e:
            logger.error(f"Failed to compress response: {e}")
            # Return original response if compression fails
            return response


class BrotliMiddleware(BaseHTTPMiddleware):
    """Brotli compression middleware (alternative to gzip)"""

    def __init__(
        self,
        app,
        minimum_size: int = 1024,
        compressible_types: list = None,
        quality: int = 4,  # Brotli quality level (0-11)
        window_bits: int = 22,
        block_bits: int = 22,
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.quality = quality
        self.window_bits = window_bits
        self.block_bits = block_bits

        self.compressible_types = compressible_types or [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "text/xml",
            "application/xml",
            "application/vnd.api+json",
            "text/plain",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and compress response with Brotli if applicable"""

        response = await call_next(request)

        # Check if response should be compressed with Brotli
        if not self._should_compress(request, response):
            return response

        # Try Brotli compression
        compressed_response = await self._compress_with_brotli(response)

        return compressed_response

    def _should_compress(self, request: Request, response: Response) -> bool:
        """Determine if response should be compressed with Brotli"""

        # Check if client accepts br encoding
        accept_encoding = request.headers.get("accept-encoding", "")
        if "br" not in accept_encoding.lower():
            return False

        # Check response status code
        if response.status_code not in [200, 201, 202]:
            return False

        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0]
        if content_type not in self.compressible_types:
            return False

        # Check if already compressed
        content_encoding = response.headers.get("content-encoding", "")
        if content_encoding:
            return False

        return True

    async def _compress_with_brotli(self, response: Response) -> Response:
        """Compress response using Brotli"""

        try:
            import brotli

            # Get response body
            if hasattr(response, "body"):
                body = response.body
            elif hasattr(response, "content"):
                body = response.content
            else:
                return response

            # Check if body is large enough
            if len(body) < self.minimum_size:
                return response

            # Compress with Brotli
            compressed_body = brotli.compress(
                body,
                quality=self.quality,
                lgwin=self.window_bits,
                lgblock=self.block_bits,
            )

            # Create new response
            if isinstance(response, JSONResponse):
                compressed_response = JSONResponse(
                    content=response.content if hasattr(response, "content") else {},
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )
            else:
                compressed_response = Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

            # Update headers
            compressed_response.headers["content-encoding"] = "br"
            compressed_response.headers["content-length"] = str(len(compressed_body))
            compressed_response.body = compressed_body

            logger.debug(
                f"Compressed response with Brotli from {len(body)} to {len(compressed_body)} bytes"
            )

            return compressed_response

        except ImportError:
            logger.warning("Brotli not available, falling back to original response")
            return response
        except Exception as e:
            logger.error(f"Failed to compress with Brotli: {e}")
            return response


class AdaptiveCompressionMiddleware(BaseHTTPMiddleware):
    """Adaptive compression middleware that chooses best compression method"""

    def __init__(
        self,
        app,
        enable_gzip: bool = True,
        enable_brotli: bool = True,
        prefer_brotli: bool = True,
        **kwargs,
    ):
        super().__init__(app)
        self.enable_gzip = enable_gzip
        self.enable_brotli = enable_brotli
        self.prefer_brotli = prefer_brotli

        # Initialize compression middleware instances
        if self.enable_brotli:
            self.brotli_middleware = BrotliMiddleware(app, **kwargs)

        if self.enable_gzip:
            self.gzip_middleware = CompressionMiddleware(app, **kwargs)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with adaptive compression"""

        response = await call_next(request)

        # Get client preferences
        accept_encoding = request.headers.get("accept-encoding", "").lower()

        # Choose compression method based on client preference
        if self.enable_brotli and self.prefer_brotli and "br" in accept_encoding:
            # Try Brotli first
            if self._should_compress(request, response):
                return await self.brotli_middleware._compress_with_brotli(response)

        elif self.enable_gzip and "gzip" in accept_encoding:
            # Use gzip
            if self._should_compress(request, response):
                return await self.gzip_middleware._compress_response(response)

        elif self.enable_brotli and "br" in accept_encoding:
            # Fallback to Brotli
            if self._should_compress(request, response):
                return await self.brotli_middleware._compress_with_brotli(response)

        return response

    def _should_compress(self, request: Request, response: Response) -> bool:
        """Unified compression check"""

        # Check response status
        if response.status_code not in [200, 201, 202]:
            return False

        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0]
        compressible_types = [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "text/xml",
            "application/xml",
            "application/vnd.api+json",
            "text/plain",
        ]

        if content_type not in compressible_types:
            return False

        # Check if already compressed
        content_encoding = response.headers.get("content-encoding", "")
        if content_encoding:
            return False

        return True


def add_compression_middleware(
    app,
    enable_gzip: bool = True,
    enable_brotli: bool = True,
    prefer_brotli: bool = True,
    minimum_size: int = 1024,
    compression_level: int = 6,
) -> None:
    """Add compression middleware to FastAPI app"""

    if enable_brotli and enable_gzip:
        # Use adaptive compression
        middleware = AdaptiveCompressionMiddleware(
            app,
            enable_gzip=enable_gzip,
            enable_brotli=enable_brotli,
            prefer_brotli=prefer_brotli,
            minimum_size=minimum_size,
            compression_level=compression_level,
        )
        app.add_middleware(type(middleware))

    elif enable_brotli:
        # Brotli only
        middleware = BrotliMiddleware(
            app, minimum_size=minimum_size, quality=compression_level
        )
        app.add_middleware(type(middleware))

    elif enable_gzip:
        # Gzip only
        middleware = CompressionMiddleware(
            app, minimum_size=minimum_size, compression_level=compression_level
        )
        app.add_middleware(type(middleware))

    logger.info(
        f"Compression middleware added (gzip: {enable_gzip}, brotli: {enable_brotli})"
    )


# Compression statistics
class CompressionStats:
    """Tracks compression statistics"""

    def __init__(self):
        self.stats = {
            "total_responses": 0,
            "compressed_responses": 0,
            "gzip_responses": 0,
            "brotli_responses": 0,
            "original_bytes": 0,
            "compressed_bytes": 0,
            "compression_ratio": 0.0,
        }

    def record_compression(
        self, original_size: int, compressed_size: int, method: str
    ) -> None:
        """Record compression statistics"""
        self.stats["total_responses"] += 1
        self.stats["compressed_responses"] += 1
        self.stats["original_bytes"] += original_size
        self.stats["compressed_bytes"] += compressed_size

        if method == "gzip":
            self.stats["gzip_responses"] += 1
        elif method == "br":
            self.stats["brotli_responses"] += 1

        # Calculate compression ratio
        if self.stats["original_bytes"] > 0:
            self.stats["compression_ratio"] = (
                1 - (self.stats["compressed_bytes"] / self.stats["original_bytes"])
            ) * 100

    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        return self.stats.copy()


# Global compression stats
_compression_stats = CompressionStats()


def get_compression_stats() -> Dict[str, Any]:
    """Get compression statistics"""
    return _compression_stats.get_stats()

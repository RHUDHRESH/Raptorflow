"""
Cache Compression Manager with gzip/LZ4 Compression and Binary Serialization
Optimizes cache storage with intelligent compression strategies
"""

import gzip
import hashlib
import json
import logging
import pickle
import time
import zlib
import lz4.frame
from typing import Any, Dict, List, Optional, Tuple, Union, Type
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict
import threading
import struct

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class CompressionAlgorithm(Enum):
    """Supported compression algorithms."""
    
    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"
    LZ4 = "lz4"
    HYBRID = "hybrid"  # Automatically selects best algorithm


class SerializationFormat(Enum):
    """Supported serialization formats."""
    
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    BINARY = "binary"
    AUTO = "auto"  # Automatically selects best format


@dataclass
class CompressionResult:
    """Result of compression operation."""
    
    data: bytes
    algorithm: CompressionAlgorithm
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    checksum: str
    
    @property
    def space_saved(self) -> int:
        """Bytes saved by compression."""
        return self.original_size - self.compressed_size
    
    @property
    def space_saved_percent(self) -> float:
        """Percentage of space saved."""
        if self.original_size == 0:
            return 0.0
        return (self.space_saved / self.original_size) * 100


@dataclass
class DecompressionResult:
    """Result of decompression operation."""
    
    data: Any
    algorithm: CompressionAlgorithm
    decompression_time: float
    checksum_verified: bool
    original_checksum: str


class CompressionAnalyzer:
    """Analyzes data to determine optimal compression strategy."""
    
    def __init__(self):
        self.algorithm_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'avg_compression_ratio': 0.0,
            'avg_compression_time': 0.0,
            'avg_decompression_time': 0.0,
            'usage_count': 0,
            'success_rate': 1.0
        })
        
        # Data type characteristics
        self.data_type_profiles = {
            'text': {
                'compressible': True,
                'preferred_algorithms': [CompressionAlgorithm.ZLIB, CompressionAlgorithm.GZIP],
                'min_size_threshold': 1024
            },
            'json': {
                'compressible': True,
                'preferred_algorithms': [CompressionAlgorithm.LZ4, CompressionAlgorithm.ZLIB],
                'min_size_threshold': 512
            },
            'binary': {
                'compressible': False,
                'preferred_algorithms': [CompressionAlgorithm.NONE],
                'min_size_threshold': 2048
            },
            'numeric_array': {
                'compressible': True,
                'preferred_algorithms': [CompressionAlgorithm.LZ4],
                'min_size_threshold': 1024
            },
            'image': {
                'compressible': False,
                'preferred_algorithms': [CompressionAlgorithm.NONE],
                'min_size_threshold': 4096
            }
        }
    
    def analyze_data(self, data: Any) -> Dict[str, Any]:
        """Analyze data characteristics."""
        data_type = self._detect_data_type(data)
        data_size = self._get_data_size(data)
        
        # Calculate entropy (simplified)
        entropy = self._calculate_entropy(data)
        
        # Detect patterns
        patterns = self._detect_patterns(data)
        
        return {
            'data_type': data_type,
            'size': data_size,
            'entropy': entropy,
            'patterns': patterns,
            'compressible': self._is_compressible(data_type, data_size, entropy),
            'profile': self.data_type_profiles.get(data_type, {})
        }
    
    def recommend_algorithm(
        self,
        data: Any,
        performance_priority: bool = False
    ) -> CompressionAlgorithm:
        """Recommend optimal compression algorithm."""
        analysis = self.analyze_data(data)
        
        if not analysis['compressible']:
            return CompressionAlgorithm.NONE
        
        profile = analysis['profile']
        preferred = profile.get('preferred_algorithms', [CompressionAlgorithm.ZLIB])
        
        if performance_priority:
            # Prioritize speed over compression ratio
            algorithm_performance = []
            for algo in preferred:
                perf = self.algorithm_performance[algo.value]
                score = (perf['success_rate'] * 0.5 - 
                         perf['avg_compression_time'] * 0.3 - 
                         perf['avg_decompression_time'] * 0.2)
                algorithm_performance.append((algo, score))
            
            algorithm_performance.sort(key=lambda x: x[1], reverse=True)
            return algorithm_performance[0][0]
        else:
            # Prioritize compression ratio
            algorithm_performance = []
            for algo in preferred:
                perf = self.algorithm_performance[algo.value]
                score = (perf['success_rate'] * 0.3 + 
                         perf['avg_compression_ratio'] * 0.5 - 
                         perf['avg_compression_time'] * 0.2)
                algorithm_performance.append((algo, score))
            
            algorithm_performance.sort(key=lambda x: x[1], reverse=True)
            return algorithm_performance[0][0]
    
    def update_performance(
        self,
        algorithm: CompressionAlgorithm,
        compression_ratio: float,
        compression_time: float,
        decompression_time: float,
        success: bool = True
    ):
        """Update algorithm performance metrics."""
        key = algorithm.value
        metrics = self.algorithm_performance[key]
        
        # Update with exponential moving average
        alpha = 0.1
        
        metrics['avg_compression_ratio'] = (
            alpha * compression_ratio + 
            (1 - alpha) * metrics['avg_compression_ratio']
        )
        metrics['avg_compression_time'] = (
            alpha * compression_time + 
            (1 - alpha) * metrics['avg_compression_time']
        )
        metrics['avg_decompression_time'] = (
            alpha * decompression_time + 
            (1 - alpha) * metrics['avg_decompression_time']
        )
        metrics['usage_count'] += 1
        
        if success:
            metrics['success_rate'] = (
                alpha * 1.0 + 
                (1 - alpha) * metrics['success_rate']
            )
        else:
            metrics['success_rate'] = (
                alpha * 0.0 + 
                (1 - alpha) * metrics['success_rate']
            )
    
    def _detect_data_type(self, data: Any) -> str:
        """Detect data type."""
        if isinstance(data, str):
            return 'text'
        elif isinstance(data, (dict, list)):
            return 'json'
        elif isinstance(data, bytes):
            return 'binary'
        elif NUMPY_AVAILABLE and isinstance(data, np.ndarray):
            return 'numeric_array'
        elif hasattr(data, 'read'):  # File-like object
            return 'image'  # Assume image for file-like
        else:
            return 'unknown'
    
    def _get_data_size(self, data: Any) -> int:
        """Get data size in bytes."""
        if isinstance(data, str):
            return len(data.encode())
        elif isinstance(data, (dict, list)):
            return len(json.dumps(data).encode())
        elif isinstance(data, bytes):
            return len(data)
        elif NUMPY_AVAILABLE and isinstance(data, np.ndarray):
            return data.nbytes
        else:
            return len(pickle.dumps(data))
    
    def _calculate_entropy(self, data: Any) -> float:
        """Calculate data entropy (simplified)."""
        try:
            if isinstance(data, str):
                data_bytes = data.encode()
            elif isinstance(data, (dict, list)):
                data_bytes = json.dumps(data).encode()
            elif isinstance(data, bytes):
                data_bytes = data
            else:
                data_bytes = pickle.dumps(data)
            
            # Calculate byte frequency
            byte_counts = defaultdict(int)
            for byte in data_bytes:
                byte_counts[byte] += 1
            
            # Calculate entropy
            entropy = 0.0
            data_len = len(data_bytes)
            
            for count in byte_counts.values():
                probability = count / data_len
                if probability > 0:
                    entropy -= probability * (probability.bit_length() - 1)
            
            return entropy
            
        except Exception:
            return 0.0
    
    def _detect_patterns(self, data: Any) -> List[str]:
        """Detect data patterns."""
        patterns = []
        
        try:
            if isinstance(data, str):
                # Check for repetitive patterns
                if len(set(data)) < len(data) * 0.5:
                    patterns.append('repetitive')
                
                # Check for structured data
                if data.startswith('{') or data.startswith('['):
                    patterns.append('structured')
                
            elif isinstance(data, (dict, list)):
                patterns.append('structured')
                
                # Check for nested structures
                if isinstance(data, dict) and any(isinstance(v, (dict, list)) for v in data.values()):
                    patterns.append('nested')
            
            elif isinstance(data, bytes):
                # Check for binary patterns
                unique_bytes = len(set(data))
                if unique_bytes < len(data) * 0.3:
                    patterns.append('repetitive')
        
        except Exception:
            pass
        
        return patterns
    
    def _is_compressible(self, data_type: str, size: int, entropy: float) -> bool:
        """Determine if data is compressible."""
        profile = self.data_type_profiles.get(data_type, {})
        
        if not profile.get('compressible', True):
            return False
        
        min_size = profile.get('min_size_threshold', 1024)
        if size < min_size:
            return False
        
        # Low entropy data is more compressible
        if entropy < 6.0:  # On a scale of 0-8
            return True
        
        return True


class SerializationManager:
    """Manages data serialization formats."""
    
    def __init__(self):
        self.format_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'avg_size_ratio': 1.0,
            'avg_serialization_time': 0.0,
            'avg_deserialization_time': 0.0,
            'usage_count': 0
        })
    
    def serialize(
        self,
        data: Any,
        format: SerializationFormat = SerializationFormat.AUTO
    ) -> Tuple[bytes, SerializationFormat]:
        """Serialize data to bytes."""
        start_time = time.time()
        
        if format == SerializationFormat.AUTO:
            format = self._recommend_format(data)
        
        try:
            if format == SerializationFormat.JSON:
                serialized = json.dumps(data, separators=(',', ':'), default=str).encode()
            elif format == SerializationFormat.PICKLE:
                serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            elif format == SerializationFormat.MSGPACK and MSGPACK_AVAILABLE:
                serialized = msgpack.packb(data, use_bin_type=True)
            elif format == SerializationFormat.BINARY:
                if isinstance(data, bytes):
                    serialized = data
                else:
                    # Convert to binary representation
                    serialized = str(data).encode()
            else:
                # Fallback to JSON
                serialized = json.dumps(data, separators=(',', ':'), default=str).encode()
                format = SerializationFormat.JSON
            
            # Update performance metrics
            serialization_time = time.time() - start_time
            self._update_performance(format, serialization_time, 0.0, len(serialized))
            
            return serialized, format
            
        except Exception as e:
            logger.error(f"Serialization error with {format.value}: {e}")
            # Fallback to JSON
            try:
                serialized = json.dumps(data, separators=(',', ':'), default=str).encode()
                return serialized, SerializationFormat.JSON
            except Exception as fallback_error:
                logger.error(f"Fallback serialization failed: {fallback_error}")
                raise
    
    def deserialize(
        self,
        data: bytes,
        format: SerializationFormat
    ) -> Any:
        """Deserialize data from bytes."""
        start_time = time.time()
        
        try:
            if format == SerializationFormat.JSON:
                deserialized = json.loads(data.decode())
            elif format == SerializationFormat.PICKLE:
                deserialized = pickle.loads(data)
            elif format == SerializationFormat.MSGPACK and MSGPACK_AVAILABLE:
                deserialized = msgpack.unpackb(data, raw=False)
            elif format == SerializationFormat.BINARY:
                deserialized = data
            else:
                # Try JSON as fallback
                deserialized = json.loads(data.decode())
            
            # Update performance metrics
            deserialization_time = time.time() - start_time
            self._update_performance(format, 0.0, deserialization_time, len(data))
            
            return deserialized
            
        except Exception as e:
            logger.error(f"Deserialization error with {format.value}: {e}")
            # Try to recover with different formats
            return self._attempt_recovery(data)
    
    def _recommend_format(self, data: Any) -> SerializationFormat:
        """Recommend optimal serialization format."""
        if isinstance(data, (dict, list, str, int, float, bool, type(None))):
            # JSON is good for structured data
            if MSGPACK_AVAILABLE and isinstance(data, (dict, list)):
                return SerializationFormat.MSGPACK
            return SerializationFormat.JSON
        elif isinstance(data, bytes):
            return SerializationFormat.BINARY
        else:
            # Use pickle for complex objects
            return SerializationFormat.PICKLE
    
    def _update_performance(
        self,
        format: SerializationFormat,
        serialization_time: float,
        deserialization_time: float,
        data_size: int
    ):
        """Update format performance metrics."""
        key = format.value
        metrics = self.format_performance[key]
        
        alpha = 0.1
        
        metrics['avg_serialization_time'] = (
            alpha * serialization_time + 
            (1 - alpha) * metrics['avg_serialization_time']
        )
        metrics['avg_deserialization_time'] = (
            alpha * deserialization_time + 
            (1 - alpha) * metrics['avg_deserialization_time']
        )
        metrics['usage_count'] += 1
    
    def _attempt_recovery(self, data: bytes) -> Any:
        """Attempt to recover data by trying different formats."""
        formats_to_try = [
            SerializationFormat.JSON,
            SerializationFormat.PICKLE,
            SerializationFormat.MSGPACK
        ]
        
        for format in formats_to_try:
            try:
                if format == SerializationFormat.JSON:
                    return json.loads(data.decode())
                elif format == SerializationFormat.PICKLE:
                    return pickle.loads(data)
                elif format == SerializationFormat.MSGPACK and MSGPACK_AVAILABLE:
                    return msgpack.unpackb(data, raw=False)
            except Exception:
                continue
        
        # Last resort: return raw bytes
        return data


class CacheCompressionManager:
    """Main cache compression manager."""
    
    def __init__(
        self,
        default_algorithm: CompressionAlgorithm = CompressionAlgorithm.HYBRID,
        default_format: SerializationFormat = SerializationFormat.AUTO,
        compression_threshold: int = 1024,
        enable_adaptive: bool = True
    ):
        self.default_algorithm = default_algorithm
        self.default_format = default_format
        self.compression_threshold = compression_threshold
        self.enable_adaptive = enable_adaptive
        
        # Components
        self.analyzer = CompressionAnalyzer()
        self.serialization_manager = SerializationManager()
        
        # Performance tracking
        self.stats = {
            'total_compressions': 0,
            'total_decompressions': 0,
            'total_space_saved': 0,
            'average_compression_ratio': 0.0,
            'algorithm_usage': defaultdict(int),
            'format_usage': defaultdict(int),
            'compression_failures': 0,
            'decompression_failures': 0
        }
        
        # Compression cache for small frequently used data
        self.compression_cache: Dict[str, CompressionResult] = {}
        self.cache_lock = threading.RLock()
    
    def compress(
        self,
        data: Any,
        algorithm: Optional[CompressionAlgorithm] = None,
        format: Optional[SerializationFormat] = None
    ) -> CompressionResult:
        """Compress data with optimal algorithm."""
        start_time = time.time()
        
        try:
            # Analyze data
            analysis = self.analyzer.analyze_data(data)
            
            # Skip compression for small or incompressible data
            if (analysis['size'] < self.compression_threshold or 
                not analysis['compressible']):
                
                serialized, used_format = self.serialization_manager.serialize(
                    data, format or self.default_format
                )
                
                result = CompressionResult(
                    data=serialized,
                    algorithm=CompressionAlgorithm.NONE,
                    original_size=analysis['size'],
                    compressed_size=len(serialized),
                    compression_ratio=1.0,
                    compression_time=time.time() - start_time,
                    checksum=self._calculate_checksum(serialized)
                )
                
                self._update_stats(result)
                return result
            
            # Select algorithm
            if algorithm is None:
                algorithm = self.analyzer.recommend_algorithm(
                    data, performance_priority=True
                )
            elif algorithm == CompressionAlgorithm.HYBRID:
                algorithm = self.analyzer.recommend_algorithm(data)
            
            # Serialize data
            serialized, used_format = self.serialization_manager.serialize(
                data, format or self.default_format
            )
            
            # Compress serialized data
            compressed_data = self._compress_with_algorithm(serialized, algorithm)
            
            # Create result
            result = CompressionResult(
                data=compressed_data,
                algorithm=algorithm,
                original_size=analysis['size'],
                compressed_size=len(compressed_data),
                compression_ratio=len(compressed_data) / len(serialized),
                compression_time=time.time() - start_time,
                checksum=self._calculate_checksum(compressed_data)
            )
            
            # Update performance
            self.analyzer.update_performance(
                algorithm,
                result.compression_ratio,
                result.compression_time,
                0.0,  # Will be updated on decompression
                True
            )
            
            self._update_stats(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Compression error: {e}")
            self.stats['compression_failures'] += 1
            
            # Return uncompressed data as fallback
            try:
                serialized, used_format = self.serialization_manager.serialize(
                    data, format or self.default_format
                )
                
                return CompressionResult(
                    data=serialized,
                    algorithm=CompressionAlgorithm.NONE,
                    original_size=len(str(data).encode()),
                    compressed_size=len(serialized),
                    compression_ratio=1.0,
                    compression_time=time.time() - start_time,
                    checksum=self._calculate_checksum(serialized)
                )
            except Exception as fallback_error:
                logger.error(f"Fallback compression failed: {fallback_error}")
                raise
    
    def decompress(
        self,
        compressed_data: bytes,
        algorithm: CompressionAlgorithm,
        original_checksum: str,
        format: SerializationFormat
    ) -> DecompressionResult:
        """Decompress data."""
        start_time = time.time()
        
        try:
            # Decompress data
            if algorithm == CompressionAlgorithm.NONE:
                decompressed_data = compressed_data
            else:
                decompressed_data = self._decompress_with_algorithm(
                    compressed_data, algorithm
                )
            
            # Verify checksum
            current_checksum = self._calculate_checksum(decompressed_data)
            checksum_verified = current_checksum == original_checksum
            
            if not checksum_verified:
                logger.warning(f"Checksum mismatch: expected {original_checksum}, got {current_checksum}")
            
            # Deserialize data
            deserialized_data = self.serialization_manager.deserialize(
                decompressed_data, format
            )
            
            result = DecompressionResult(
                data=deserialized_data,
                algorithm=algorithm,
                decompression_time=time.time() - start_time,
                checksum_verified=checksum_verified,
                original_checksum=original_checksum
            )
            
            # Update performance
            self.analyzer.update_performance(
                algorithm,
                0.0,  # Will be updated on compression
                0.0,
                result.decompression_time,
                checksum_verified
            )
            
            self.stats['total_decompressions'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Decompression error: {e}")
            self.stats['decompression_failures'] += 1
            raise
    
    def _compress_with_algorithm(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """Compress data with specific algorithm."""
        if algorithm == CompressionAlgorithm.ZLIB:
            return zlib.compress(data, level=6)
        elif algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data, compresslevel=6)
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.compress(data, compression_level=5)
        else:
            return data
    
    def _decompress_with_algorithm(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """Decompress data with specific algorithm."""
        if algorithm == CompressionAlgorithm.ZLIB:
            return zlib.decompress(data)
        elif algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(data)
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.decompress(data)
        else:
            return data
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate checksum for data integrity."""
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _update_stats(self, result: CompressionResult):
        """Update compression statistics."""
        self.stats['total_compressions'] += 1
        self.stats['algorithm_usage'][result.algorithm.value] += 1
        self.stats['total_space_saved'] += result.space_saved
        
        # Update average compression ratio
        current_avg = self.stats['average_compression_ratio']
        self.stats['average_compression_ratio'] = (
            (current_avg + result.compression_ratio) / 2
        )
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        return {
            'compression_stats': self.stats.copy(),
            'algorithm_performance': dict(self.analyzer.algorithm_performance),
            'format_performance': dict(self.serialization_manager.format_performance),
            'cache_size': len(self.compression_cache)
        }
    
    def benchmark_algorithms(self, test_data: Any) -> Dict[str, Any]:
        """Benchmark compression algorithms on test data."""
        algorithms = [
            CompressionAlgorithm.NONE,
            CompressionAlgorithm.ZLIB,
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.LZ4
        ]
        
        results = {}
        
        for algorithm in algorithms:
            try:
                start_time = time.time()
                result = self.compress(test_data, algorithm=algorithm)
                
                results[algorithm.value] = {
                    'compression_ratio': result.compression_ratio,
                    'compression_time': result.compression_time,
                    'space_saved': result.space_saved,
                    'space_saved_percent': result.space_saved_percent
                }
                
            except Exception as e:
                results[algorithm.value] = {'error': str(e)}
        
        return results


# Global compression manager instance
_compression_manager: Optional[CacheCompressionManager] = None


def get_compression_manager() -> CacheCompressionManager:
    """Get the global compression manager."""
    global _compression_manager
    if _compression_manager is None:
        _compression_manager = CacheCompressionManager()
    return _compression_manager


# Convenience functions
def compress_data(
    data: Any,
    algorithm: Optional[CompressionAlgorithm] = None
) -> CompressionResult:
    """Compress data (convenience function)."""
    manager = get_compression_manager()
    return manager.compress(data, algorithm)


def decompress_data(
    compressed_data: bytes,
    algorithm: CompressionAlgorithm,
    original_checksum: str,
    format: SerializationFormat
) -> DecompressionResult:
    """Decompress data (convenience function)."""
    manager = get_compression_manager()
    return manager.decompress(compressed_data, algorithm, original_checksum, format)


def get_compression_statistics() -> Dict[str, Any]:
    """Get compression statistics (convenience function)."""
    manager = get_compression_manager()
    return manager.get_compression_stats()

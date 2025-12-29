"""
Part 20: Multi-Modal Search and Content Understanding
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements multi-modal search capabilities, supporting text, image,
video, and audio content understanding and retrieval.
"""

import asyncio
import base64
import hashlib
import io
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.unified_search_part1 import ContentType, SearchQuery, SearchResult
from core.unified_search_part19 import ContentProcessor, TextAnalysis

logger = logging.getLogger("raptorflow.unified_search.multimodal")


class ModalityType(Enum):
    """Types of content modalities."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    TABLE = "table"
    CHART = "chart"
    CODE = "code"


class MediaType(Enum):
    """Media file types."""

    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MP3 = "mp3"
    WAV = "wav"
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"


@dataclass
class MediaContent:
    """Media content representation."""

    content_id: str
    modality: ModalityType
    media_type: MediaType
    url: Optional[str] = None
    base64_data: Optional[str] = None
    file_size_bytes: int = 0
    duration_seconds: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_features: Dict[str, Any] = field(default_factory=dict)
    text_transcript: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content_id": self.content_id,
            "modality": self.modality.value,
            "media_type": self.media_type.value,
            "url": self.url,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "dimensions": self.dimensions,
            "metadata": self.metadata,
            "extracted_features": self.extracted_features,
            "text_transcript": self.text_transcript,
            "description": self.description,
            "tags": self.tags,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MultiModalQuery:
    """Multi-modal search query."""

    query_id: str
    text_query: Optional[str] = None
    image_query: Optional[MediaContent] = None
    audio_query: Optional[MediaContent] = None
    video_query: Optional[MediaContent] = None
    modality_weights: Dict[ModalityType, float] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    max_results: int = 10
    similarity_threshold: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_id": self.query_id,
            "text_query": self.text_query,
            "image_query": self.image_query.to_dict() if self.image_query else None,
            "audio_query": self.audio_query.to_dict() if self.audio_query else None,
            "video_query": self.video_query.to_dict() if self.video_query else None,
            "modality_weights": {k.value: v for k, v in self.modality_weights.items()},
            "filters": self.filters,
            "max_results": self.max_results,
            "similarity_threshold": self.similarity_threshold,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MultiModalResult:
    """Multi-modal search result."""

    content: MediaContent
    similarity_score: float
    relevance_score: float
    modality_matches: Dict[ModalityType, float]
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content.to_dict(),
            "similarity_score": self.similarity_score,
            "relevance_score": self.relevance_score,
            "modality_matches": {k.value: v for k, v in self.modality_matches.items()},
            "explanation": self.explanation,
            "metadata": self.metadata,
        }


class ImageProcessor:
    """Processes and analyzes image content."""

    def __init__(self):
        self.supported_formats = {MediaType.JPEG, MediaType.PNG, MediaType.GIF}
        self.max_file_size_mb = 50
        self.max_dimensions = (4096, 4096)

    async def process_image(
        self, image_data: Union[str, bytes], media_type: MediaType
    ) -> MediaContent:
        """Process image and extract features."""
        content_id = str(uuid.uuid4())

        # Convert base64 to bytes if needed
        if isinstance(image_data, str):
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 image data: {e}")
        else:
            image_bytes = image_data

        # Validate image
        self._validate_image(image_bytes, media_type)

        # Extract basic features
        features = await self._extract_image_features(image_bytes, media_type)

        # Generate description (simplified)
        description = self._generate_image_description(features)

        # Extract tags
        tags = self._extract_image_tags(features)

        return MediaContent(
            content_id=content_id,
            modality=ModalityType.IMAGE,
            media_type=media_type,
            base64_data=(
                base64.b64encode(image_bytes).decode()
                if isinstance(image_data, str)
                else base64.b64encode(image_bytes).decode()
            ),
            file_size_bytes=len(image_bytes),
            dimensions=features.get("dimensions"),
            metadata=features.get("metadata", {}),
            extracted_features=features,
            description=description,
            tags=tags,
            confidence=features.get("confidence", 0.5),
        )

    def _validate_image(self, image_bytes: bytes, media_type: MediaType):
        """Validate image data."""
        # Check file size
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > self.max_file_size_mb:
            raise ValueError(
                f"Image too large: {size_mb:.1f}MB > {self.max_file_size_mb}MB"
            )

        # Check image format
        if media_type not in self.supported_formats:
            raise ValueError(f"Unsupported image format: {media_type}")

        # Basic image header validation
        if media_type == MediaType.JPEG:
            if not image_bytes.startswith(b"\xff\xd8\xff"):
                raise ValueError("Invalid JPEG image")
        elif media_type == MediaType.PNG:
            if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("Invalid PNG image")

    async def _extract_image_features(
        self, image_bytes: bytes, media_type: MediaType
    ) -> Dict[str, Any]:
        """Extract features from image."""
        # This would use computer vision libraries in production
        # For now, provide mock features

        features = {
            "dimensions": (1920, 1080),  # Mock dimensions
            "color_histogram": [0.1, 0.2, 0.3, 0.4],  # Mock color distribution
            "edge_density": 0.15,
            "texture_complexity": 0.7,
            "brightness": 0.6,
            "contrast": 0.8,
            "sharpness": 0.75,
            "metadata": {
                "format": media_type.value,
                "has_transparency": media_type == MediaType.PNG,
                "aspect_ratio": 16 / 9,
            },
            "confidence": 0.8,
        }

        return features

    def _generate_image_description(self, features: Dict[str, Any]) -> str:
        """Generate image description."""
        dimensions = features.get("dimensions", (0, 0))
        brightness = features.get("brightness", 0.5)

        description_parts = []

        if dimensions[0] > 0 and dimensions[1] > 0:
            description_parts.append(f"{dimensions[0]}x{dimensions[1]} image")

        if brightness > 0.7:
            description_parts.append("bright")
        elif brightness < 0.3:
            description_parts.append("dark")

        if features.get("edge_density", 0) > 0.2:
            description_parts.append("detailed")

        return " ".join(description_parts) if description_parts else "digital image"

    def _extract_image_tags(self, features: Dict[str, Any]) -> List[str]:
        """Extract tags from image features."""
        tags = []

        # Add tags based on features
        if features.get("brightness", 0.5) > 0.7:
            tags.append("bright")

        if features.get("edge_density", 0) > 0.2:
            tags.append("detailed")

        if features.get("texture_complexity", 0) > 0.6:
            tags.append("textured")

        dimensions = features.get("dimensions", (0, 0))
        if dimensions[0] > dimensions[1]:
            tags.append("landscape")
        elif dimensions[1] > dimensions[0]:
            tags.append("portrait")

        return tags


class AudioProcessor:
    """Processes and analyzes audio content."""

    def __init__(self):
        self.supported_formats = {MediaType.MP3, MediaType.WAV}
        self.max_file_size_mb = 100
        self.max_duration_minutes = 60

    async def process_audio(
        self, audio_data: Union[str, bytes], media_type: MediaType
    ) -> MediaContent:
        """Process audio and extract features."""
        content_id = str(uuid.uuid4())

        # Convert base64 to bytes if needed
        if isinstance(audio_data, str):
            try:
                audio_bytes = base64.b64decode(audio_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 audio data: {e}")
        else:
            audio_bytes = audio_data

        # Validate audio
        self._validate_audio(audio_bytes, media_type)

        # Extract features
        features = await self._extract_audio_features(audio_bytes, media_type)

        # Generate transcript (mock)
        transcript = self._generate_audio_transcript(features)

        # Extract tags
        tags = self._extract_audio_tags(features)

        return MediaContent(
            content_id=content_id,
            modality=ModalityType.AUDIO,
            media_type=media_type,
            base64_data=base64.b64encode(audio_bytes).decode(),
            file_size_bytes=len(audio_bytes),
            duration_seconds=features.get("duration"),
            metadata=features.get("metadata", {}),
            extracted_features=features,
            text_transcript=transcript,
            tags=tags,
            confidence=features.get("confidence", 0.5),
        )

    def _validate_audio(self, audio_bytes: bytes, media_type: MediaType):
        """Validate audio data."""
        # Check file size
        size_mb = len(audio_bytes) / (1024 * 1024)
        if size_mb > self.max_file_size_mb:
            raise ValueError(
                f"Audio too large: {size_mb:.1f}MB > {self.max_file_size_mb}MB"
            )

        # Check audio format
        if media_type not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {media_type}")

    async def _extract_audio_features(
        self, audio_bytes: bytes, media_type: MediaType
    ) -> Dict[str, Any]:
        """Extract features from audio."""
        # This would use audio processing libraries in production
        features = {
            "duration": 120.5,  # Mock duration in seconds
            "sample_rate": 44100,
            "channels": 2,
            "bitrate": 320000,
            "spectral_centroid": 2000.0,
            "zero_crossing_rate": 0.05,
            "energy": 0.8,
            "tempo": 120.0,
            "key": "C",
            "metadata": {"format": media_type.value, "codec": "MP3", "stereo": True},
            "confidence": 0.7,
        }

        return features

    def _generate_audio_transcript(self, features: Dict[str, Any]) -> str:
        """Generate audio transcript (mock)."""
        # In production, this would use speech-to-text
        return "This is a mock transcript of the audio content."

    def _extract_audio_tags(self, features: Dict[str, Any]) -> List[str]:
        """Extract tags from audio features."""
        tags = []

        duration = features.get("duration", 0)
        if duration < 30:
            tags.append("short")
        elif duration > 300:
            tags.append("long")

        if features.get("tempo", 0) > 120:
            tags.append("fast")
        elif features.get("tempo", 0) < 80:
            tags.append("slow")

        if features.get("channels", 1) > 1:
            tags.append("stereo")
        else:
            tags.append("mono")

        return tags


class VideoProcessor:
    """Processes and analyzes video content."""

    def __init__(self):
        self.supported_formats = {MediaType.MP4, MediaType.AVI, MediaType.MOV}
        self.max_file_size_mb = 500
        self.max_duration_minutes = 120
        self.audio_processor = AudioProcessor()
        self.image_processor = ImageProcessor()

    async def process_video(
        self, video_data: Union[str, bytes], media_type: MediaType
    ) -> MediaContent:
        """Process video and extract features."""
        content_id = str(uuid.uuid4())

        # Convert base64 to bytes if needed
        if isinstance(video_data, str):
            try:
                video_bytes = base64.b64decode(video_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 video data: {e}")
        else:
            video_bytes = video_data

        # Validate video
        self._validate_video(video_bytes, media_type)

        # Extract features
        features = await self._extract_video_features(video_bytes, media_type)

        # Extract key frames as images
        key_frames = await self._extract_key_frames(video_bytes)

        # Extract audio track
        audio_features = features.get("audio_features", {})

        # Generate description
        description = self._generate_video_description(features, key_frames)

        # Extract tags
        tags = self._extract_video_tags(features, key_frames)

        return MediaContent(
            content_id=content_id,
            modality=ModalityType.VIDEO,
            media_type=media_type,
            base64_data=base64.b64encode(video_bytes).decode(),
            file_size_bytes=len(video_bytes),
            duration_seconds=features.get("duration"),
            dimensions=features.get("dimensions"),
            metadata={
                **features.get("metadata", {}),
                "key_frames": key_frames,
                "audio_features": audio_features,
            },
            extracted_features=features,
            description=description,
            tags=tags,
            confidence=features.get("confidence", 0.5),
        )

    def _validate_video(self, video_bytes: bytes, media_type: MediaType):
        """Validate video data."""
        # Check file size
        size_mb = len(video_bytes) / (1024 * 1024)
        if size_mb > self.max_file_size_mb:
            raise ValueError(
                f"Video too large: {size_mb:.1f}MB > {self.max_file_size_mb}MB"
            )

        # Check video format
        if media_type not in self.supported_formats:
            raise ValueError(f"Unsupported video format: {media_type}")

    async def _extract_video_features(
        self, video_bytes: bytes, media_type: MediaType
    ) -> Dict[str, Any]:
        """Extract features from video."""
        # This would use video processing libraries in production
        features = {
            "duration": 300.0,  # Mock duration in seconds
            "dimensions": (1920, 1080),
            "frame_rate": 30.0,
            "bitrate": 5000000,
            "codec": "H.264",
            "audio_features": {
                "has_audio": True,
                "audio_codec": "AAC",
                "audio_channels": 2,
                "audio_sample_rate": 44100,
            },
            "scene_changes": 15,
            "motion_intensity": 0.6,
            "brightness": 0.7,
            "contrast": 0.8,
            "metadata": {
                "format": media_type.value,
                "container": media_type.value.upper(),
                "has_subtitles": False,
            },
            "confidence": 0.8,
        }

        return features

    async def _extract_key_frames(self, video_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract key frames from video."""
        # Mock key frame extraction
        key_frames = [
            {"timestamp": 0.0, "frame_number": 0, "description": "Opening scene"},
            {"timestamp": 60.0, "frame_number": 1800, "description": "Middle scene"},
            {"timestamp": 240.0, "frame_number": 7200, "description": "Ending scene"},
        ]

        return key_frames

    def _generate_video_description(
        self, features: Dict[str, Any], key_frames: List[Dict[str, Any]]
    ) -> str:
        """Generate video description."""
        duration = features.get("duration", 0)
        dimensions = features.get("dimensions", (0, 0))

        description_parts = []

        if duration > 0:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            description_parts.append(f"{minutes}:{seconds:02d} video")

        if dimensions[0] > 0 and dimensions[1] > 0:
            description_parts.append(f"{dimensions[0]}x{dimensions[1]}")

        if features.get("motion_intensity", 0) > 0.7:
            description_parts.append("high motion")
        elif features.get("motion_intensity", 0) < 0.3:
            description_parts.append("low motion")

        return " ".join(description_parts) if description_parts else "digital video"

    def _extract_video_tags(
        self, features: Dict[str, Any], key_frames: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract tags from video features."""
        tags = []

        duration = features.get("duration", 0)
        if duration < 60:
            tags.append("short")
        elif duration > 600:
            tags.append("long")

        dimensions = features.get("dimensions", (0, 0))
        if dimensions[0] >= 3840:  # 4K
            tags.append("4K")
        elif dimensions[0] >= 1920:  # Full HD
            tags.append("HD")
        elif dimensions[0] >= 1280:  # HD
            tags.append("720p")

        if features.get("motion_intensity", 0) > 0.7:
            tags.append("action")

        if features.get("audio_features", {}).get("has_audio"):
            tags.append("with_audio")

        return tags


class MultiModalSearchEngine:
    """Multi-modal search engine."""

    def __init__(self):
        self.content_index: Dict[str, MediaContent] = {}
        self.modality_index: Dict[ModalityType, Set[str]] = defaultdict(set)
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        self.feature_index: Dict[str, Dict[str, Any]] = {}

        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()

        self.processors = {
            ModalityType.IMAGE: self.image_processor,
            ModalityType.AUDIO: self.audio_processor,
            ModalityType.VIDEO: self.video_processor,
        }

    async def index_content(self, content: MediaContent):
        """Index multi-modal content."""
        self.content_index[content.content_id] = content
        self.modality_index[content.modality].add(content.content_id)

        # Index tags
        for tag in content.tags:
            self.tag_index[tag.lower()].add(content.content_id)

        # Index features
        self.feature_index[content.content_id] = content.extracted_features

        logger.info(f"Indexed {content.modality.value} content: {content.content_id}")

    async def search(self, query: MultiModalQuery) -> List[MultiModalResult]:
        """Perform multi-modal search."""
        results = []

        # Text-based search
        if query.text_query:
            text_results = await self._search_text(
                query.text_query, query.modality_weights, query.filters
            )
            results.extend(text_results)

        # Image-based search
        if query.image_query:
            image_results = await self._search_by_image(
                query.image_query, query.modality_weights, query.filters
            )
            results.extend(image_results)

        # Audio-based search
        if query.audio_query:
            audio_results = await self._search_by_audio(
                query.audio_query, query.modality_weights, query.filters
            )
            results.extend(audio_results)

        # Video-based search
        if query.video_query:
            video_results = await self._search_by_video(
                query.video_query, query.modality_weights, query.filters
            )
            results.extend(video_results)

        # Sort and filter results
        results = self._rank_and_filter_results(results, query)

        return results[: query.max_results]

    async def _search_text(
        self,
        text_query: str,
        modality_weights: Dict[ModalityType, float],
        filters: Dict[str, Any],
    ) -> List[MultiModalResult]:
        """Search by text query."""
        results = []
        query_lower = text_query.lower()

        for content_id, content in self.content_index.items():
            # Check modality filter
            if modality_weights and content.modality not in modality_weights:
                continue

            # Calculate text similarity
            similarity = self._calculate_text_similarity(query_lower, content)

            if similarity > 0.3:  # Threshold
                modality_matches = {content.modality: similarity}
                relevance_score = similarity * modality_weights.get(
                    content.modality, 1.0
                )

                result = MultiModalResult(
                    content=content,
                    similarity_score=similarity,
                    relevance_score=relevance_score,
                    modality_matches=modality_matches,
                    explanation=f"Text match: {similarity:.2f}",
                )
                results.append(result)

        return results

    async def _search_by_image(
        self,
        query_image: MediaContent,
        modality_weights: Dict[ModalityType, float],
        filters: Dict[str, Any],
    ) -> List[MultiModalResult]:
        """Search by image similarity."""
        results = []

        # Search for similar images
        image_content_ids = self.modality_index.get(ModalityType.IMAGE, set())

        for content_id in image_content_ids:
            content = self.content_index[content_id]

            # Calculate image similarity
            similarity = self._calculate_image_similarity(query_image, content)

            if similarity > 0.3:
                modality_matches = {ModalityType.IMAGE: similarity}
                relevance_score = similarity * modality_weights.get(
                    ModalityType.IMAGE, 1.0
                )

                result = MultiModalResult(
                    content=content,
                    similarity_score=similarity,
                    relevance_score=relevance_score,
                    modality_matches=modality_matches,
                    explanation=f"Image similarity: {similarity:.2f}",
                )
                results.append(result)

        return results

    async def _search_by_audio(
        self,
        query_audio: MediaContent,
        modality_weights: Dict[ModalityType, float],
        filters: Dict[str, Any],
    ) -> List[MultiModalResult]:
        """Search by audio similarity."""
        results = []

        # Search for similar audio
        audio_content_ids = self.modality_index.get(ModalityType.AUDIO, set())

        for content_id in audio_content_ids:
            content = self.content_index[content_id]

            # Calculate audio similarity
            similarity = self._calculate_audio_similarity(query_audio, content)

            if similarity > 0.3:
                modality_matches = {ModalityType.AUDIO: similarity}
                relevance_score = similarity * modality_weights.get(
                    ModalityType.AUDIO, 1.0
                )

                result = MultiModalResult(
                    content=content,
                    similarity_score=similarity,
                    relevance_score=relevance_score,
                    modality_matches=modality_matches,
                    explanation=f"Audio similarity: {similarity:.2f}",
                )
                results.append(result)

        return results

    async def _search_by_video(
        self,
        query_video: MediaContent,
        modality_weights: Dict[ModalityType, float],
        filters: Dict[str, Any],
    ) -> List[MultiModalResult]:
        """Search by video similarity."""
        results = []

        # Search for similar videos
        video_content_ids = self.modality_index.get(ModalityType.VIDEO, set())

        for content_id in video_content_ids:
            content = self.content_index[content_id]

            # Calculate video similarity
            similarity = self._calculate_video_similarity(query_video, content)

            if similarity > 0.3:
                modality_matches = {ModalityType.VIDEO: similarity}
                relevance_score = similarity * modality_weights.get(
                    ModalityType.VIDEO, 1.0
                )

                result = MultiModalResult(
                    content=content,
                    similarity_score=similarity,
                    relevance_score=relevance_score,
                    modality_matches=modality_matches,
                    explanation=f"Video similarity: {similarity:.2f}",
                )
                results.append(result)

        return results

    def _calculate_text_similarity(self, query: str, content: MediaContent) -> float:
        """Calculate text similarity score."""
        # Check description
        if content.description:
            desc_lower = content.description.lower()
            common_words = set(query.split()) & set(desc_lower.split())
            if common_words:
                return len(common_words) / len(set(query.split()))

        # Check transcript
        if content.text_transcript:
            transcript_lower = content.text_transcript.lower()
            common_words = set(query.split()) & set(transcript_lower.split())
            if common_words:
                return len(common_words) / len(set(query.split()))

        # Check tags
        query_tags = set(query.split())
        content_tags = set(tag.lower() for tag in content.tags)
        common_tags = query_tags & content_tags
        if common_tags:
            return len(common_tags) / len(query_tags) if query_tags else 0

        return 0.0

    def _calculate_image_similarity(
        self, query_image: MediaContent, content: MediaContent
    ) -> float:
        """Calculate image similarity score."""
        # Compare extracted features
        query_features = query_image.extracted_features
        content_features = content.extracted_features

        # Compare dimensions
        query_dims = query_features.get("dimensions")
        content_dims = content_features.get("dimensions")

        if query_dims and content_dims:
            # Simple aspect ratio similarity
            query_ratio = query_dims[0] / query_dims[1] if query_dims[1] > 0 else 0
            content_ratio = (
                content_dims[0] / content_dims[1] if content_dims[1] > 0 else 0
            )

            ratio_similarity = 1.0 - abs(query_ratio - content_ratio)

            # Compare brightness
            query_brightness = query_features.get("brightness", 0.5)
            content_brightness = content_features.get("brightness", 0.5)
            brightness_similarity = 1.0 - abs(query_brightness - content_brightness)

            return (ratio_similarity + brightness_similarity) / 2

        return 0.0

    def _calculate_audio_similarity(
        self, query_audio: MediaContent, content: MediaContent
    ) -> float:
        """Calculate audio similarity score."""
        # Compare audio features
        query_features = query_audio.extracted_features
        content_features = content.extracted_features

        # Compare duration
        query_duration = query_features.get("duration", 0)
        content_duration = content_features.get("duration", 0)

        if query_duration > 0 and content_duration > 0:
            duration_similarity = 1.0 - abs(query_duration - content_duration) / max(
                query_duration, content_duration
            )

            # Compare tempo
            query_tempo = query_features.get("tempo", 0)
            content_tempo = content_features.get("tempo", 0)

            if query_tempo > 0 and content_tempo > 0:
                tempo_similarity = 1.0 - abs(query_tempo - content_tempo) / max(
                    query_tempo, content_tempo
                )
                return (duration_similarity + tempo_similarity) / 2

        return 0.0

    def _calculate_video_similarity(
        self, query_video: MediaContent, content: MediaContent
    ) -> float:
        """Calculate video similarity score."""
        # Combine image and audio similarity
        image_similarity = self._calculate_image_similarity(query_video, content)

        # Compare video-specific features
        query_features = query_video.extracted_features
        content_features = content.extracted_features

        # Compare duration
        query_duration = query_features.get("duration", 0)
        content_duration = content_features.get("duration", 0)

        duration_similarity = 0.0
        if query_duration > 0 and content_duration > 0:
            duration_similarity = 1.0 - abs(query_duration - content_duration) / max(
                query_duration, content_duration
            )

        # Combine similarities
        return (image_similarity * 0.7) + (duration_similarity * 0.3)

    def _rank_and_filter_results(
        self, results: List[MultiModalResult], query: MultiModalQuery
    ) -> List[MultiModalResult]:
        """Rank and filter search results."""
        # Filter by similarity threshold
        filtered_results = [
            result
            for result in results
            if result.similarity_score >= query.similarity_threshold
        ]

        # Sort by relevance score
        filtered_results.sort(key=lambda x: x.relevance_score, reverse=True)

        return filtered_results

    def get_stats(self) -> Dict[str, Any]:
        """Get multi-modal search statistics."""
        modality_counts = {}
        for modality, content_ids in self.modality_index.items():
            modality_counts[modality.value] = len(content_ids)

        return {
            "total_content": len(self.content_index),
            "modality_distribution": modality_counts,
            "total_tags": len(self.tag_index),
            "supported_modalities": [m.value for m in ModalityType],
        }


# Global multi-modal search engine
multimodal_search_engine = MultiModalSearchEngine()

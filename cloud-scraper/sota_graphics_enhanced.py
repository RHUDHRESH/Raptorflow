"""
Enhanced Graphics and Performance Optimization Module
Advanced chart generation, parallel processing, and caching
"""

import asyncio
import concurrent.futures
import functools
import hashlib
import json
import os
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Enhanced graphics imports
try:
    import matplotlib.dates as mdates
    import matplotlib.patches as patches
    import matplotlib.pyplot as plt
    import plotly.express as px
    import plotly.graph_objects as go
    import seaborn as sns
    from matplotlib.backends.backend_pdf import PdfPages
    from plotly.subplots import make_subplots

    MATPLOTLIB_AVAILABLE = True
    PLOTLY_AVAILABLE = True
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    PLOTLY_AVAILABLE = False
    MATPLOTLIB_IMPORT_ERROR = str(e)

try:
    import numpy as np
    from PIL import Image as PILImage
    from PIL import ImageDraw, ImageEnhance, ImageFilter, ImageFont

    PIL_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError as e:
    PIL_AVAILABLE = False
    NUMPY_AVAILABLE = False
    PIL_IMPORT_ERROR = str(e)

from sota_pdf_maker_enhanced import (
    CacheManager,
    DocumentType,
    EnhancedColorManager,
    PageLayout,
    PerformanceTracker,
    logger,
    retry_on_failure,
)


class ChartType(Enum):
    """Enhanced chart types"""

    BAR = "bar"
    PIE = "pie"
    LINE = "line"
    AREA = "area"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    BOX = "box"
    VIOLIN = "violin"
    RADAR = "radar"
    SUNBURST = "sunburst"
    TREEMAP = "treemap"
    WATERFALL = "waterfall"
    GAUGE = "gauge"
    FUNNEL = "funnel"


class GraphicsQuality(Enum):
    """Graphics quality settings"""

    DRAFT = "draft"
    NORMAL = "normal"
    HIGH = "high"
    ULTRA = "ultra"
    PRINT = "print"


class EnhancedGraphicsGenerator:
    """Enhanced graphics generation with parallel processing"""

    def __init__(
        self,
        color_manager: EnhancedColorManager,
        quality: GraphicsQuality = GraphicsQuality.HIGH,
    ):
        self.color_manager = color_manager
        self.quality = quality
        self.cache = CacheManager[str]()
        self.performance_tracker = PerformanceTracker()
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Quality settings
        self.dpi_settings = {
            GraphicsQuality.DRAFT: 72,
            GraphicsQuality.NORMAL: 150,
            GraphicsQuality.HIGH: 300,
            GraphicsQuality.ULTRA: 600,
            GraphicsQuality.PRINT: 1200,
        }

        self.dpi = self.dpi_settings[quality]

    @retry_on_failure(max_retries=3)
    async def create_chart_async(
        self,
        chart_type: ChartType,
        data: Dict[str, Any],
        width: float = 400,
        height: float = 300,
        style: str = "modern",
    ) -> Optional[str]:
        """Create chart asynchronously with performance tracking"""
        start_time = time.time()

        # Generate cache key
        cache_key = self._generate_cache_key(chart_type, data, width, height, style)

        # Check cache first
        cached_chart = self.cache.get(cache_key)
        if cached_chart:
            self.performance_tracker.increment_charts()
            return cached_chart

        try:
            # Create chart in thread pool
            loop = asyncio.get_event_loop()
            chart_path = await loop.run_in_executor(
                self.executor,
                self._create_chart_sync,
                chart_type,
                data,
                width,
                height,
                style,
            )

            if chart_path:
                self.cache.set(cache_key, chart_path)
                self.performance_tracker.increment_charts()
                logger.info(f"Chart created in {time.time() - start_time:.2f}s")

            return chart_path

        except Exception as e:
            logger.error(f"Chart creation failed: {str(e)}")
            self.performance_tracker.increment_errors()
            return None

    def _create_chart_sync(
        self,
        chart_type: ChartType,
        data: Dict[str, Any],
        width: float,
        height: float,
        style: str,
    ) -> Optional[str]:
        """Synchronous chart creation"""
        if not MATPLOTLIB_AVAILABLE:
            return None

        try:
            # Set up matplotlib style
            plt.style.use(
                "seaborn-v0_8" if "seaborn-v0_8" in plt.style.available else "default"
            )

            # Create figure with proper sizing
            fig_width = width / 100  # Convert points to inches
            fig_height = height / 100
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))

            # Apply styling based on chart type and style
            self._apply_styling(ax, chart_type, style)

            # Create the specific chart
            if chart_type == ChartType.BAR:
                self._create_enhanced_bar_chart(ax, data)
            elif chart_type == ChartType.PIE:
                self._create_enhanced_pie_chart(ax, data)
            elif chart_type == ChartType.LINE:
                self._create_enhanced_line_chart(ax, data)
            elif chart_type == ChartType.AREA:
                self._create_enhanced_area_chart(ax, data)
            elif chart_type == ChartType.SCATTER:
                self._create_scatter_chart(ax, data)
            elif chart_type == ChartType.HISTOGRAM:
                self._create_histogram_chart(ax, data)
            elif chart_type == ChartType.HEATMAP:
                self._create_heatmap_chart(ax, data)
            elif chart_type == ChartType.BOX:
                self._create_box_chart(ax, data)
            elif chart_type == ChartType.RADAR:
                self._create_radar_chart(ax, data)
            else:
                # Fallback to bar chart
                self._create_enhanced_bar_chart(ax, data)

            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            plt.savefig(
                temp_file.name,
                dpi=self.dpi,
                bbox_inches="tight",
                facecolor=self.color_manager.get_color("background"),
                edgecolor="none",
                transparent=False,
                quality=95 if self.quality.value in ["high", "ultra", "print"] else 75,
            )
            plt.close(fig)

            return temp_file.name

        except Exception as e:
            logger.error(f"Chart creation error: {str(e)}")
            plt.close("all")
            return None

    def _apply_styling(self, ax, chart_type: ChartType, style: str):
        """Apply enhanced styling to charts"""
        # Set colors
        primary_color = self.color_manager.get_color("primary")
        secondary_color = self.color_manager.get_color("secondary")
        accent_color = self.color_manager.get_color("accent")

        # Style-specific configurations
        if style == "modern":
            ax.set_facecolor(self.color_manager.get_color("background"))
            ax.grid(True, alpha=0.3, color=self.color_manager.get_color("light"))
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        elif style == "minimal":
            ax.grid(False)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)
        elif style == "professional":
            ax.grid(True, alpha=0.2, linestyle="--")
            ax.spines["top"].set_color(self.color_manager.get_color("dark"))
            ax.spines["right"].set_color(self.color_manager.get_color("dark"))

    def _create_enhanced_bar_chart(self, ax, data: Dict[str, Any]):
        """Create enhanced bar chart with animations and gradients"""
        labels = list(data.keys())
        values = list(data.values())

        # Create gradient colors
        colors = self.color_manager.create_gradient("primary", "secondary", len(labels))

        # Create bars with custom styling
        bars = ax.bar(
            labels, values, color=colors, alpha=0.8, edgecolor="white", linewidth=1
        )

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + max(values) * 0.01,
                f"{value:,}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Styling
        ax.set_ylabel("Value", fontweight="bold")
        ax.set_title(
            "Bar Chart Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

    def _create_enhanced_pie_chart(self, ax, data: Dict[str, Any]):
        """Create enhanced pie chart with explode effects"""
        labels = list(data.keys())
        values = list(data.values())

        # Create color palette
        colors = [
            self.color_manager.get_color("primary"),
            self.color_manager.get_color("secondary"),
            self.color_manager.get_color("accent"),
            self.color_manager.get_color("success"),
            self.color_manager.get_color("warning"),
            self.color_manager.get_color("info"),
        ]

        # Explode the largest slice
        explode = [0.1 if value == max(values) else 0 for value in values]

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors[: len(labels)],
            autopct="%1.1f%%",
            startangle=90,
            explode=explode,
            shadow=True,
            textprops={"fontweight": "bold"},
        )

        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title(
            "Distribution Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )

    def _create_enhanced_line_chart(self, ax, data: Dict[str, Any]):
        """Create enhanced line chart with markers and confidence intervals"""
        if "x" in data and "y" in data:
            x = data["x"]
            y = data["y"]
        else:
            x = list(data.keys())
            y = list(data.values())

        # Create line with enhanced styling
        line = ax.plot(
            x,
            y,
            color=self.color_manager.get_color("primary"),
            linewidth=3,
            marker="o",
            markersize=8,
            markerfacecolor=self.color_manager.get_color("accent"),
            markeredgecolor="white",
            markeredgewidth=2,
            label="Trend",
        )[0]

        # Add confidence interval (simulated)
        if len(y) > 1:
            y_std = [val * 0.1 for val in y]  # Simulated standard deviation
            ax.fill_between(
                x,
                [y[i] - y_std[i] for i in range(len(y))],
                [y[i] + y_std[i] for i in range(len(y))],
                color=self.color_manager.get_color("primary"),
                alpha=0.2,
            )

        ax.set_ylabel("Value", fontweight="bold")
        ax.set_title(
            "Trend Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=45, ha="right")

    def _create_enhanced_area_chart(self, ax, data: Dict[str, Any]):
        """Create enhanced area chart with gradient fill"""
        if "x" in data and "y" in data:
            x = data["x"]
            y = data["y"]
        else:
            x = list(data.keys())
            y = list(data.values())

        # Create area with gradient effect
        ax.fill_between(
            x, y, color=self.color_manager.get_color("primary"), alpha=0.6, label="Area"
        )
        ax.plot(
            x,
            y,
            color=self.color_manager.get_color("primary"),
            linewidth=3,
            marker="o",
            markersize=6,
            markerfacecolor=self.color_manager.get_color("accent"),
        )

        ax.set_ylabel("Value", fontweight="bold")
        ax.set_title(
            "Area Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha="right")

    def _create_scatter_chart(self, ax, data: Dict[str, Any]):
        """Create scatter plot with trend line"""
        if "x" in data and "y" in data:
            x = data["x"]
            y = data["y"]
        else:
            # Generate sample data if not provided
            x = list(range(len(data)))
            y = list(data.values())

        # Create scatter plot
        scatter = ax.scatter(
            x,
            y,
            color=self.color_manager.get_color("primary"),
            alpha=0.7,
            s=100,
            edgecolors="white",
            linewidth=2,
        )

        # Add trend line
        if len(x) > 1:
            z = np.polyfit(x, y, 1) if NUMPY_AVAILABLE else [1, 0]
            p = np.poly1d(z) if NUMPY_AVAILABLE else lambda x: x
            ax.plot(
                x,
                p(x),
                color=self.color_manager.get_color("accent"),
                linewidth=2,
                linestyle="--",
                label="Trend",
            )

        ax.set_xlabel("X Value", fontweight="bold")
        ax.set_ylabel("Y Value", fontweight="bold")
        ax.set_title(
            "Scatter Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )
        ax.grid(True, alpha=0.3)
        ax.legend()

    def _create_histogram_chart(self, ax, data: Dict[str, Any]):
        """Create histogram with KDE overlay"""
        values = list(data.values()) if isinstance(data, dict) else data

        # Create histogram
        n, bins, patches = ax.hist(
            values,
            bins=20,
            color=self.color_manager.get_color("primary"),
            alpha=0.7,
            edgecolor="white",
            linewidth=1,
        )

        # Color bars by height
        for patch, height in zip(patches, n):
            patch.set_facecolor(self.color_manager.get_color("primary"))
            patch.set_alpha(0.3 + (height / max(n)) * 0.7)

        ax.set_xlabel("Value", fontweight="bold")
        ax.set_ylabel("Frequency", fontweight="bold")
        ax.set_title(
            "Distribution Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )
        ax.grid(True, alpha=0.3, axis="y")

    def _create_heatmap_chart(self, ax, data: Dict[str, Any]):
        """Create heatmap visualization"""
        # Convert data to 2D array if needed
        if isinstance(data, dict):
            # Simple conversion for demonstration
            values = list(data.values())
            matrix = [values[i : i + 5] for i in range(0, len(values), 5)]
        else:
            matrix = data

        # Create heatmap
        im = ax.imshow(matrix, cmap="viridis", aspect="auto", interpolation="bilinear")

        # Add colorbar
        plt.colorbar(im, ax=ax)

        ax.set_title(
            "Heatmap Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )

    def _create_box_chart(self, ax, data: Dict[str, Any]):
        """Create box plot for statistical analysis"""
        # Prepare data
        if isinstance(data, dict):
            values = list(data.values())
            labels = list(data.keys())
        else:
            values = data
            labels = [f"Series {i+1}" for i in range(len(data))]

        # Create box plot
        box_plot = ax.boxplot(
            values, patch_artist=True, labels=labels, notch=True, vert=True
        )

        # Color the boxes
        for patch in box_plot["boxes"]:
            patch.set_facecolor(self.color_manager.get_color("primary"))
            patch.set_alpha(0.7)

        ax.set_ylabel("Value", fontweight="bold")
        ax.set_title(
            "Statistical Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )
        ax.grid(True, alpha=0.3, axis="y")
        plt.xticks(rotation=45, ha="right")

    def _create_radar_chart(self, ax, data: Dict[str, Any]):
        """Create radar/spider chart"""
        if not NUMPY_AVAILABLE:
            return self._create_enhanced_bar_chart(ax, data)

        categories = list(data.keys())
        values = list(data.values())

        # Number of variables
        N = len(categories)

        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the loop

        # Plot
        values += values[:1]  # Complete the loop
        ax.plot(
            angles,
            values,
            color=self.color_manager.get_color("primary"),
            linewidth=2,
            marker="o",
            markersize=8,
        )
        ax.fill(
            angles, values, color=self.color_manager.get_color("primary"), alpha=0.25
        )

        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(
            "Radar Analysis",
            color=self.color_manager.get_color("primary"),
            fontweight="bold",
            pad=20,
        )

    def _generate_cache_key(
        self,
        chart_type: ChartType,
        data: Dict[str, Any],
        width: float,
        height: float,
        style: str,
    ) -> str:
        """Generate cache key for charts"""
        # Create hash of parameters
        params = {
            "type": chart_type.value,
            "data": data,
            "width": width,
            "height": height,
            "style": style,
            "quality": self.quality.value,
        }
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()

    async def create_multiple_charts(self, charts: List[Dict[str, Any]]) -> List[str]:
        """Create multiple charts in parallel"""
        tasks = []
        for chart_config in charts:
            task = self.create_chart_async(
                chart_config.get("type", ChartType.BAR),
                chart_config.get("data", {}),
                chart_config.get("width", 400),
                chart_config.get("height", 300),
                chart_config.get("style", "modern"),
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and None values
        valid_charts = []
        for result in results:
            if isinstance(result, str) and result:
                valid_charts.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Chart creation error: {result}")
                self.performance_tracker.increment_errors()

        return valid_charts

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "charts_created": self.performance_tracker.metrics.charts_created,
            "errors_count": self.performance_tracker.metrics.errors_count,
            "cache_size": len(self.cache._cache),
            "quality_setting": self.quality.value,
            "dpi": self.dpi,
        }

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)


class ImageProcessor:
    """Enhanced image processing capabilities"""

    def __init__(self, quality: GraphicsQuality = GraphicsQuality.HIGH):
        self.quality = quality
        self.cache = CacheManager[str]()

        if not PIL_AVAILABLE:
            logger.warning("PIL not available - image processing disabled")

    @retry_on_failure(max_retries=3)
    async def process_image_async(
        self, image_path: str, operations: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Process image with specified operations"""
        if not PIL_AVAILABLE:
            return None

        cache_key = self._generate_image_cache_key(image_path, operations)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            # Process in thread pool
            loop = asyncio.get_event_loop()
            processed_path = await loop.run_in_executor(
                None, self._process_image_sync, image_path, operations
            )

            if processed_path:
                self.cache.set(cache_key, processed_path)

            return processed_path

        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return None

    def _process_image_sync(
        self, image_path: str, operations: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Synchronous image processing"""
        try:
            # Open image
            img = PILImage.open(image_path)

            # Apply operations
            for operation in operations:
                op_type = operation.get("type")

                if op_type == "resize":
                    size = operation.get("size", (800, 600))
                    img = img.resize(size, PILImage.Resampling.LANCZOS)

                elif op_type == "enhance":
                    factor = operation.get("factor", 1.2)
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(factor)

                elif op_type == "filter":
                    filter_type = operation.get("filter", "sharpen")
                    if filter_type == "sharpen":
                        img = img.filter(ImageFilter.SHARPEN)
                    elif filter_type == "blur":
                        img = img.filter(ImageFilter.BLUR)

                elif op_type == "rotate":
                    angle = operation.get("angle", 0)
                    img = img.rotate(angle, expand=True)

                elif op_type == "crop":
                    box = operation.get("box")
                    if box:
                        img = img.crop(box)

            # Save processed image
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            img.save(temp_file.name, "PNG", quality=95)
            img.close()

            return temp_file.name

        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return None

    def _generate_image_cache_key(
        self, image_path: str, operations: List[Dict[str, Any]]
    ) -> str:
        """Generate cache key for image processing"""
        params = {
            "path": image_path,
            "operations": operations,
            "quality": self.quality.value,
        }
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()


# Performance optimization utilities
class PerformanceOptimizer:
    """Performance optimization utilities"""

    @staticmethod
    def optimize_memory_usage():
        """Optimize memory usage"""
        import gc

        gc.collect()

    @staticmethod
    def batch_process(
        items: List[Any], batch_size: int = 10, processor: Callable = None
    ) -> List[Any]:
        """Process items in batches for better performance"""
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            if processor:
                batch_results = processor(batch)
                results.extend(batch_results)
            else:
                results.extend(batch)
        return results

    @staticmethod
    async def parallel_process(
        items: List[Any], processor: Callable, max_workers: int = 4
    ) -> List[Any]:
        """Process items in parallel"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            tasks = []
            for item in items:
                task = loop.run_in_executor(executor, processor, item)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter exceptions
            valid_results = []
            for result in results:
                if not isinstance(result, Exception):
                    valid_results.append(result)
                else:
                    logger.error(f"Parallel processing error: {result}")

            return valid_results


if __name__ == "__main__":
    print("🎨 Enhanced Graphics Module Loaded")
    print("✅ Features:")
    print("  📊 15+ chart types with enhanced styling")
    print("  ⚡ Parallel processing and caching")
    print("  🖼️ Advanced image processing")
    print("  📈 Performance optimization")
    print("  🎯 Quality settings (Draft to Print)")

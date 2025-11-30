import time
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.extractors.pdf_engine import PDFExtractorV2
from backend.services.extractors.image_engine import ImageExtractorV2
from backend.services.extractors.url_engine import URLExtractorV2

async def benchmark_engine(engine, input_data, name, iterations=1):
    print(f"Running {name} x{iterations}...")
    start = time.time()
    success_count = 0
    for i in range(iterations):
        try:
            result = await engine.extract(input_data, {})
            if "error" not in result:
                success_count += 1
        except Exception as e:
            print(f"  Error in iteration {i}: {e}")
            
    end = time.time()
    total_time = end - start
    avg_time = total_time / iterations
    
    print(f"  Total Time: {total_time:.4f}s")
    print(f"  Avg Time:   {avg_time:.4f}s")
    print(f"  Success:    {success_count}/{iterations}")
    print("-" * 30)

async def main():
    print("=== INTELLIGENCE ENGINE BENCHMARK ===")
    
    # Initialize Engines
    pdf_engine = PDFExtractorV2()
    image_engine = ImageExtractorV2()
    url_engine = URLExtractorV2()
    
    # 1. URL Benchmark
    # We use a reliable public URL
    url = "https://www.example.com"
    print(f"\n[URL ENGINE] Target: {url}")
    await benchmark_engine(url_engine, url, "Trafilatura", 5)
    
    # 2. PDF Benchmark
    # Check for sample
    pdf_path = "backend/tests/samples/benchmark.pdf"
    if os.path.exists(pdf_path):
        print(f"\n[PDF ENGINE] Target: {pdf_path}")
        await benchmark_engine(pdf_engine, pdf_path, "PDFPlumber", 5)
    else:
        print(f"\n[PDF ENGINE] Skipped (Sample not found at {pdf_path})")
        print("To run PDF benchmark, place a sample PDF at backend/tests/samples/benchmark.pdf")

    # 3. Image Benchmark
    image_path = "backend/tests/samples/benchmark.jpg"
    if os.path.exists(image_path):
        print(f"\n[IMAGE ENGINE] Target: {image_path}")
        await benchmark_engine(image_engine, image_path, "PaddleOCR", 5)
    else:
        print(f"\n[IMAGE ENGINE] Skipped (Sample not found at {image_path})")
        print("To run Image benchmark, place a sample JPG at backend/tests/samples/benchmark.jpg")

if __name__ == "__main__":
    asyncio.run(main())

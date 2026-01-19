import asyncio
import sys
sys.path.append('.')
from backend.memory.controller import SimpleMemoryController

async def run_basic_tests():
    controller = SimpleMemoryController()
    
    print("Testing basic memory operations...")
    
    # Test storage and retrieval
    result = await controller.store_memory("test", {"data": "value"})
    print(f"Store result: {result}")
    
    retrieved = await controller.retrieve_memory("test")
    print(f"Retrieved: {retrieved}")
    
    # Test health check
    health = await controller.health_check()
    print(f"Health status: {health['status']}")
    
    # Test stats
    stats = await controller.get_memory_stats()
    print(f"Total operations: {stats['total_operations']}")
    print(f"Error rate: {stats.get('error_rate', 0):.2f}%")
    
    # Test vector operations
    vector_id = await controller.store_vector("test text", [0.1, 0.2, 0.3])
    print(f"Vector stored with ID: {vector_id}")
    
    # Test vector search
    search_results = await controller.search_vectors([0.1, 0.2, 0.3])
    print(f"Vector search results: {len(search_results)} items")
    
    print("Basic tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_basic_tests())

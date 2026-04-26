"""
Test script to verify Groq API connection.
Run this before deploying to Render.com
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.core.llm_client import GroqClient


async def test_groq():
    """Test Groq API connection and generation."""
    print("🧪 Testing Groq Client...")
    print("=" * 60)
    
    # Create client
    client = GroqClient()
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    is_healthy = await client.health_check()
    if is_healthy:
        print("✅ Groq API is accessible!")
    else:
        print("❌ Cannot reach Groq API")
        print("   Check your GROQ_API_KEY in .env")
        return
    
    # Test 2: Simple generation
    print("\n2️⃣ Testing text generation...")
    prompt = "Say hello in one sentence."
    print(f"Prompt: {prompt}")
    response = await client.generate(prompt)
    print(f"Response: {response}")
    
    # Test 3: Product search query optimization
    print("\n3️⃣ Testing query optimization...")
    prompt = """
Improve this product search query to be more specific:

Original query: "car"
Budget: $10,000

Return only the improved query, nothing else.
"""
    print("Optimizing query...")
    response = await client.generate(prompt, temperature=0.3)
    print(f"Improved query: {response}")
    
    # Test 4: JSON generation
    print("\n4️⃣ Testing JSON generation...")
    prompt = """
Analyze this search performance and return JSON:

Total products found: 50
Products matching threshold: 5
Match rate: 10%

Return JSON with these fields:
{
    "should_adjust_threshold": true/false,
    "suggested_threshold": number,
    "reasoning": "explanation"
}
"""
    print("Generating JSON...")
    result = await client.generate_json(prompt)
    print(f"JSON result: {result}")
    
    # Test 5: Speed test
    print("\n5️⃣ Testing speed...")
    import time
    start = time.time()
    await client.generate("Count to 5")
    elapsed = time.time() - start
    print(f"⚡ Response time: {elapsed:.2f} seconds")
    print(f"   (Groq is typically 0.5-1s - very fast!)")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Groq is working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_groq())
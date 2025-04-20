import asyncio
from utils.stackoverflow import search_stackoverflow
import json

async def main():
    # Test query
    test_query = "redis database"
    
    print("Testing Stack Overflow API...")
    print(f"Query: {test_query}")
    
    # Call the search function
    answer, sources = await search_stackoverflow(test_query)
    
    print("\nResults:")
    print("=" * 50)
    print("Answer:")
    if answer:
        print(answer)
    else:
        print("No answer content received")
    print("\nSources:")
    for source in sources:
        print(f"- {source}")
    
    # Print raw response for debugging
    print("\nDebug Info:")
    print("-" * 50)
    print(f"Answer length: {len(answer) if answer else 0} characters")
    print(f"Number of sources: {len(sources)}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 
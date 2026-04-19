"""
Manual script to trigger a search execution for testing.
"""
import asyncio
from app.database import SessionLocal
from app.models.search_request import SearchRequest
from app.core.orchestrator import SearchOrchestrator

async def main():
    db = SessionLocal()
    
    # Get the Lenovo search
    search = db.query(SearchRequest).filter(
        SearchRequest.product_name == "Lenovo ThinkPad P1 Gen5 Intel i7-12th"
    ).first()
    
    if not search:
        print("Search not found!")
        db.close()
        return
    
    print(f"Triggering search: {search.product_name}")
    print(f"Search ID: {search.id}")
    
    # Create orchestrator and run search
    orchestrator = SearchOrchestrator(db)
    execution = await orchestrator.execute_search(search)
    
    print(f"\nExecution completed!")
    print(f"Execution ID: {execution.id}")
    print(f"Status: {execution.status}")
    print(f"Products found: {execution.products_found}")
    print(f"Matches found: {execution.matches_found}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob

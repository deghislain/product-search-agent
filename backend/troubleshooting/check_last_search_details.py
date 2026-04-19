from app.database import SessionLocal
from app.models.search_execution import SearchExecution
from app.models.search_request import SearchRequest

db = SessionLocal()

# Get the latest execution
latest_exec = db.query(SearchExecution).order_by(
    SearchExecution.started_at.desc()
).first()

if latest_exec:
    print(f'Latest Execution Details:')
    print(f'  ID: {latest_exec.id}')
    print(f'  Status: {latest_exec.status}')
    print(f'  Started: {latest_exec.started_at}')
    print(f'  Completed: {latest_exec.completed_at}')
    print(f'  Products found: {latest_exec.products_found}')
    print(f'  Matches found: {latest_exec.matches_found}')
    print(f'  Error: {latest_exec.error_message}')
    
    # Get the search request
    search = db.query(SearchRequest).filter(
        SearchRequest.id == latest_exec.search_request_id
    ).first()
    
    if search:
        print(f'\nSearch Request:')
        print(f'  Product: {search.product_name}')
        print(f'  Craigslist: {search.search_craigslist}')
        print(f'  eBay: {search.search_ebay}')
        print(f'  Facebook: {search.search_facebook}')
        print(f'  Location: {search.location}')

db.close()

# Made with Bob

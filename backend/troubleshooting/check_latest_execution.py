from app.database import SessionLocal
from app.models.search_execution import SearchExecution
from app.models.product import Product
from datetime import datetime

db = SessionLocal()

search_id = 'b44e2749-ab73-40da-a6cb-4fe05a22476a'

# Get latest execution
recent = db.query(SearchExecution).filter(
    SearchExecution.search_request_id == search_id
).order_by(SearchExecution.started_at.desc()).first()

if recent:
    print(f'Latest execution: {recent.id}')
    print(f'Started at: {recent.started_at}')
    print(f'Status: {recent.status}')
    print(f'Products found: {recent.products_found}')
    print(f'Matches found: {recent.matches_found}')
    
    minutes_ago = (datetime.now() - recent.started_at).total_seconds() / 60
    print(f'Time ago: {minutes_ago:.1f} minutes')
    
    # Check if products exist with this execution_id
    products = db.query(Product).filter(
        Product.search_execution_id == recent.id
    ).all()
    print(f'\nProducts with this execution_id: {len(products)}')
    
    if products:
        print(f'First product: {products[0].title[:50]}')
        print(f'  is_match: {products[0].is_match}')
else:
    print('No executions found for this search')

db.close()

# Made with Bob

from app.database import SessionLocal
from app.models.product import Product
from app.models.search_execution import SearchExecution
from app.models.search_request import SearchRequest

db = SessionLocal()

# Check the execution that has products
exec_id = '857fc6cf-5def-4db7-ac59-a413878a3d8c'
execution = db.query(SearchExecution).filter(SearchExecution.id == exec_id).first()

if execution:
    search = db.query(SearchRequest).filter(
        SearchRequest.id == execution.search_request_id
    ).first()
    
    print(f'Execution {exec_id}:')
    print(f'  Belongs to search: {search.product_name if search else "Unknown"}')
    print(f'  Search ID: {execution.search_request_id}')
    print(f'  Search status: {search.status if search else "Unknown"}')
    
    # Count products
    products = db.query(Product).filter(
        Product.search_execution_id == exec_id
    ).all()
    print(f'  Products: {len(products)}')
    matches = [p for p in products if p.is_match]
    print(f'  Matches: {len(matches)}')

print('\n' + '='*50)
print('All active searches:')
active_searches = db.query(SearchRequest).filter(
    SearchRequest.status == 'active'
).all()

for search in active_searches:
    print(f'\n{search.product_name}:')
    print(f'  ID: {search.id}')
    
    # Get latest execution
    execs = db.query(SearchExecution).filter(
        SearchExecution.search_request_id == search.id
    ).order_by(SearchExecution.started_at.desc()).limit(1).all()
    
    if execs:
        latest = execs[0]
        products = db.query(Product).filter(
            Product.search_execution_id == latest.id
        ).all()
        matches = [p for p in products if p.is_match]
        print(f'  Latest execution: {latest.id}')
        print(f'  Products: {len(products)}')
        print(f'  Matches: {len(matches)}')

db.close()

# Made with Bob

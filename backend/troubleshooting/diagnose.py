from app.database import SessionLocal
from app.models.search_request import SearchRequest
from app.models.search_execution import SearchExecution
from app.models.product import Product

db = SessionLocal()

# Check searches
searches = db.query(SearchRequest).all()
print(f'Total searches: {len(searches)}')

active = [s for s in searches if s.status == 'active']
print(f'Active searches: {len(active)}')

if active:
    s = active[0]
    print(f'\nFirst active search: {s.product_name}')
    print(f'ID: {s.id}')
    
    # Check executions
    execs = db.query(SearchExecution).filter(
        SearchExecution.search_request_id == s.id
    ).all()
    print(f'Executions: {len(execs)}')
    
    if execs:
        e = execs[-1]
        print(f'\nLatest execution:')
        print(f'  ID: {e.id}')
        print(f'  Status: {e.status}')
        print(f'  Products found: {e.products_found}')
        print(f'  Matches found: {e.matches_found}')
        
        # Check products
        prods = db.query(Product).filter(
            Product.search_execution_id == e.id
        ).all()
        print(f'  Products in DB with this exec_id: {len(prods)}')
        
        if prods:
            print(f'\n  First product:')
            print(f'    Title: {prods[0].title[:50]}')
            print(f'    is_match: {prods[0].is_match}')
            print(f'    match_score: {prods[0].match_score}')
    else:
        print('No executions found for this search')
else:
    print('No active searches found')

# Check all products
all_products = db.query(Product).all()
print(f'\nTotal products in database: {len(all_products)}')

matches = db.query(Product).filter(Product.is_match == True).all()
print(f'Total matches: {len(matches)}')

db.close()

# Made with Bob

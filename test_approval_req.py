from fastapi.testclient import TestClient
from combined_app import create_combined_app
app = create_combined_app()
client = TestClient(app)

# Try creating without approval_criteria - should be 422 from FastAPI because Form(...) missing
r = client.post('/api/categories/', data={'categoryname': 'NOCRIT', 'categorydescription': 'desc'})
print('create missing criteria status:', r.status_code)
print('create missing criteria body:', r.text)

# Create with criteria - should succeed
r2 = client.post('/api/categories/', data={'categoryname': 'WITHCRIT', 'categorydescription': 'desc', 'approval_criteria':'must approve'})
print('create with criteria status:', r2.status_code, r2.json())

# Update: create one then try update without approval_criteria - expect 422
cid = r2.json()['id']
r3 = client.patch(f'/api/categories/{cid}', data={'categorydescription': 'new desc'})
print('update missing criteria status:', r3.status_code, r3.text)

# Update with criteria - should succeed
r4 = client.patch(f'/api/categories/{cid}', data={'approval_criteria': 'updated crit', 'comments':'ok'})
print('update with criteria status:', r4.status_code, r4.json())

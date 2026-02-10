import requests

try:
    response = requests.get('http://localhost:8000/products/filter?category_id=1&limit=10')
    print('Status:', response.status_code)
    if response.status_code == 200:
        data = response.json()
        print('Products returned:', len(data))
        if data:
            print('First product:', data[0])
            print('Category info:', data[0].get('category'))
            print('All product IDs:', [p['id'] for p in data])
    else:
        print('Error:', response.text)
except Exception as e:
    print('Connection error:', e)

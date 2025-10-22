import requests

response = requests.get('http://localhost:8000/scores', timeout=10)
print(f'Status: {response.status_code}')
data = response.json()
print(f'Records: {len(data)}')
print(f'First record: {data[0]}')
# Member B CSV Data Endpoints

This document describes the endpoints created for Member B to access CSV data from the data folder. **Important**: The dataset contains 10,000 records, so we use pagination to prevent API timeouts.

## New Endpoints

### 1. Get CSV Data Info
**GET** `/v1/ml/data/info`

Returns metadata about the CSV data file without loading all data.

**Response:**
```json
{
  "status": "success",
  "file_path": "/path/to/data/base_txns_10k_ml_slim.csv",
  "file_size_bytes": 1234567,
  "file_size_mb": 1.18,
  "columns": ["idx", "step", "amount", "isFraud", ...],
  "column_count": 12
}
```

### 2. Get CSV Data Sample
**GET** `/v1/ml/data/sample?limit=100`

Returns a limited number of records from the CSV file for testing purposes.

**Parameters:**
- `limit` (optional): Number of records to return (default: 100, max: 10000)

**Response:**
```json
{
  "status": "success",
  "file_path": "/path/to/data/base_txns_10k_ml_slim.csv",
  "limit": 100,
  "count": 100,
  "columns": ["idx", "step", "amount", "isFraud", ...],
  "data": [
    {
      "idx": 1951391,
      "step": 323,
      "amount": 128939.17,
      "isFraud": 0,
      ...
    }
  ]
}
```

### 3. Get CSV Data (Paginated) ⭐ **RECOMMENDED**
**GET** `/v1/ml/data?limit=1000&offset=0`

Returns CSV data with pagination support to handle large datasets safely.

**Parameters:**
- `limit` (optional): Number of records to return (default: 1000, max: 10000)
- `offset` (optional): Number of records to skip (default: 0)

**Response:**
```json
{
  "status": "success",
  "file_path": "/path/to/data/base_txns_10k_ml_slim.csv",
  "count": 1000,
  "total_count": 10000,
  "limit": 1000,
  "offset": 0,
  "has_more": true,
  "columns": ["idx", "step", "amount", "isFraud", ...],
  "data": [
    // 1000 records
  ]
}
```

### 4. Get Chunk Information
**GET** `/v1/ml/data/chunks?chunk_size=1000`

Returns information about how to paginate through all data.

**Parameters:**
- `chunk_size` (optional): Size of each chunk (default: 1000, max: 10000)

**Response:**
```json
{
  "status": "success",
  "file_path": "/path/to/data/base_txns_10k_ml_slim.csv",
  "total_count": 10000,
  "chunk_size": 1000,
  "total_chunks": 10,
  "instructions": {
    "message": "Use /v1/ml/data with limit and offset parameters to get chunks",
    "example_urls": [
      "/v1/ml/data?limit=1000&offset=0",
      "/v1/ml/data?limit=1000&offset=1000",
      "/v1/ml/data?limit=1000&offset=2000"
    ]
  }
}
```

### 5. Run ML Detection on CSV Data
**POST** `/v1/ml/detect-from-csv`

Runs the full ML anomaly detection pipeline directly on the CSV data from the data folder.

**Response:**
```json
{
  "status": "success",
  "file_path": "/path/to/data/base_txns_10k_ml_slim.csv",
  "count": 10000,
  "results": [
    {
      "transaction_id": 1951391,
      "anomaly_score": 0.123,
      "risk_score": 0.456,
      "is_anomaly": false,
      ...
    }
  ],
  "models_used": ["IsolationForest", "OneClassSVM", "XGBoost"]
}
```

## Usage Examples

### Getting All Data Safely (Recommended Approach):

```bash
# Step 1: Get chunk information
curl "http://localhost:8001/v1/ml/data/chunks?chunk_size=1000"

# Step 2: Get data in chunks
curl "http://localhost:8001/v1/ml/data?limit=1000&offset=0"    # Records 1-1000
curl "http://localhost:8001/v1/ml/data?limit=1000&offset=1000" # Records 1001-2000
curl "http://localhost:8001/v1/ml/data?limit=1000&offset=2000" # Records 2001-3000
# ... continue until you have all data
```

### Using Python requests for pagination:

```python
import requests

def get_all_csv_data():
    """Get all CSV data using pagination"""
    base_url = "http://localhost:8001/v1/ml/data"
    all_data = []
    
    # Get chunk info first
    chunk_info = requests.get("http://localhost:8001/v1/ml/data/chunks").json()
    chunk_size = chunk_info["chunk_size"]
    total_count = chunk_info["total_count"]
    
    # Get data in chunks
    offset = 0
    while offset < total_count:
        response = requests.get(f"{base_url}?limit={chunk_size}&offset={offset}")
        chunk_data = response.json()
        all_data.extend(chunk_data["data"])
        
        if not chunk_data["has_more"]:
            break
            
        offset += chunk_size
    
    return all_data

# Get all data
all_data = get_all_csv_data()
print(f"Retrieved {len(all_data)} records")
```

### Quick Testing:

```bash
# Get data info (fast)
curl http://localhost:8001/v1/ml/data/info

# Get small sample (fast)
curl "http://localhost:8001/v1/ml/data/sample?limit=10"

# Get all 10,000 records at once (moderate)
curl "http://localhost:8001/v1/ml/data?limit=10000"

# Get first chunk (moderate)
curl "http://localhost:8001/v1/ml/data?limit=1000&offset=0"

# Run ML detection (slow - processes all 10k records)
curl -X POST http://localhost:8001/v1/ml/detect-from-csv
```

## Testing

Run the test script to verify all endpoints work:

```bash
python test_csv_endpoints.py
```

Make sure the API server is running first:

```bash
python api/unified_app.py
```

## Important Notes

- **You can now get all 10,000 records** in a single request if needed
- **Use pagination** with `limit` and `offset` parameters for better performance with large datasets
- **Sample endpoint** supports up to 10,000 records (full dataset)
- **Main data endpoint** supports up to 10,000 records per request (full dataset)
- All endpoints automatically handle JSON serialization of pandas DataFrames
- NaN and infinite values are converted to null for JSON compatibility
- The ML detection endpoint processes all data but may take time to complete
- File paths are resolved relative to the project root directory

# 🚀 Quick Start Guide - Integrated Fraud Detection System

This guide will get you up and running with the integrated fraud detection system combining Member A and Member B's work in **5 minutes**.

## ✅ Prerequisites

- Python 3.11 or higher
- pip package manager
- 150MB free disk space

## 📦 Installation

### Step 1: Navigate to the Project
```bash
cd "Fraud-Detection"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- **Member A dependencies**: FastAPI, NetworkX, pandas
- **Member B dependencies**: scikit-learn, XGBoost, SHAP
- **Testing tools**: pytest, httpx

---

## 🎯 Quick Demo (Fastest Way)

Run the integrated demo script that executes both Member A and B's code:

```bash
python scripts/demo_integrated.py
```

This will:
1. ✅ Run Member B's ML anomaly detection
2. ✅ Run Member A's graph analysis
3. ✅ Merge results and show integrated output
4. ✅ Generate all output files

**Output Files:**
- `models/ml_scores.csv` - Member B's ML scores
- `models/anomaly_output_standard.json` - Member B's detailed results
- `outputs/graph_scores.json` - Member A's graph scores
- `outputs/integrated_results.csv` - **Combined results (ready for demo!)**

---

## 🌐 Running the APIs

### Option 1: Unified API (Recommended for Demo)

**Single command to run everything:**
```bash
uvicorn api.unified_app:app --reload --port 8001
```

Then open your browser:
- **Swagger UI**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

**Test the unified endpoint:**
```bash
curl -X POST "http://localhost:8001/v1/unified/score" \
  -H "Content-Type: application/json" \
  -d @tests/better_test_data.json
```

### Option 2: Member A's API Only
```bash
uvicorn api.unified_app:app --reload --port 8001
```

### Option 3: Member B's API Only
```bash
python scripts/memberB_api.py
```

### Option 4: Both APIs Separately (Microservices)
```bash
# Terminal 1: Member A
uvicorn api.unified_app:app --reload --port 8001

# Terminal 2: Member B
python scripts/memberB_api.py
```

---

## 🧪 Testing

### Test Member A (Graph Analysis)
```bash
# Using pytest
pytest tests/test_api.py

# Using curl
curl -X POST "http://localhost:8001/v1/graph/score" \
  -H "Content-Type: application/json" \
  -d @tests/better_test_data.json
```

### Test Member B (ML Detection)
```bash
# Run standalone detection
python scripts/run_detection.py

# Test API endpoint
curl -X POST "http://localhost:8001/v1/ml/detect-from-transactions" \
  -H "Content-Type: application/json" \
  -d @tests/better_test_data.json
```

---

## 📊 Available Endpoints

### Member A: Graph Analysis
| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `POST /v1/graph/score` | Batch graph scoring |
| `POST /v1/graph/precision` | Detailed 7d/30d analysis |

### Member B: ML Detection
| Endpoint | Description |
|----------|-------------|
| `POST /v1/ml/detect` | ML detection from CSV file |
| `POST /v1/ml/detect-from-transactions` | ML detection from JSON |
| `POST /run-agentB` | Legacy endpoint |

### Unified (Both A & B)
| Endpoint | Description |
|----------|-------------|
| `POST /v1/unified/score` | Combined graph + ML analysis |

---

## 💡 Usage Examples

### Python Example
```python
import requests
import pandas as pd

# Load test data
df = pd.read_csv("tests/better_test_data.json")
transactions = df.to_dict(orient='records')

# Call unified endpoint
response = requests.post(
    "http://localhost:8001/v1/unified/score",
    json={
        "transactions": transactions,
        "run_ml_detection": True,
        "run_graph_analysis": True
    }
)

# Get integrated results
results = response.json()
integrated_df = pd.DataFrame(results["integrated_results"])

# Display scores
print(integrated_df[["idx", "ring_score_7d", "ml_score", "amount"]].head())
```

### Direct Script Usage
```python
# Member B: Run ML detection
from scripts import run_detection
run_detection.main()  # Generates models/ml_scores.csv

# Member A: Run graph scoring
from src.graph_scoring import score_batch
import pandas as pd

df = pd.read_csv("data/transactions.csv")
results = score_batch(df)
```

---

## 📁 Project Structure

```
Fraud-Detection/
├── api/
│   ├── app.py              # Member A API
│   └── unified_app.py      # Unified API (both A & B)
├── src/
│   ├── graph_scoring.py    # Member A: Graph scoring
│   └── precision_scoring.py # Member A: Precision analysis
├── agents/
│   └── anomaly_detector.py # Member B: ML models
├── scripts/
│   ├── run_detection.py    # Member B: Main script
│   ├── memberB_api.py      # Member B: API wrapper
│   └── demo_integrated.py  # Integrated demo
├── data/                   # Input data
├── models/                 # Member B outputs
├── outputs/                # Member A outputs + integrated
├── tests/                  # Test data and scripts
└── docs/                   # Documentation
```

---

## 🎬 Demo Flow

### For Presentation/Demo:

1. **Show the integrated system:**
   ```bash
   python scripts/demo_integrated.py
   ```

2. **Start unified API:**
   ```bash
   uvicorn api.unified_app:app --reload --port 8001
   ```

3. **Open Swagger UI:**
   - Navigate to: http://localhost:8001/docs
   - Show the endpoints organized by Member A, B, and Unified

4. **Test unified endpoint:**
   - Use the `/v1/unified/score` endpoint in Swagger UI
   - Upload test data from `tests/better_test_data.json`
   - Show integrated results with both graph and ML scores

5. **Show output files:**
   - `outputs/integrated_results.csv` - Combined results
   - `outputs/fraud_ring_7d.html` - Network visualization (if generated)
   - `models/ml_scores.csv` - ML scores with SHAP features

---

## 🔧 Troubleshooting

### Issue: "Module not found"
```bash
# Make sure you're in the right directory
cd Fraud-Detection

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port already in use"
```bash
# Use a different port
uvicorn api.unified_app:app --reload --port 8002
```

### Issue: "Data file not found"
```bash
# The demo will create sample data automatically
# Or place your CSV file in the data/ folder
```

### Issue: Import errors
```bash
# Make sure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows
```

---

## 📚 Next Steps

- **Read full documentation**: See `README.md` for complete details
- **API reference**: See `docs/api.md` for all endpoints
- **Architecture**: See `docs/architecture.md` for system design
- **Team handoff**: See `TEAM_HANDOFF.md` for integration with Members C & D

---

## 🆘 Need Help?

1. Check the [documentation](docs/)
2. Review [test examples](tests/)
3. Look at the [demo script](scripts/demo_integrated.py)
4. Open an issue in the repository

---

**🎉 You're ready to demo! The integrated system combines both Member A and Member B's work seamlessly.**





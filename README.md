# Integrated Fraud Detection System (Members A & B)

Production-ready FastAPI service combining **Graph-based Fraud Ring Detection** (Member A) and **ML Anomaly Detection** (Member B) for comprehensive fraud analysis.

## 🚀 Features

### Member A: Graph & Link Analysis
- **FAST Batch Scoring**: High-performance batch processing with global graph features
- **Precision Analysis**: Detailed 7-day vs 30-day subgraph analysis for suspicious transactions
- **Network Analysis**: PageRank, community detection, and motif identification

### Member B: ML Anomaly Detection
- **Multi-Model Ensemble**: Isolation Forest + One-Class SVM + XGBoost
- **Explainable AI**: SHAP-based feature importance and explanations
- **Supervised Learning**: XGBoost classifier with train/test evaluation
- **Standardized Output**: JSON and CSV export for team integration

### System Integration
- **Real-time API**: RESTful endpoints for seamless integration
- **Unified Pipeline**: Both agents work together on the same data
- **Production Ready**: Docker support, comprehensive testing, and documentation

## 📋 API Endpoints

### Member A: Graph Analysis Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/v1/graph/score` | POST | Batch FAST scoring for transactions |
| `/v1/graph/precision` | POST | Detailed analysis for single transaction |

### Member B: ML Anomaly Detection Endpoint
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/run-agentB` | POST | Run full ML anomaly detection pipeline |

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────┐
                    │      Raw Transaction Data           │
                    │         (CSV/JSON)                  │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │                                     │
         ┌──────────▼──────────┐           ┌────────────▼─────────┐
         │   Member A:          │           │   Member B:          │
         │ Graph & Link Agent   │           │ ML Anomaly Detector  │
         │  (NetworkX Graph)    │           │ (IF/SVM/XGBoost)     │
         └──────────┬───────────┘           └────────────┬─────────┘
                    │                                     │
         ┌──────────▼──────────┐           ┌────────────▼─────────┐
         │ - ring_score_7d     │           │ - ml_score           │
         │ - ring_score_30d    │           │ - ml_supervised      │
         │ - component_size    │           │ - anomaly_score      │
         │ - pagerank          │           │ - SHAP features      │
         └──────────┬───────────┘           └────────────┬─────────┘
                    │                                     │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │     Integrated Results              │
                    │   (Ready for Members C & D)         │
                    │  - Verifier Agent                   │
                    │  - UI/Dashboard/Alerts              │
                    └─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd fraud-detection

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Services

#### Option 1: Run Member A's Graph Analysis API
```bash
# Start Member A's API server (Graph & Link Analysis)
uvicorn api.unified_app:app --reload --port 8001

# Open API documentation
# http://127.0.0.1:8001/docs
```

#### Option 2: Run Member B's ML Detection API
```bash
# Start Member B's API server (ML Anomaly Detection)
python scripts/memberB_api.py

# API runs on port 8001
# http://127.0.0.1:8001/docs
```

#### Option 3: Run Both Together (Recommended for Demo)
```bash
# Terminal 1: Start Member A's Graph API
uvicorn api.unified_app:app --reload --port 8001

# Terminal 2: Start Member B's Detection API
python scripts/memberB_api.py --port 8002

# Or run Member B's detection standalone
python scripts/run_detection.py
```

### Testing
```bash
# Run unit tests
pytest

# Test API endpoints
curl -X POST "http://127.0.0.1:8001/v1/graph/score" \
  -H "Content-Type: application/json" \
  -d @tests/better_test_data.json
```

## 📁 Project Structure

```
fraud-detection/
├── api/                    # Member A: FastAPI application
│   └── app.py            # Graph & Link Analysis API
├── src/                   # Member A: Core scoring modules
│   ├── graph_scoring.py  # FAST batch scoring
│   └── precision_scoring.py # 7d/30d temporal analysis
├── agents/                # Member B: ML agents
│   ├── __init__.py       # Package initialization
│   └── anomaly_detector.py # IF/SVM/XGBoost ensemble
├── scripts/               # Member B: Execution scripts
│   ├── run_detection.py  # Main detection pipeline
│   ├── memberB_api.py    # Member B's API wrapper
│   └── export_ml_scores.py # JSON to CSV exporter
├── data/                  # Input data directory
│   └── (place CSV files here)
├── models/                # Output models and scores
│   ├── anomaly_output_standard.json # ML results
│   └── ml_scores.csv     # Formatted scores
├── tests/                 # Test suite
│   ├── test_api.py       # API tests
│   ├── sample_request.json # Basic test data
│   ├── better_test_data.json # Extended test data
│   └── fraud_ring_scenario.json # Fraud pattern test
├── docs/                  # Documentation
│   ├── api.md            # API reference
│   ├── architecture.md   # System architecture
│   └── responsible_ai.md # AI ethics guidelines
├── outputs/               # Demo artifacts & visualizations
│   ├── sample_graph_score.json
│   ├── ring_scores_window.csv
│   ├── fraud_ring_7d.html
│   └── fraud_ring_30d.html
├── notebooks/             # Jupyter notebooks
│   ├── Fraud_Detection_AI.ipynb # Main analysis
│   └── visualize_anomalies.ipynb # Visualization
├── requirements.txt       # Python dependencies (both members)
├── Dockerfile            # Container configuration
├── Makefile              # Development commands
├── setup.py              # Package setup
├── TEAM_HANDOFF.md       # Integration guide
└── README.md             # This file
```

## 🧪 Testing

### Test Data
- **Basic**: `tests/sample_request.json` - Simple 2-transaction test
- **Extended**: `tests/better_test_data.json` - 8 transactions, same receiver
- **Fraud Ring**: `tests/fraud_ring_scenario.json` - Classic fraud pattern

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_api.py

# With coverage
pytest --cov=src --cov=api
```

## 🐳 Docker

```bash
# Build image
docker build -t fraud-graph-agent .

# Run container
docker run -p 8001:8001 fraud-graph-agent
```

## 🔧 Development

```bash
# Start development server
make run

# Run tests
make test

# Build and run Docker
make docker
```

## 📊 Performance

- **FAST Scoring**: ~100ms for 1000 transactions
- **Precision Analysis**: ~500ms per transaction
- **Memory Usage**: ~50MB base + 10MB per 1000 transactions

## 🤝 Team Integration

### ✅ Members A & B (This Repository)
**Status**: INTEGRATED ✨

Both Member A's graph analysis and Member B's ML anomaly detection work together in this codebase:
- Member A: Graph scoring via `/v1/graph/score` and `/v1/graph/precision` endpoints
- Member B: ML detection via `/run-agentB` endpoint and `run_detection.py` script
- Output files: `models/ml_scores.csv` (Member B) + graph scores from API (Member A)

### For Member C (Verifier Agent)
- **Input**: Use Member A's `/v1/graph/precision` endpoint + Member B's `ml_scores.csv`
- **Output**: Add `verifier_verdict` and `verifier_reason` columns
- **Join on**: `idx` field

### For Member D (UI/Dashboard/Alerts)
- **Input**: Merge results from Members A, B, and C
- **Display**: 
  - Combined results table with all scores
  - Link to `fraud_ring_7d.html` and `fraud_ring_30d.html` visualizations
  - SHAP explanations from Member B
  - Graph features from Member A
- **Interactive**: Call Member A's precision endpoint for detailed analysis

### Integration Example
```python
# 1. Run Member B's ML detection
import scripts.run_detection as rd
rd.main()  # Generates models/ml_scores.csv

# 2. Call Member A's Graph API
import requests
response = requests.post(
    "http://localhost:8001/v1/graph/score",
    json={"transactions": [...]}
)
graph_scores = response.json()

# 3. Merge on 'idx' field
import pandas as pd
ml_df = pd.read_csv("models/ml_scores.csv")
graph_df = pd.DataFrame(graph_scores["results"])
merged = pd.merge(ml_df, graph_df, on="idx")
# Ready for Member C and D!
```

## 📚 Documentation

- **API Reference**: `docs/api.md`
- **Architecture**: `docs/architecture.md`
- **Responsible AI**: `docs/responsible_ai.md`
- **Interactive Docs**: http://127.0.0.1:8001/docs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions or issues:
1. Check the [documentation](docs/)
2. Review [test examples](tests/)
3. Open an issue in the repository

---

**Ready for production deployment and team integration! 🚀**

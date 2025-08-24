# Graph & Link Analysis Agent (Member A)

Production-ready FastAPI service for graph-based fraud-ring detection using network analysis and machine learning techniques.

## 🚀 Features

- **FAST Batch Scoring**: High-performance batch processing with global graph features
- **Precision Analysis**: Detailed 7-day vs 30-day subgraph analysis for suspicious transactions
- **Real-time API**: RESTful endpoints for seamless integration
- **Production Ready**: Docker support, comprehensive testing, and documentation

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/v1/graph/score` | POST | Batch FAST scoring for transactions |
| `/v1/graph/precision` | POST | Detailed analysis for single transaction |

## 🏗️ Architecture

```
Raw Transactions → Graph Agent → Graph-based Scores → Team Integration
     ↓                    ↓              ↓              ↓
  CSV/JSON         NetworkX Graph    Fraud Scores    Members B,C,D
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

### Running the Service
```bash
# Start the API server
uvicorn api.app:app --reload --port 8001

# Open API documentation
# http://127.0.0.1:8001/docs
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
├── api/                    # FastAPI application
│   └── app.py            # Main API entry point
├── src/                   # Core scoring modules
│   ├── graph_scoring.py  # FAST batch scoring
│   └── precision_scoring.py # 7d/30d analysis
├── tests/                 # Test suite
│   ├── test_api.py       # API tests
│   ├── sample_request.json # Basic test data
│   ├── better_test_data.json # Extended test data
│   └── fraud_ring_scenario.json # Fraud pattern test
├── docs/                  # Documentation
│   ├── api.md            # API reference
│   ├── architecture.md   # System architecture
│   └── responsible_ai.md # AI ethics guidelines
├── outputs/               # Demo artifacts
│   ├── sample_graph_score.json
│   ├── ring_scores_window.csv
│   ├── fraud_ring_7d.html
│   └── fraud_ring_30d.html
├── notebooks/             # Analysis notebooks
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── Makefile              # Development commands
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

### For Member B (ML Anomaly Detector)
- Use `/v1/graph/score` endpoint
- Join results on `idx` field
- Add `ml_score` column

### For Member C (Verifier Agent)
- Use `/v1/graph/precision` endpoint
- Add `verifier_verdict` and `verifier_reason` columns

### For Member D (UI/Alerts)
- Display merged results table
- Link to `fraud_ring_7d.html` visualizations
- Call precision endpoint for detailed analysis

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

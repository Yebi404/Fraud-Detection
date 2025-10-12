# Integrated Pipeline Architecture

## Overview

This repository contains the **integrated fraud detection system** combining:
- **Member A**: Graph & Link Analysis Agent
- **Member B**: ML Anomaly Detection Agent

Both agents work together to provide comprehensive fraud detection capabilities.

## Architecture Diagram

```
                    ┌─────────────────────────────────────┐
                    │      Raw Transaction Data           │
                    │    (CSV/JSON via API or file)       │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │                                     │
         ┌──────────▼──────────┐           ┌────────────▼─────────┐
         │   MEMBER A:          │           │   MEMBER B:          │
         │ Graph & Link Agent   │           │ ML Anomaly Detector  │
         │                      │           │                      │
         │ • NetworkX Graph     │           │ • Isolation Forest   │
         │ • PageRank           │           │ • One-Class SVM      │
         │ • Community Detection│           │ • XGBoost            │
         │ • Motif Analysis     │           │ • SHAP Explanations  │
         │                      │           │                      │
         │ Endpoints:           │           │ Endpoints:           │
         │ /v1/graph/score      │           │ /v1/ml/detect        │
         │ /v1/graph/precision  │           │ /run-agentB          │
         └──────────┬───────────┘           └────────────┬─────────┘
                    │                                     │
         ┌──────────▼──────────┐           ┌────────────▼─────────┐
         │ Outputs:             │           │ Outputs:             │
         │ • ring_score_7d      │           │ • ml_score           │
         │ • ring_score_30d     │           │ • ml_supervised      │
         │ • component_size     │           │ • anomaly_score      │
         │ • pagerank           │           │ • SHAP features      │
         │ • confidence         │           │ • risk_score         │
         └──────────┬───────────┘           └────────────┬─────────┘
                    │                                     │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │   UNIFIED INTEGRATION LAYER         │
                    │   /v1/unified/score                 │
                    │   (Merges both A & B results)       │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │     Member C: Verifier Agent        │
                    │  • verifier_verdict                 │
                    │  • verifier_reason                  │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │     Member D: UI/Dashboard/Alerts   │
                    │  • Integrated display               │
                    │  • Visualizations                   │
                    │  • Alert notifications              │
                    └─────────────────────────────────────┘
```

## Integration Key

**Shared merge key**: `idx` (transaction ID)

All components use the `idx` field to join results across different agents.

## Data Flow

### 1. Input Stage
- **Format**: CSV or JSON via API
- **Required Fields**: `idx`, `step`, `type`, `amount`, `nameOrig`, `nameDest`
- **Optional Fields**: `isFraud` (for supervised learning)

### 2. Member A Processing (Graph Analysis)
- Builds bipartite graph: users → receivers
- Computes network features:
  - Component size
  - PageRank scores
  - Community structure (Louvain)
  - K-core numbers
  - Temporal burst patterns
  - U-R-U motif counts
- Generates `ring_score_7d` and `ring_score_30d`

### 3. Member B Processing (ML Detection)
- Applies ensemble of models:
  - **Isolation Forest**: Anomaly detection
  - **One-Class SVM**: Novelty detection
  - **XGBoost**: Supervised classification (if labels available)
- Generates:
  - `ml_score`: Combined anomaly score
  - `ml_supervised`: XGBoost probability (if trained)
  - SHAP explanations for interpretability

### 4. Integration
- Results merged on `idx` field
- Combined output includes both graph and ML scores
- Available via:
  - File exports: `models/ml_scores.csv`, `outputs/graph_scores.json`
  - Unified API: `/v1/unified/score`

### 5. Handoff to Members C & D
- **Member C (Verifier)**: Receives integrated scores, adds verification
- **Member D (UI)**: Displays merged results with visualizations

## API Endpoints

### Member A Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/graph/score` | POST | Batch graph scoring |
| `/v1/graph/precision` | POST | Detailed 7d/30d analysis |

### Member B Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/ml/detect` | POST | ML detection from file |
| `/v1/ml/detect-from-transactions` | POST | ML detection from JSON |
| `/run-agentB` | POST | Legacy endpoint |

### Unified Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/unified/score` | POST | Combined A+B analysis |
| `/health` | GET | System health check |

## Deployment Options

### Option 1: Separate Services (Microservices)
```bash
# Terminal 1: Member A
uvicorn api.app:app --port 8001

# Terminal 2: Member B
python scripts/memberB_api.py --port 8002
```

### Option 2: Unified Service (Recommended for Demo)
```bash
# Single unified API
uvicorn api.unified_app:app --port 8001
```

### Option 3: Standalone Scripts
```bash
# Run full integrated demo
python scripts/demo_integrated.py

# Run only Member B detection
python scripts/run_detection.py
```

## File Outputs

### Member B Outputs
- `models/anomaly_output_standard.json`: Full ML results with explanations
- `models/ml_scores.csv`: CSV format for easy integration

### Member A Outputs
- `outputs/graph_scores.json`: Graph analysis results
- `outputs/fraud_ring_7d.html`: 7-day network visualization
- `outputs/fraud_ring_30d.html`: 30-day network visualization

### Integrated Outputs
- `outputs/integrated_results.csv`: Combined A+B results

## Performance Characteristics

### Member A (Graph Analysis)
- **Batch Scoring**: ~100ms for 1000 transactions
- **Precision Analysis**: ~500ms per transaction
- **Memory**: ~50MB base + 10MB per 1000 transactions

### Member B (ML Detection)
- **Isolation Forest**: ~200ms for 1000 transactions
- **One-Class SVM**: ~500ms for 10,000 samples
- **XGBoost**: ~1s training, ~50ms inference for 1000 transactions
- **Memory**: ~100MB base + 20MB per 10,000 transactions

### Unified Pipeline
- **Combined Processing**: ~2-3s for full pipeline on 1000 transactions
- **Memory**: ~150MB total

## Scalability Considerations

1. **Horizontal Scaling**: Deploy Member A and B as separate microservices
2. **Batch Processing**: Process large datasets in chunks
3. **Caching**: Cache graph computations for repeated queries
4. **Async Processing**: Use background tasks for ML training

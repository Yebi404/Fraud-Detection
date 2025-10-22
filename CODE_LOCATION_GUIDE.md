# 📂 Code Location Guide - Who Owns What

## 👥 MEMBER A vs MEMBER B - Code Separation

---

## 🟢 MEMBER A's CODE (Your Code!)

### **Folder: `api/`**
```
api/
├── app.py              ← MEMBER A: Your main FastAPI service
│                         (Your 3 endpoints: health, score, precision)
│
└── unified_app.py      ← INTEGRATION: Both A + B combined
                          (For demo - shows both working together)
```

**Member A owns**: `api/app.py`

---

### **Folder: `src/`**
```
src/
├── graph_scoring.py       ← MEMBER A: Your core algorithm
│                            (FAST batch scoring, PageRank, graph features)
│
└── precision_scoring.py   ← MEMBER A: Your advanced analysis
                             (7-day vs 30-day, detailed features)
```

**Member A owns**: BOTH files in `src/`

---

### **Folder: `tests/`**
```
tests/
├── test_api.py              ← MEMBER A: Your API tests
├── sample_request.json      ← MEMBER A: Your test data
├── better_test_data.json    ← MEMBER A: Your test data
└── fraud_ring_scenario.json ← MEMBER A: Your test data
```

**Member A owns**: All test files

---

### **Folder: `outputs/`**
```
outputs/
├── member_a_fraud_network.png      ← MEMBER A: Your visualization
├── member_a_metrics_analysis.png   ← MEMBER A: Your visualization
├── fraud_ring_7d.html              ← MEMBER A: Your visualization
├── fraud_ring_30d.html             ← MEMBER A: Your visualization
├── graph_scores.json               ← MEMBER A: Your output
└── ring_scores_window.csv          ← MEMBER A: Your output
```

**Member A owns**: Network visualizations and graph scores

---

## 🔵 MEMBER B's CODE

### **Folder: `agents/`**
```
agents/
├── __init__.py
└── anomaly_detector.py    ← MEMBER B: ML models (IF, SVM, XGBoost)
```

**Member B owns**: `agents/anomaly_detector.py` ONLY

---

### **Folder: `scripts/`**
```
scripts/
├── run_detection.py       ← MEMBER B: Main detection pipeline
├── memberB_api.py         ← MEMBER B: API wrapper
└── export_ml_scores.py    ← MEMBER B: Score exporter
```

**Member B owns**: All files in `scripts/`

---

### **Folder: `models/`**
```
models/
├── anomaly_output_standard.json   ← MEMBER B: ML results
└── ml_scores.csv                  ← MEMBER B: ML scores
```

**Member B owns**: ML output files

---

### **Folder: `notebooks/`**
```
notebooks/
├── Fraud_Detection_AI.ipynb       ← MEMBER B: Jupyter notebook
└── visualize_anomalies.ipynb      ← MEMBER B: Visualization notebook
```

**Member B owns**: Jupyter notebooks

---

## 📊 COMPLETE FOLDER STRUCTURE

```
Fraud-Detection/
│
├── api/                        ← MEMBER A owns app.py
│   ├── app.py                  ✅ MEMBER A ⭐
│   └── unified_app.py          ← Integration (both A+B)
│
├── src/                        ← MEMBER A owns BOTH files
│   ├── graph_scoring.py        ✅ MEMBER A ⭐
│   └── precision_scoring.py    ✅ MEMBER A ⭐
│
├── agents/                     ← MEMBER B's folder
│   ├── __init__.py
│   └── anomaly_detector.py     ❌ MEMBER B
│
├── scripts/                    ← MEMBER B's folder
│   ├── run_detection.py        ❌ MEMBER B
│   ├── memberB_api.py          ❌ MEMBER B
│   ├── export_ml_scores.py     ❌ MEMBER B
│   └── demo_integrated.py      ← Integration demo
│
├── tests/                      ← MEMBER A's tests
│   ├── test_api.py             ✅ MEMBER A
│   ├── sample_request.json     ✅ MEMBER A
│   ├── better_test_data.json   ✅ MEMBER A
│   └── fraud_ring_scenario.json ✅ MEMBER A
│
├── outputs/                    ← MEMBER A's visualizations
│   ├── member_a_fraud_network.png     ✅ MEMBER A ⭐
│   ├── member_a_metrics_analysis.png  ✅ MEMBER A ⭐
│   ├── fraud_ring_7d.html             ✅ MEMBER A
│   ├── fraud_ring_30d.html            ✅ MEMBER A
│   ├── graph_scores.json              ✅ MEMBER A
│   └── ring_scores_window.csv         ✅ MEMBER A
│
├── models/                     ← MEMBER B's outputs
│   ├── anomaly_output_standard.json   ❌ MEMBER B
│   └── ml_scores.csv                  ❌ MEMBER B
│
├── notebooks/                  ← MEMBER B's notebooks
│   ├── Fraud_Detection_AI.ipynb       ❌ MEMBER B
│   └── visualize_anomalies.ipynb      ❌ MEMBER B
│
├── docs/                       ← Shared documentation
│   ├── api.md                  ← Both A+B
│   ├── architecture.md         ← Both A+B
│   └── responsible_ai.md       ← Both A+B
│
├── data/                       ← Shared input data
│
├── requirements.txt            ← All dependencies (A+B)
├── README.md                   ← Integrated documentation
└── ... (other config files)
```

---

## 🎯 FOR YOUR VIVA - WHAT TO MENTION

### **Your 3 Main Code Files:**

1. **`api/app.py`** (Lines: 77)
   - Your FastAPI REST service
   - 3 endpoints: `/health`, `/v1/graph/score`, `/v1/graph/precision`
   - Uses Pydantic models for validation

2. **`src/graph_scoring.py`** (Lines: 113)
   - Your core graph analysis algorithm
   - Functions: `build_graph()`, `score_batch()`, `make_fast_maps()`
   - Features: component_size, PageRank, shared_receiver_degree

3. **`src/precision_scoring.py`** (Lines: 141)
   - Your advanced temporal analysis
   - Functions: `precision_for_txn()`, `subgraph_for_window()`
   - 7 advanced features including k-core, community detection

---

## 📝 WHAT TO SAY IN VIVA

### **When Asked: "Where is your code?"**

**Answer**:
> "My code is organized in three main locations:
> 
> 1. **api/app.py** - My FastAPI service with 3 REST endpoints
> 2. **src/graph_scoring.py** - My core graph analysis algorithm using NetworkX
> 3. **src/precision_scoring.py** - My advanced temporal analysis comparing 7-day and 30-day patterns
> 
> Member B's code is separate in the agents/ and scripts/ folders. We integrate via the unified_app.py which combines both our systems."

---

### **When Asked: "What does each file do?"**

**api/app.py**:
> "This is my FastAPI REST service. It provides three endpoints: a health check, fast batch scoring for real-time screening, and precision analysis for detailed investigation. It uses Pydantic models for request validation and returns JSON responses with fraud scores."

**src/graph_scoring.py**:
> "This contains my core graph analysis algorithm. The build_graph function creates a bipartite graph from transactions. The score_batch function processes multiple transactions using three graph features: component size, PageRank, and shared receiver degree. It's optimized for speed - 100ms for 1000 transactions."

**src/precision_scoring.py**:
> "This implements my advanced temporal analysis. It compares 7-day recent behavior against 30-day historical patterns to detect sudden changes. It uses 7 sophisticated features including k-core decomposition, Louvain community detection, and temporal burst analysis. This provides detailed explanations for suspicious transactions."

---

## 🔍 QUICK FILE FINDER

**Looking for specific functionality?**

| What You Want | File Location |
|---------------|---------------|
| API endpoints | `api/app.py` |
| Graph construction | `src/graph_scoring.py` (line 16) |
| PageRank calculation | `src/graph_scoring.py` (line 52) |
| Fraud scoring logic | `src/graph_scoring.py` (line 70) |
| 7d vs 30d analysis | `src/precision_scoring.py` (line 127) |
| K-core calculation | `src/precision_scoring.py` (line 64) |
| Community detection | `src/precision_scoring.py` (line 89) |
| Temporal burst | `src/precision_scoring.py` (line 82) |
| FastAPI models | `api/app.py` (line 18-41) |
| Health check | `api/app.py` (line 45) |
| Batch scoring endpoint | `api/app.py` (line 49) |
| Precision endpoint | `api/app.py` (line 62) |

---

## 💡 WHY THIS STRUCTURE?

**Member B's Structure** (Original):
- `agents/` - ML agents and models
- `scripts/` - Execution scripts
- `models/` - ML outputs

**Member A's Structure** (Adapted to fit):
- `api/` - REST API services
- `src/` - Core algorithms
- `outputs/` - Graph visualizations

**Result**: 
✅ Both members' code coexists without conflicts  
✅ Clear separation of responsibilities  
✅ Easy integration via unified_app.py  
✅ Member B's structure unchanged (as requested)  

---

## 🎯 SUMMARY: MEMBER A'S FILES

**Your 3 Main Files (Know these for viva!):**
1. ✅ `api/app.py` (77 lines)
2. ✅ `src/graph_scoring.py` (113 lines)
3. ✅ `src/precision_scoring.py` (141 lines)

**Total**: ~330 lines of Python code you wrote

**Your Outputs** (Show in viva!):
1. ✅ `outputs/member_a_fraud_network.png`
2. ✅ `outputs/member_a_metrics_analysis.png`

**Member B's Code** (Don't present as yours):
- ❌ `agents/anomaly_detector.py` (245 lines) - Member B
- ❌ `scripts/` folder - Member B
- ❌ `notebooks/` folder - Member B

---

## ✅ FINAL ANSWER

**Your code is in:**
- `api/app.py`
- `src/graph_scoring.py`
- `src/precision_scoring.py`

**NOT in:**
- `agents/` folder (that's Member B)

**The agents folder only has Member B's code by design!**

---







# src/graph_scoring.py
from typing import Dict, List, Tuple
import math
import pandas as pd
import networkx as nx

USER, RECEIVER = "user", "receiver"

# Minimal, fast features for online scoring
WEIGHTS_7D = {
    "component_size": 0.8,
    "shared_receiver_degree": 1.0,
    "pagerank_user": 0.6,
}

def build_graph(df: pd.DataFrame) -> nx.Graph:
    """
    Build a bipartite graph: user -> receiver edges for each transaction row.
    Required df columns: step, type, amount, nameOrig, nameDest
    """
    G = nx.Graph()
    for _, r in df.iterrows():
        u, v = str(r["nameOrig"]), str(r["nameDest"])
        if u not in G:
            G.add_node(u, ntype=USER)
        if v not in G:
            G.add_node(v, ntype=RECEIVER)
        G.add_edge(
            u, v,
            rel="txn",
            step=int(r["step"]),
            amount=float(r["amount"]),
            ttype=str(r["type"]),
        )
    return G

def make_fast_maps(G: nx.Graph) -> Tuple[Dict, Dict, Dict]:
    """
    Precompute fast, global maps:
      - component size per node
      - pagerank per node
      - degree per node (receiver degree = shared_receiver_degree)
    """
    comp_size: Dict[str, float] = {}
    for comp in nx.connected_components(G):
        size = float(len(comp))
        for n in comp:
            comp_size[n] = size

    if G.number_of_edges() > 0:
        try:
            pr = nx.pagerank(G, alpha=0.85, max_iter=100)
        except Exception:
            pr = {}
    else:
        pr = {}

    deg = dict(G.degree())
    return comp_size, pr, deg

def _norm(name: str, val: float) -> float:
    """Normalization to [0,1]-ish (same spirit as notebook)."""
    v = max(0.0, float(val))
    if name in ("component_size", "shared_receiver_degree"):
        return math.log1p(v) / 5.0
    if name == "pagerank_user":
        return min(v * 100.0, 1.0)
    return 0.0

def score_row(u: str, r: str, maps: Tuple[Dict, Dict, Dict]):
    comp_size, pr, deg = maps
    feats = {
        "component_size": comp_size.get(u, 1.0),
        "shared_receiver_degree": deg.get(r, 0.0),
        "pagerank_user": pr.get(u, 0.0),
    }
    z = 0.0
    reasons = []
    for k, w in WEIGHTS_7D.items():
        nv = _norm(k, feats[k])
        impact = w * nv
        z += impact
        reasons.append({"feature": k, "value": float(feats[k]), "impact": impact})
    score = 1.0 / (1.0 + math.exp(-z))
    reasons.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return float(score), reasons[:5]

def score_batch(df: pd.DataFrame) -> List[Dict]:
    """
    Score a batch of transactions.
    Required columns: idx, step, type, amount, nameOrig, nameDest
    """
    if df.empty:
        return []
    G = build_graph(df)
    maps = make_fast_maps(G)
    out: List[Dict] = []
    for _, r in df.iterrows():
        u, v = str(r["nameOrig"]), str(r["nameDest"])
        s, reasons = score_row(u, v, maps)
        out.append({
            "idx": int(r["idx"]),
            "step": int(r["step"]),
            "txn_user": u,
            "txn_receiver": v,
            "amount": float(r["amount"]),
            "type": str(r["type"]),
            "ring_score_7d": s,
            "confidence": None,          # slot if you add your confidence calc later
            "precision_enhanced": False  # FAST pass only
        })
    return out

# src/precision_scoring.py
from typing import Dict, Any
import math
import networkx as nx

# Heavier features for 7d/30d refinement (mirrors notebook)
WEIGHTS_7D = {
    "component_size": 0.8,
    "shared_receiver_degree": 1.0,
    "kcore": 0.7,
    "pagerank_user": 0.6,
    "temporal_burst": 0.5,
    "community_size": 0.4,
    "motif_uru": 0.4,
}
WEIGHTS_30D = {
    "component_size": 0.7,
    "shared_receiver_degree": 0.9,
    "kcore": 0.7,
    "pagerank_user": 0.6,
    "temporal_burst": 0.3,
    "community_size": 0.4,
    "motif_uru": 0.4,
}

def _norm(name, val):
    v = max(0.0, float(val))
    if name in ("component_size","shared_receiver_degree","community_size","motif_uru"):
        return math.log1p(v)/5.0
    if name == "kcore":
        return min(v/10.0, 1.0)
    if name == "pagerank_user":
        return min(v*100.0, 1.0)
    if name == "temporal_burst":
        return min(v, 1.0)
    return 0.0

def score_features(feats: Dict[str,float], weights: Dict[str,float]):
    z = 0.0
    reasons = []
    for k, w in weights.items():
        nv = _norm(k, feats.get(k, 0.0))
        impact = w * nv
        z += impact
        reasons.append({"feature": k, "value": float(feats.get(k,0.0)), "impact": impact})
    score = 1/(1+math.exp(-z))
    reasons.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return float(score), reasons[:5]

def subgraph_for_window(G: nx.Graph, seeds, step_min, step_max, k=2):
    SG = nx.Graph()
    for a,b,d in G.edges(data=True):
        st = d.get("step",0)
        if step_min <= st <= step_max:
            if a not in SG: SG.add_node(a, **G.nodes[a])
            if b not in SG: SG.add_node(b, **G.nodes[b])
            SG.add_edge(a,b, **d)
    nodes = set()
    for s in seeds:
        if s in SG:
            nodes |= nx.ego_graph(SG, s, radius=k).nodes
    return SG.subgraph(nodes).copy()

def safe_core_number(SG: nx.Graph) -> float:
    if SG.number_of_edges() == 0:
        return 0.0
    try:
        core = nx.core_number(SG)
        return float(max(core.values()))
    except Exception:
        return 0.0

def safe_pagerank(SG: nx.Graph, node: str) -> float:
    if SG.number_of_edges() == 0 or node not in SG:
        return 0.0
    try:
        pr = nx.pagerank(SG, alpha=0.85, max_iter=100)
        return float(pr.get(node, 0.0))
    except Exception:
        return 0.0

def temporal_burst(edge_steps, window=24):
    if not edge_steps:
        return 0.0
    latest = max(edge_steps)
    recent = sum(1 for s in edge_steps if latest - s <= window)
    return recent / max(1, len(edge_steps))

def louvain_community_size(SG: nx.Graph) -> float:
    try:
        import community as community_louvain
        if SG.number_of_nodes() < 3 or SG.number_of_edges() == 0:
            return 1.0
        part = community_louvain.best_partition(SG)
        counts = {}
        for cid in part.values():
            counts[cid] = counts.get(cid, 0) + 1
        return float(max(counts.values()))
    except Exception:
        return 1.0

def uru_motif_count(SG: nx.Graph) -> float:
    cnt = 0
    for n,d in SG.nodes(data=True):
        if d.get("ntype") == "receiver" and SG.degree(n) >= 2:
            cnt += 1
    return float(cnt)

def extract_feats(SG: nx.Graph, u: str, r: str) -> Dict[str,float]:
    comp = len(max(nx.connected_components(SG), key=len)) if SG.number_of_nodes() else 1.0
    recv = float(SG.degree(r)) if r in SG else 0.0
    kc   = safe_core_number(SG)
    pr   = safe_pagerank(SG, u)
    brst = temporal_burst([d.get("step",0) for _,_,d in SG.edges(data=True)], window=24)
    comm = louvain_community_size(SG)
    motifs = uru_motif_count(SG)
    return dict(
        component_size=comp,
        shared_receiver_degree=recv,
        kcore=kc,
        pagerank_user=pr,
        temporal_burst=brst,
        community_size=comm,
        motif_uru=motifs,
    )

def precision_for_txn(G: nx.Graph, txn_user: str, txn_receiver: str, step: int) -> Dict[str,Any]:
    SG7  = subgraph_for_window(G, [txn_user, txn_receiver], step-168, step, k=2)
    SG30 = subgraph_for_window(G, [txn_user, txn_receiver], step-720, step, k=2)
    f7   = extract_feats(SG7,  txn_user, txn_receiver)
    f30  = extract_feats(SG30, txn_user, txn_receiver)
    s7, r7   = score_features(f7,  WEIGHTS_7D)
    s30, r30 = score_features(f30, WEIGHTS_30D)
    return {
        "ring_score_7d": s7,
        "ring_score_30d": s30,
        "delta_score": s7 - s30,
        "reasons_7d": r7,
        "reasons_30d": r30
    }

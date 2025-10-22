#!/usr/bin/env python3
"""
Generate Graph Visualizations for Member A's Work
Creates network graphs showing fraud patterns
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph_scoring import build_graph

print("=" * 70)
print("Generating Graph Visualizations for Member A")
print("=" * 70)
print()

# Create output directory
os.makedirs("outputs", exist_ok=True)

# Sample fraud ring data - THIS IS YOUR DEMO DATA
print("Creating sample fraud ring scenario...")
data = pd.DataFrame({
    'idx': list(range(1, 13)),
    'step': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106],
    'type': ['TRANSFER'] * 10 + ['CASH_OUT'] * 2,
    'amount': [1000, 2000, 1500, 3000, 2500, 1800, 2200, 1900, 2600, 2100, 15000, 14500],
    'nameOrig': ['User1', 'User2', 'User3', 'User4', 'User5', 
                  'User6', 'User7', 'User8', 'User9', 'User10', 
                  'SuspectReceiver', 'SuspectReceiver'],
    'nameDest': ['SuspectReceiver', 'SuspectReceiver', 'SuspectReceiver', 
                  'SuspectReceiver', 'SuspectReceiver', 'SuspectReceiver',
                  'SuspectReceiver', 'NormalReceiver', 'NormalReceiver', 
                  'NormalReceiver', 'ExitAccount1', 'ExitAccount2']
})

print(f"✅ Created {len(data)} sample transactions")
print(f"   - 7 users → SuspectReceiver (FRAUD RING PATTERN)")
print(f"   - 3 users → NormalReceiver (Normal transactions)")
print(f"   - 2 cash-outs from SuspectReceiver (Money laundering)")
print()

# Build graph using Member A's function
print("Building graph using Member A's algorithm...")
G = build_graph(data)
print(f"✅ Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print()

# Calculate graph metrics
print("Calculating graph metrics (Your Features)...")
degrees = dict(G.degree())
try:
    pagerank = nx.pagerank(G)
    print("✅ PageRank calculated")
except:
    pagerank = {node: 0.1 for node in G.nodes()}
    print("⚠️  PageRank calculation skipped")

components = list(nx.connected_components(G))
print(f"✅ Found {len(components)} connected components")
print()

# Identify suspicious patterns
print("Fraud Pattern Detection:")
suspicious_receivers = []
for node, degree in degrees.items():
    if G.nodes[node].get('ntype') == 'receiver' and degree >= 3:
        suspicious_receivers.append((node, degree))
        print(f"  ⚠️  {node}: {degree} incoming connections (FRAUD INDICATOR)")

if not suspicious_receivers:
    print("  ✓ No obvious fraud patterns detected")
print()

# Generate Visualization 1: Network Graph
print("Generating network visualization...")
plt.figure(figsize=(14, 10))

# Position nodes using spring layout
pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

# Separate nodes by type
users = [n for n, d in G.nodes(data=True) if d.get('ntype') == 'user']
receivers = [n for n, d in G.nodes(data=True) if d.get('ntype') == 'receiver']

# Draw nodes
nx.draw_networkx_nodes(G, pos, nodelist=users, 
                        node_color='#90EE90', node_size=600, 
                        label='Users (Senders)', alpha=0.9,
                        edgecolors='black', linewidths=2)

# Color receivers by suspiciousness
suspicious_nodes = [n for n, d in suspicious_receivers]
normal_receivers = [n for n in receivers if n not in suspicious_nodes]

if suspicious_nodes:
    nx.draw_networkx_nodes(G, pos, nodelist=suspicious_nodes, 
                            node_color='#FF4444', node_size=1000, 
                            label='Suspicious Receivers (⚠️)', alpha=0.9,
                            edgecolors='darkred', linewidths=3)

if normal_receivers:
    nx.draw_networkx_nodes(G, pos, nodelist=normal_receivers, 
                            node_color='#4444FF', node_size=700, 
                            label='Normal Receivers', alpha=0.9,
                            edgecolors='darkblue', linewidths=2)

# Draw edges with varying width based on amount
edge_widths = []
for (u, v) in G.edges():
    amount = G[u][v].get('amount', 1000)
    width = 1 + (amount / 2000)  # Scale width
    edge_widths.append(width)

nx.draw_networkx_edges(G, pos, alpha=0.4, width=edge_widths, 
                        edge_color='gray', arrows=True, 
                        arrowsize=20, arrowstyle='->')

# Draw labels
nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold',
                         font_family='sans-serif')

plt.title("Fraud Ring Network Visualization\n(Member A: Graph & Link Analysis)", 
          fontsize=16, fontweight='bold', pad=20)
plt.legend(loc='upper left', fontsize=11, framealpha=0.9)
plt.axis('off')
plt.tight_layout()

output_file1 = "outputs/member_a_fraud_network.png"
plt.savefig(output_file1, dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print(f"✅ Saved: {output_file1}")
plt.close()

# Generate Visualization 2: Degree Distribution
print("Generating degree distribution chart...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Node degrees
nodes = list(degrees.keys())
degree_values = list(degrees.values())
colors = ['red' if G.nodes[n].get('ntype') == 'receiver' and degrees[n] >= 3 
          else 'blue' if G.nodes[n].get('ntype') == 'receiver'
          else 'green' for n in nodes]

ax1.barh(nodes, degree_values, color=colors, alpha=0.7, edgecolor='black')
ax1.set_xlabel('Number of Connections', fontsize=12, fontweight='bold')
ax1.set_ylabel('Node', fontsize=12, fontweight='bold')
ax1.set_title('Node Connectivity Analysis\n(Red = Suspicious)', 
              fontsize=13, fontweight='bold')
ax1.axvline(x=3, color='red', linestyle='--', linewidth=2, 
            label='Fraud Threshold (3+ connections)')
ax1.legend()
ax1.grid(axis='x', alpha=0.3)

# Plot 2: PageRank scores
pr_nodes = list(pagerank.keys())
pr_values = list(pagerank.values())
pr_colors = ['red' if n in suspicious_nodes else 'gray' for n in pr_nodes]

ax2.barh(pr_nodes, pr_values, color=pr_colors, alpha=0.7, edgecolor='black')
ax2.set_xlabel('PageRank Score', fontsize=12, fontweight='bold')
ax2.set_ylabel('Node', fontsize=12, fontweight='bold')
ax2.set_title('Node Importance (PageRank)\n(Red = Suspicious)', 
              fontsize=13, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
output_file2 = "outputs/member_a_metrics_analysis.png"
plt.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Saved: {output_file2}")
plt.close()

# Generate Summary Report
print()
print("=" * 70)
print("GRAPH ANALYSIS SUMMARY REPORT")
print("=" * 70)
print()
print("📊 Network Statistics:")
print(f"  • Total Nodes: {G.number_of_nodes()}")
print(f"  • Total Edges: {G.number_of_edges()}")
print(f"  • Connected Components: {len(components)}")
print(f"  • Graph Density: {nx.density(G):.4f}")
print()
print("🚨 Fraud Detection Results:")
if suspicious_receivers:
    print(f"  • Found {len(suspicious_receivers)} SUSPICIOUS receiver(s):")
    for node, degree in suspicious_receivers:
        pr_score = pagerank.get(node, 0)
        print(f"    ⚠️  {node}:")
        print(f"       - {degree} incoming connections (FRAUD RING INDICATOR)")
        print(f"       - PageRank: {pr_score:.4f} (High importance)")
        print(f"       - Status: HIGH RISK - Multiple users sending to same account")
else:
    print("  ✓ No high-risk fraud patterns detected")
print()
print("📈 PageRank Analysis (Top 5 Most Important Nodes):")
top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
for i, (node, score) in enumerate(top_pagerank, 1):
    node_type = G.nodes[node].get('ntype', 'unknown')
    print(f"  {i}. {node} ({node_type}): {score:.4f}")
print()
print("💡 Key Findings:")
if suspicious_receivers:
    print(f"  • Classic FRAUD RING pattern detected")
    print(f"  • Multiple independent users sending to same receiver")
    print(f"  • Suggests coordinated attack or compromised accounts")
    print(f"  • Recommendation: Immediately investigate {suspicious_receivers[0][0]}")
else:
    print(f"  • Normal transaction patterns observed")
    print(f"  • No obvious fraud ring structures")
print()

print("=" * 70)
print("✅ VISUALIZATION GENERATION COMPLETE!")
print("=" * 70)
print()
print("📁 Generated Files (Use these in your viva!):")
print(f"  1. {output_file1}")
print(f"     → Network graph showing fraud ring pattern")
print(f"  2. {output_file2}")
print(f"     → Metrics charts (connectivity & PageRank)")
print()
print("🎬 How to Use in Viva Demonstration:")
print("  1. Show the network graph first")
print("  2. Point out the RED nodes (suspicious receivers)")
print("  3. Explain how your algorithm detected the pattern")
print("  4. Show the metrics charts to quantify the risk")
print("  5. Mention the PageRank scores identifying key nodes")
print()
print("💬 What to Say:")
print('  "My graph analysis detected a fraud ring pattern where')
print(f'   {suspicious_receivers[0][1] if suspicious_receivers else 0} different users are sending to the same receiver.')
print('   This is a classic fraud indicator that traditional analysis')
print('   would miss because each individual transaction looks normal.')
print('   My PageRank algorithm also identified this receiver as a')
print('   high-importance node in the network."')
print()
print("🎯 Technical Points to Highlight:")
print("  ✓ Bipartite graph structure (users → receivers)")
print("  ✓ Degree centrality for detecting hubs")
print("  ✓ PageRank for node importance ranking")
print("  ✓ Visual representation for interpretability")
print("  ✓ Automated pattern detection")
print()







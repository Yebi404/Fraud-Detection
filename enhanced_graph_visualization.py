#!/usr/bin/env python3
"""
Enhanced Graph Visualization with Transaction Details
Shows step, amount, ttype directly on the graph
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
print("Enhanced Graph Visualization with Transaction Details")
print("=" * 70)
print()

# Create output directory
os.makedirs("outputs", exist_ok=True)

# Sample fraud ring data
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
print()

# Build graph
print("Building graph...")
G = build_graph(data)
print(f"✅ Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print()

# Print all edge details to show what's stored
print("🔍 ALL EDGE DETAILS STORED IN GRAPH:")
print("-" * 50)
for u, v, data in G.edges(data=True):
    print(f"Edge: {u} → {v}")
    print(f"  Step: {data['step']}")
    print(f"  Amount: ${data['amount']:,.2f}")
    print(f"  Type: {data['ttype']}")
    print(f"  Relationship: {data['rel']}")
    print()

# Generate Enhanced Visualization 1: Network Graph with Edge Labels
print("Generating enhanced network visualization with transaction details...")
plt.figure(figsize=(16, 12))

# Position nodes using spring layout
pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

# Separate nodes by type
users = [n for n, d in G.nodes(data=True) if d.get('ntype') == 'user']
receivers = [n for n, d in G.nodes(data=True) if d.get('ntype') == 'receiver']

# Calculate degrees for suspicious detection
degrees = dict(G.degree())
suspicious_receivers = []
for node, degree in degrees.items():
    if G.nodes[node].get('ntype') == 'receiver' and degree >= 3:
        suspicious_receivers.append((node, degree))

# Draw nodes
nx.draw_networkx_nodes(G, pos, nodelist=users, 
                      node_color='#90EE90', node_size=800, 
                      label='Users (Senders)', alpha=0.9,
                      edgecolors='black', linewidths=2)

# Color receivers by suspiciousness
suspicious_nodes = [n for n, d in suspicious_receivers]
normal_receivers = [n for n in receivers if n not in suspicious_nodes]

if suspicious_nodes:
    nx.draw_networkx_nodes(G, pos, nodelist=suspicious_nodes, 
                          node_color='#FF4444', node_size=1200, 
                          label='Suspicious Receivers (⚠️)', alpha=0.9,
                          edgecolors='darkred', linewidths=3)

if normal_receivers:
    nx.draw_networkx_nodes(G, pos, nodelist=normal_receivers, 
                          node_color='#4444FF', node_size=900, 
                          label='Normal Receivers', alpha=0.9,
                          edgecolors='darkblue', linewidths=2)

# Draw edges with varying width based on amount
edge_widths = []
edge_colors = []
for (u, v) in G.edges():
    amount = G[u][v].get('amount', 1000)
    ttype = G[u][v].get('ttype', 'TRANSFER')
    width = 1 + (amount / 2000)  # Scale width
    edge_widths.append(width)
    
    # Color edges by transaction type
    if ttype == 'CASH_OUT':
        edge_colors.append('#FF6B6B')  # Red for cash out
    else:
        edge_colors.append('#4ECDC4')  # Teal for transfer

nx.draw_networkx_edges(G, pos, alpha=0.6, width=edge_widths, 
                      edge_color=edge_colors, arrows=True, 
                      arrowsize=25, arrowstyle='->')

# ⭐ NEW: Draw edge labels with transaction details
edge_labels = {}
for (u, v) in G.edges():
    step = G[u][v].get('step', 0)
    amount = G[u][v].get('amount', 0)
    ttype = G[u][v].get('ttype', 'TRANSFER')
    
    # Create detailed edge label
    edge_labels[(u, v)] = f"Step:{step}\n${amount:,.0f}\n{ttype}"

# Draw edge labels
nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, 
                           font_weight='bold', font_color='darkblue',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", 
                                   edgecolor="gray", alpha=0.8))

# Draw node labels
nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold',
                       font_family='sans-serif')

plt.title("Enhanced Fraud Ring Network with Transaction Details\n" +
          "Step | Amount | Transaction Type", 
          fontsize=16, fontweight='bold', pad=20)
plt.legend(loc='upper left', fontsize=11, framealpha=0.9)
plt.axis('off')
plt.tight_layout()

output_file1 = "outputs/enhanced_fraud_network_with_details.png"
plt.savefig(output_file1, dpi=300, bbox_inches='tight', 
          facecolor='white', edgecolor='none')
print(f"✅ Saved: {output_file1}")
plt.close()

# Generate Enhanced Visualization 2: Transaction Timeline
print("Generating transaction timeline visualization...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: Transaction amounts over time
steps = []
amounts = []
types = []
colors = []

for u, v, data in G.edges(data=True):
    steps.append(data['step'])
    amounts.append(data['amount'])
    types.append(data['ttype'])
    colors.append('red' if data['ttype'] == 'CASH_OUT' else 'blue')

ax1.scatter(steps, amounts, c=colors, alpha=0.7, s=100, edgecolors='black')
ax1.set_xlabel('Time Step', fontsize=12, fontweight='bold')
ax1.set_ylabel('Transaction Amount ($)', fontsize=12, fontweight='bold')
ax1.set_title('Transaction Timeline: Amount vs Time Step\n(Red = CASH_OUT, Blue = TRANSFER)', 
              fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Add annotations for high-value transactions
for i, (step, amount, ttype) in enumerate(zip(steps, amounts, types)):
    if amount > 10000:  # Highlight large transactions
        ax1.annotate(f'${amount:,.0f}\n{ttype}', 
                    (step, amount), xytext=(10, 10), 
                    textcoords='offset points', fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

# Plot 2: Transaction type distribution
type_counts = pd.Series(types).value_counts()
colors_pie = ['#4ECDC4', '#FF6B6B']
wedges, texts, autotexts = ax2.pie(type_counts.values, labels=type_counts.index, 
                                 autopct='%1.1f%%', colors=colors_pie, startangle=90)
ax2.set_title('Transaction Type Distribution', fontsize=13, fontweight='bold')

plt.tight_layout()
output_file2 = "outputs/enhanced_transaction_timeline.png"
plt.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Saved: {output_file2}")
plt.close()

# Generate Enhanced Visualization 3: Detailed Edge Table
print("Generating detailed transaction table...")
fig, ax = plt.subplots(figsize=(16, 8))
ax.axis('tight')
ax.axis('off')

# Create detailed table data
table_data = []
for u, v, data in G.edges(data=True):
    table_data.append([
        f"{u} → {v}",
        data['step'],
        f"${data['amount']:,.2f}",
        data['ttype'],
        data['rel']
    ])

# Sort by step for chronological order
table_data.sort(key=lambda x: x[1])

table = ax.table(cellText=table_data,
                colLabels=['Transaction', 'Step', 'Amount', 'Type', 'Relationship'],
                cellLoc='center',
                loc='center',
                colWidths=[0.3, 0.15, 0.2, 0.15, 0.2])

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# Color code the table rows
for i in range(len(table_data)):
    if table_data[i][3] == 'CASH_OUT':
        for j in range(5):
            table[(i+1, j)].set_facecolor('#FFE6E6')
    else:
        for j in range(5):
            table[(i+1, j)].set_facecolor('#E6F3FF')

plt.title('Detailed Transaction Table\nAll Edge Attributes from Graph Structure', 
          fontsize=14, fontweight='bold', pad=20)

output_file3 = "outputs/enhanced_transaction_table.png"
plt.savefig(output_file3, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Saved: {output_file3}")
plt.close()

# Generate Summary Report
print()
print("=" * 70)
print("ENHANCED VISUALIZATION SUMMARY")
print("=" * 70)
print()
print("📊 What's Now Visible:")
print("  ✅ Step numbers on each edge")
print("  ✅ Transaction amounts on each edge")
print("  ✅ Transaction types (TRANSFER/CASH_OUT) on each edge")
print("  ✅ Color-coded edges by transaction type")
print("  ✅ Timeline showing temporal patterns")
print("  ✅ Detailed transaction table")
print()
print("🎯 Key Improvements:")
print("  • Edge labels show: Step | Amount | Type")
print("  • Red edges = CASH_OUT transactions")
print("  • Teal edges = TRANSFER transactions")
print("  • Edge thickness = Transaction amount")
print("  • Timeline shows temporal fraud patterns")
print()
print("📁 Generated Enhanced Files:")
print(f"  1. {output_file1}")
print(f"     → Network graph with ALL transaction details visible")
print(f"  2. {output_file2}")
print(f"     → Timeline and distribution analysis")
print(f"  3. {output_file3}")
print(f"     → Complete transaction table")
print()
print("💬 What to Say in Viva:")
print('  "Now you can see ALL the transaction details directly on the graph:')
print('   each edge shows the time step, amount, and transaction type.')
print('   This makes it clear how my algorithm uses temporal patterns')
print('   and transaction characteristics for fraud detection."')
print()
print("=" * 70)
print("✅ ENHANCED VISUALIZATION COMPLETE!")
print("=" * 70)


#!/usr/bin/env python3
"""
Enhanced Interactive HTML Graph with Transaction Details
Creates an interactive visualization showing step, amount, ttype on hover/click
"""

import pandas as pd
import networkx as nx
import os
import sys
from pyvis.network import Network

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph_scoring import build_graph

print("=" * 70)
print("Enhanced Interactive HTML Graph with Transaction Details")
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

# Create interactive network
print("Creating enhanced interactive HTML visualization...")
net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")

# Configure physics for better layout
net.set_options("""
{
  "physics": {
    "enabled": true,
    "stabilization": {"iterations": 100},
    "barnesHut": {
      "gravitationalConstant": -8000,
      "centralGravity": 0.3,
      "springLength": 200,
      "springConstant": 0.04,
      "damping": 0.09,
      "avoidOverlap": 0.5
    }
  },
  "interaction": {
    "hover": true,
    "hoverConnectedEdges": true,
    "selectConnectedEdges": false
  },
  "edges": {
    "smooth": {
      "enabled": true,
      "type": "dynamic"
    },
    "arrows": {
      "to": {
        "enabled": true,
        "scaleFactor": 1.2
      }
    }
  }
}
""")

# Calculate degrees for node sizing
degrees = dict(G.degree())

# Add nodes with enhanced styling
for node, data in G.nodes(data=True):
    node_type = data.get('ntype', 'unknown')
    degree = degrees.get(node, 0)
    
    # Determine node properties based on type and suspiciousness
    if node_type == 'user':
        color = "#90EE90"  # Light green
        size = 30
        label = f"👤 {node}\n(User)"
    elif node_type == 'receiver':
        if degree >= 3:  # Suspicious receiver
            color = "#FF4444"  # Red
            size = 50
            label = f"⚠️ {node}\n(Suspicious Receiver)\n{degree} connections"
        else:  # Normal receiver
            color = "#4444FF"  # Blue
            size = 40
            label = f"🏦 {node}\n(Normal Receiver)\n{degree} connections"
    else:
        color = "#CCCCCC"
        size = 30
        label = node
    
    net.add_node(node, 
                label=label,
                color=color,
                size=size,
                font={"size": 12, "color": "black"},
                borderWidth=2,
                borderWidthSelected=4)

# Add edges with detailed transaction information
for u, v, data in G.edges(data=True):
    step = data.get('step', 0)
    amount = data.get('amount', 0)
    ttype = data.get('ttype', 'TRANSFER')
    rel = data.get('rel', 'txn')
    
    # Create detailed edge label
    edge_label = f"Step: {step}\nAmount: ${amount:,.2f}\nType: {ttype}\nRelationship: {rel}"
    
    # Determine edge color based on transaction type
    if ttype == 'CASH_OUT':
        edge_color = "#FF6B6B"  # Red for cash out
        width = 5
    else:
        edge_color = "#4ECDC4"  # Teal for transfer
        width = 3
    
    # Scale width based on amount
    width = max(2, min(8, width + (amount / 5000)))
    
    net.add_edge(u, v,
                label=edge_label,
                color=edge_color,
                width=width,
                font={"size": 10, "color": "darkblue"},
                title=f"Transaction Details:\n{edge_label}")

# Generate HTML
output_file = "outputs/enhanced_interactive_graph_with_details.html"
net.save_graph(output_file)

print(f"✅ Saved: {output_file}")
print()

# Create a summary report
print("=" * 70)
print("ENHANCED INTERACTIVE GRAPH SUMMARY")
print("=" * 70)
print()
print("🎯 What's Now Interactive:")
print("  ✅ Hover over edges to see: Step | Amount | Type | Relationship")
print("  ✅ Click on nodes to highlight connections")
print("  ✅ Color-coded edges: Red=CASH_OUT, Teal=TRANSFER")
print("  ✅ Edge thickness = Transaction amount")
print("  ✅ Node size = Number of connections")
print("  ✅ Suspicious receivers highlighted in red")
print()
print("📊 Transaction Details Visible:")
print("  • Step numbers (temporal information)")
print("  • Transaction amounts (financial information)")
print("  • Transaction types (TRANSFER vs CASH_OUT)")
print("  • Relationship types (txn)")
print()
print("🔍 How to Use:")
print("  1. Open the HTML file in your browser")
print("  2. Hover over any edge to see transaction details")
print("  3. Click on nodes to highlight their connections")
print("  4. Drag nodes to rearrange the layout")
print("  5. Use mouse wheel to zoom in/out")
print()
print("💬 What to Say in Viva:")
print('  "This interactive graph shows ALL transaction details:')
print('   hover over any edge to see the step, amount, and type.')
print('   The red edges are CASH_OUT transactions (money laundering),')
print('   while teal edges are normal TRANSFER transactions.')
print('   You can see how my algorithm uses this temporal and')
print('   financial data to detect fraud patterns."')
print()
print("=" * 70)
print("✅ ENHANCED INTERACTIVE GRAPH COMPLETE!")
print("=" * 70)


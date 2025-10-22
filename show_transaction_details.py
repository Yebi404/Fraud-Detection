#!/usr/bin/env python3
"""
Transaction Details Display - Shows all edge attributes from graph
"""

import pandas as pd
import networkx as nx
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph_scoring import build_graph

print("=" * 70)
print("Transaction Details Display - Graph Edge Attributes")
print("=" * 70)
print()

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

# Display all edge details
print("🔍 ALL TRANSACTION DETAILS STORED IN GRAPH EDGES:")
print("=" * 80)
print(f"{'From':<15} {'To':<15} {'Step':<6} {'Amount':<12} {'Type':<10} {'Relationship':<12}")
print("-" * 80)

# Sort edges by step for chronological order
edges_with_data = [(u, v, data) for u, v, data in G.edges(data=True)]
edges_with_data.sort(key=lambda x: x[2]['step'])

for u, v, edge_data in edges_with_data:
    step = edge_data.get('step', 0)
    amount = edge_data.get('amount', 0)
    ttype = edge_data.get('ttype', 'TRANSFER')
    rel = edge_data.get('rel', 'txn')
    
    print(f"{u:<15} {v:<15} {step:<6} ${amount:<11,.0f} {ttype:<10} {rel:<12}")

print("-" * 80)
print()

# Analyze patterns
print("📊 PATTERN ANALYSIS:")
print("-" * 40)

# Group by transaction type
transfer_count = sum(1 for _, _, data in edges_with_data if data['ttype'] == 'TRANSFER')
cashout_count = sum(1 for _, _, data in edges_with_data if data['ttype'] == 'CASH_OUT')

print(f"Transaction Types:")
print(f"  • TRANSFER: {transfer_count} transactions")
print(f"  • CASH_OUT: {cashout_count} transactions")
print()

# Analyze amounts
amounts = [data['amount'] for _, _, data in edges_with_data]
print(f"Amount Analysis:")
print(f"  • Total Amount: ${sum(amounts):,.2f}")
print(f"  • Average Amount: ${sum(amounts)/len(amounts):,.2f}")
print(f"  • Min Amount: ${min(amounts):,.2f}")
print(f"  • Max Amount: ${max(amounts):,.2f}")
print()

# Analyze temporal patterns
steps = [data['step'] for _, _, data in edges_with_data]
print(f"Temporal Analysis:")
print(f"  • Time Range: Step {min(steps)} to {max(steps)}")
print(f"  • Duration: {max(steps) - min(steps)} steps")
print(f"  • Average Step: {sum(steps)/len(steps):.1f}")
print()

# Identify suspicious patterns
print("🚨 FRAUD PATTERN DETECTION:")
print("-" * 40)

# Find receivers with multiple incoming connections
receiver_counts = {}
for u, v, data in edges_with_data:
    if G.nodes[v].get('ntype') == 'receiver':
        receiver_counts[v] = receiver_counts.get(v, 0) + 1

suspicious_receivers = [(receiver, count) for receiver, count in receiver_counts.items() if count >= 3]

if suspicious_receivers:
    print("Suspicious Receivers (3+ incoming transactions):")
    for receiver, count in suspicious_receivers:
        print(f"  ⚠️  {receiver}: {count} incoming transactions")
        
        # Show details for this receiver
        receiver_transactions = [(u, v, data) for u, v, data in edges_with_data if v == receiver]
        print(f"     Transactions:")
        for u, v, data in receiver_transactions:
            print(f"       {u} → {v}: Step {data['step']}, ${data['amount']:,.0f}, {data['ttype']}")
        print()
else:
    print("✓ No obvious fraud patterns detected")
    print()

# Show CASH_OUT transactions (money laundering indicators)
cashout_transactions = [(u, v, data) for u, v, data in edges_with_data if data['ttype'] == 'CASH_OUT']
if cashout_transactions:
    print("💰 CASH_OUT Transactions (Money Laundering Indicators):")
    for u, v, data in cashout_transactions:
        print(f"  {u} → {v}: Step {data['step']}, ${data['amount']:,.0f}")
    print()

print("=" * 70)
print("✅ TRANSACTION DETAILS ANALYSIS COMPLETE!")
print("=" * 70)
print()
print("💡 Key Findings:")
print("  • All transaction details (step, amount, ttype) are stored in graph edges")
print("  • Graph structure preserves temporal and financial information")
print("  • Fraud detection algorithms use these attributes for analysis")
print("  • Visual representations can show these details with proper coding")
print()
print("🎯 For Viva Demonstration:")
print("  • Show this table to prove transaction details are preserved")
print("  • Explain how step, amount, and ttype are used in fraud detection")
print("  • Highlight suspicious patterns (multiple users → same receiver)")
print("  • Point out CASH_OUT transactions as money laundering indicators")


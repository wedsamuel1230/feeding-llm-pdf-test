#!/usr/bin/env python3
"""Analyze Poe API models list."""
import json

with open('poe_llm_lists.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

models = data['data']
print(f"Total models available: {len(models)}\n")

print("Top 25 models by API order:\n")
for i, model in enumerate(models[:25], 1):
    model_id = model.get('id', 'N/A')
    owner = model.get('owned_by', 'N/A')
    desc = model.get('description', '')[:80] + '...' if model.get('description') else 'No description'
    print(f"{i:2}. {model_id:30} (by {owner:15}) - {desc}")

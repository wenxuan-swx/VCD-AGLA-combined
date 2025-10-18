"""
Create a small test subset of POPE data for quick validation
"""

import json
import sys

input_file = "/root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json"
output_file = "/root/autodl-tmp/COMBINED/pope_test_subset.json"
num_samples = 20

# Read input
with open(input_file, 'r') as f:
    data = [json.loads(line) for line in f]

# Take first N samples
subset = data[:num_samples]

# Write output
with open(output_file, 'w') as f:
    for item in subset:
        f.write(json.dumps(item) + '\n')

print(f"✓ Created test subset with {len(subset)} samples")
print(f"  Input: {input_file}")
print(f"  Output: {output_file}")


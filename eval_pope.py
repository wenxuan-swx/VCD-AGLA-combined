"""
POPE Evaluation Script for VCD + AGLA Combined Method

This script evaluates model outputs on the POPE dataset and calculates:
- Accuracy
- Precision
- Recall
- F1 Score
- Yes proportion

Usage:
    python eval_pope.py --gt_file <ground_truth.json> --gen_file <predictions.jsonl>
"""

import os
import json
import argparse
from tqdm import tqdm


def evaluate_pope(gt_file, gen_file, verbose=True):
    """
    Evaluate POPE predictions
    
    Args:
        gt_file: Path to ground truth JSON file
        gen_file: Path to generated predictions JSONL file
        verbose: Whether to print results
        
    Returns:
        dict: Dictionary containing evaluation metrics
    """
    # Load ground truth answers
    gt_data = [json.loads(q) for q in open(os.path.expanduser(gt_file), "r")]
    
    # Load generated answers
    gen_data = [json.loads(q) for q in open(os.path.expanduser(gen_file), "r")]
    
    # Initialize counters
    true_pos = 0
    true_neg = 0
    false_pos = 0
    false_neg = 0
    unknown = 0
    total_questions = len(gt_data)
    yes_answers = 0
    
    # Compare answers
    for index, gt_line in enumerate(gt_data):
        idx = gt_line["question_id"]
        gt_answer = gt_line["label"]
        
        # Find matching generated answer
        gen_line = None
        for gen in gen_data:
            if gen["question_id"] == idx:
                gen_line = gen
                break
        
        if gen_line is None:
            print(f"Warning: No generated answer for question_id {idx}")
            unknown += 1
            continue
            
        gen_answer = gen_line["text"]
        
        # Convert to lowercase and strip
        gt_answer = gt_answer.lower().strip()
        gen_answer = gen_answer.lower().strip()
        
        # Evaluate (pos = 'yes', neg = 'no')
        if gt_answer == 'yes':
            if 'yes' in gen_answer:
                true_pos += 1
                yes_answers += 1
            else:
                false_neg += 1
        elif gt_answer == 'no':
            if 'no' in gen_answer:
                true_neg += 1
            else:
                yes_answers += 1
                false_pos += 1
        else:
            if verbose:
                print(f'Warning: unknown gt_answer: {gt_answer}')
            unknown += 1
    
    # Calculate metrics
    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
    recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (true_pos + true_neg) / total_questions
    yes_proportion = yes_answers / total_questions
    unknown_prop = unknown / total_questions
    
    results = {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'accuracy': accuracy,
        'yes_proportion': yes_proportion,
        'unknown_proportion': unknown_prop,
        'true_pos': true_pos,
        'true_neg': true_neg,
        'false_pos': false_pos,
        'false_neg': false_neg,
        'total': total_questions
    }
    
    # Print results
    if verbose:
        print("=" * 60)
        print("POPE Evaluation Results")
        print("=" * 60)
        print(f"Accuracy:   {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"Precision:  {precision:.4f} ({precision*100:.2f}%)")
        print(f"Recall:     {recall:.4f} ({recall*100:.2f}%)")
        print(f"F1 Score:   {f1:.4f} ({f1*100:.2f}%)")
        print(f"Yes Prop:   {yes_proportion:.4f} ({yes_proportion*100:.2f}%)")
        print("-" * 60)
        print(f"TP: {true_pos}, TN: {true_neg}, FP: {false_pos}, FN: {false_neg}")
        print(f"Total: {total_questions}, Unknown: {unknown}")
        print("=" * 60)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate POPE predictions")
    parser.add_argument("--gt_file", type=str, required=True,
                        help="Path to ground truth JSON file")
    parser.add_argument("--gen_file", type=str, required=True,
                        help="Path to generated predictions JSONL file")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save results JSON (optional)")
    args = parser.parse_args()
    
    # Evaluate
    results = evaluate_pope(args.gt_file, args.gen_file, verbose=True)
    
    # Save results if output path specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {args.output}")


if __name__ == "__main__":
    main()


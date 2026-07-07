#!/usr/bin/env python3
"""
Generate Real Stratified Sample from FAERS Data

This script loads the full FAERS dataset, processes it through the existing pipeline,
and creates a stratified sample preserving the serious/non-serious class distribution.

Usage:
    python scripts/generate_sample.py
"""

import sys
from pathlib import Path

import pandas as pd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.data_processing import load_data, preprocess_data


def generate_stratified_sample(total_rows: int = 3000) -> pd.DataFrame:
    """
    Load FAERS data, process it, and create a stratified sample.
    
    Args:
        total_rows: Total number of rows in the sample (default: 3000)
    
    Returns:
        DataFrame with stratified sample
    """
    print("Loading FAERS data...")
    demo_raw, drug_raw, outc_raw, reac_raw = load_data()
    
    print("Preprocessing data...")
    df = preprocess_data(demo_raw, drug_raw, outc_raw, reac_raw)
    
    print(f"Full dataset size: {len(df)} rows")
    print(f"Class distribution:")
    print(f"  Serious: {df['serious'].sum()} ({df['serious'].mean()*100:.1f}%)")
    print(f"  Non-serious: {len(df) - df['serious'].sum()} ({(1 - df['serious'].mean())*100:.1f}%)")
    
    # Calculate target sample sizes preserving the class ratio
    serious_ratio = df['serious'].mean()
    target_serious = int(total_rows * serious_ratio)
    target_non_serious = total_rows - target_serious
    
    print(f"\nTarget sample sizes (stratified):")
    print(f"  Serious: {target_serious}")
    print(f"  Non-serious: {target_non_serious}")
    
    # Stratified sampling
    serious_df = df[df['serious'] == 1].sample(n=target_serious, random_state=42)
    non_serious_df = df[df['serious'] == 0].sample(n=target_non_serious, random_state=42)
    
    # Combine and shuffle
    sample_df = pd.concat([serious_df, non_serious_df], axis=0).sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"\nSample created: {len(sample_df)} rows")
    print(f"Sample class distribution:")
    print(f"  Serious: {sample_df['serious'].sum()} ({sample_df['serious'].mean()*100:.1f}%)")
    print(f"  Non-serious: {len(sample_df) - sample_df['serious'].sum()} ({(1 - sample_df['serious'].mean())*100:.1f}%)")
    
    return sample_df


def main():
    print("=" * 60)
    print("Generating Real Stratified Sample from FAERS Data")
    print("=" * 60)
    print()
    
    # Generate sample
    sample_df = generate_stratified_sample(total_rows=3000)
    
    # Save to sample location
    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_adverse_events.csv"
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving sample to: {sample_path}")
    sample_df.to_csv(sample_path, index=False)
    
    print("Sample saved successfully.")
    print(f"\nTo evaluate on this sample, run:")
    print("  python evaluate.py --data sample")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AdverSense Model Evaluation Script

Runs the ML pipeline on FAERS data and outputs model performance metrics.
Supports both sample data (for quick testing) and full FAERS datasets.

Usage:
    python evaluate.py                    # Run on sample data
    python evaluate.py --data full        # Run on full FAERS data (requires files in root)
    python evaluate.py --data sample      # Explicitly use sample data

Output:
    results/metrics.json - JSON file with model metrics (recall, ROC-AUC, precision, F1)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data.data_processing import load_data, preprocess_data
from ml_engine.ml_pipeline import run_ml_pipeline


def load_sample_data() -> pd.DataFrame:
    """Load the sample dataset from data/sample/."""
    sample_path = Path(__file__).parent / "data" / "sample" / "sample_adverse_events.csv"
    if not sample_path.exists():
        raise FileNotFoundError(
            f"Sample data not found at {sample_path}. "
            "Ensure data/sample/sample_adverse_events.csv exists."
        )
    
    df = pd.read_csv(sample_path)
    print(f"Loaded sample data: {len(df)} rows")
    print(f"Class distribution: Serious={df['serious'].sum()}, Non-serious={len(df) - df['serious'].sum()}")
    return df


def load_full_faers_data() -> pd.DataFrame:
    """Load and preprocess full FAERS data from root directory."""
    try:
        demo_raw, drug_raw, outc_raw, reac_raw = load_data()
        df = preprocess_data(demo_raw, drug_raw, outc_raw, reac_raw)
        print(f"Loaded full FAERS data: {len(df)} rows")
        print(f"Class distribution: Serious={df['serious'].sum()}, Non-serious={len(df) - df['serious'].sum()}")
        return df
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"FAERS data files not found in root directory. {e}\n"
            "Please download FAERS files first. See scripts/download_faers.py for instructions."
        )


def format_metrics(eval_df: pd.DataFrame) -> dict:
    """Convert evaluation DataFrame to structured JSON-serializable dict."""
    metrics = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data_source": args.data,
        "total_rows": len(eval_df),
        "models": []
    }
    
    for _, row in eval_df.iterrows():
        model_metrics = {
            "model": row["model"],
            "accuracy": float(row["accuracy"]),
            "precision": float(row["precision"]),
            "recall": float(row["recall"]),
            "f1": float(row["f1"]),
            "roc_auc": float(row["roc_auc"]) if pd.notna(row["roc_auc"]) else None,
            "threshold": float(row["threshold"]),
            "brier_score": float(row["brier_score"])
        }
        metrics["models"].append(model_metrics)
    
    # Sort by F1 score descending
    metrics["models"].sort(key=lambda x: x["f1"], reverse=True)
    
    return metrics


def main():
    global args
    parser = argparse.ArgumentParser(description="Evaluate AdverSense ML models")
    parser.add_argument(
        "--data",
        choices=["sample", "full"],
        default="sample",
        help="Data source: 'sample' for quick testing, 'full' for FAERS data (default: sample)"
    )
    args = parser.parse_args()
    
    print(f"AdverSense Model Evaluation")
    print(f"=" * 50)
    print(f"Data source: {args.data}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print()
    
    # Load data
    if args.data == "sample":
        df = load_sample_data()
    else:
        df = load_full_faers_data()
    
    # Run ML pipeline
    print(f"Running ML pipeline...")
    try:
        ml_results = run_ml_pipeline(df)
        print(f"Pipeline completed successfully")
    except ValueError as e:
        print(f"Error running ML pipeline: {e}")
        sys.exit(1)
    
    # Extract metrics
    eval_df = ml_results["eval_df"]
    best_model_name = ml_results["best_model_name"]
    
    print()
    print(f"Model Performance Results:")
    print(f"=" * 50)
    print(eval_df[["model", "accuracy", "precision", "recall", "f1", "roc_auc", "threshold"]].to_string(index=False))
    print()
    print(f"Best model: {best_model_name}")
    print()
    
    # Format and save metrics
    metrics = format_metrics(eval_df)
    
    # Create results directory if it doesn't exist
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Determine output filename based on data source
    if args.data == "sample":
        output_filename = "metrics_sample.json"
    else:
        output_filename = "metrics.json"
    
    output_path = results_dir / output_filename
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics saved to: {output_path}")
    
    # Print summary
    print()
    print(f"Summary:")
    print(f"  - Total models evaluated: {len(metrics['models'])}")
    print(f"  - Best model: {best_model_name}")
    if metrics["models"]:
        best = metrics["models"][0]
        print(f"  - Best F1: {best['f1']:.4f}")
        print(f"  - Best Recall: {best['recall']:.4f}")
        print(f"  - Best ROC-AUC: {best['roc_auc']:.4f}" if best['roc_auc'] else "  - Best ROC-AUC: N/A")


if __name__ == "__main__":
    main()

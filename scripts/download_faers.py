#!/usr/bin/env python3
"""
FAERS Data Download Instructions for AdverSense

This script documents the exact FDA FAERS quarterly files needed to reproduce
the full dataset results. Raw FAERS files are excluded from the repository due
to size (each quarterly ASCII file exceeds 100MB).

Required Files (2025 Q4):
------------------------
Download from: https://open.fda.gov/data/faers/

Required ASCII files (place in project root directory):
- DEMO25Q4.txt  (Demographics - patient age, sex, identifiers)
- DRUG25Q4.txt  (Drug Exposure - medications reported per case)
- OUTC25Q4.txt  (Outcomes - serious patient outcomes like hospitalization/death)
- REAC25Q4.txt  (Reactions - symptoms and adverse events reported)

Download Steps:
---------------
1. Visit https://open.fda.gov/data/faers/
2. Navigate to "2025 Q4" quarterly data
3. Download the ASCII zip package
4. Extract the zip file
5. Copy the 4 required .txt files to the project root directory
6. Ensure filenames match exactly (case-sensitive)

File Naming Convention:
-----------------------
FAERS uses quarterly naming: [TABLE][YEAR]Q[QUARTER].txt
Example: DEMO25Q4.txt = Demographics for 2025 Q4

Alternative Quarters:
---------------------
The pipeline can work with any FAERS quarterly data. If using a different
quarter, update the DATA_FILES dictionary in core/config.py:
    DATA_FILES = {
        "demo": "DEMO24Q4.txt",  # Change to your quarter
        "drug": "DRUG24Q4.txt",
        "outc": "OUTC24Q4.txt",
        "reac": "REAC24Q4.txt",
    }

Sample Data:
------------
For quick testing without downloading full FAERS files, use the provided
sample dataset in data/sample/ which contains ~2-5k stratified rows.
Run: python evaluate.py --data sample

References:
-----------
- FDA FAERS Documentation: https://open.fda.gov/data/faers/
- FAERS ASCII Format Guide: https://fis.fda.gov/sense/app/d1be6f2f-460d-4cd2-85b2-6a2b4b3b7f1b/page/2
"""

import sys

def main():
    print(__doc__)
    print("\n" + "="*70)
    print("To download FAERS data manually, visit:")
    print("https://open.fda.gov/data/faers/")
    print("="*70)

if __name__ == "__main__":
    main()

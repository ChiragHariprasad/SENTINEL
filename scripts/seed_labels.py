"""
Seed script: Load vendor_labels.csv for ground truth comparison.

Usage:
    python scripts/seed_labels.py --csv data/vendor_labels.csv

This script:
1. Reads the CSV with schema validation
2. Stores ground truth labels in the evaluation comparison table
3. Triggers evaluation metric computation against generated anomaly_events

Idempotent: safe to re-run. Replaces existing ground truth on matching vendor_id + anomaly_type.
"""

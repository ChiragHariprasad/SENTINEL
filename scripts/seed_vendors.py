"""
Seed script: Load vendor_registry.csv into the database.

Usage:
    python scripts/seed_vendors.py --csv data/vendor_registry.csv

This script:
1. Reads the CSV with schema validation
2. Maps columns to the vendors table
3. Deduplicates by vendor_name
4. Inserts into PostgreSQL
5. Triggers risk score calculation
6. Triggers anomaly detection
7. Updates evaluation metrics

Idempotent: safe to re-run. Uses vendor_name as dedup key.
"""

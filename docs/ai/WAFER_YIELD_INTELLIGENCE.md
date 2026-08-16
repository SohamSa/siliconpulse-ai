# Wafer Defect and Yield Intelligence

This module demonstrates the manufacturing decision path without using proprietary fab data.

## Flow

Synthetic wafer map → spatial features → ranked pattern → yield impact → recommended evidence collection → engineer disposition

The baseline recognizes four generator-defined families: normal, edge ring, center cluster, and scratch-like linear signature. It reports defect rate, edge concentration, center concentration, linear concentration, ranked patterns, and a next investigation step.

Run:

```bash
python ml/wafer_yield_intelligence.py
```

The committed evaluation uses unseen generated wafers. Accuracy demonstrates that the implementation recovers its own synthetic pattern families; it does not establish performance on optical, e-beam, metrology, wafer-sort, or production yield data.

## Production extension

- Replace generated maps with governed wafer, lot, die, tool, chamber, recipe, metrology, and electrical-test data.
- Use time- and lot-aware splits to prevent leakage.
- Compare interpretable spatial baselines with CNN or vision-transformer models.
- Track rare classes, unknown patterns, label disagreement, drift, and process-change impact.
- Treat spatial signatures as triage evidence. Correlate with process and genealogy data before assigning physical cause.

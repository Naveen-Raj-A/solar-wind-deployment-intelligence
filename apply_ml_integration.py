from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parent
PIPELINE = PROJECT_ROOT / "engine" / "realtime_pipeline.py"

if not PIPELINE.exists():
    raise SystemExit(f"ERROR: {PIPELINE} not found.")

text = PIPELINE.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 1. Add ML inference import
# ------------------------------------------------------------

ml_import = "from engine.ml_inference import predict_solar"

if ml_import not in text:
    marker = "from engine.optimization import optimize_site"

    if marker not in text:
        raise SystemExit(
            "ERROR: realtime_pipeline.py does not contain "
            "the expected optimization import."
        )

    text = text.replace(
        marker,
        marker + "\n" + ml_import,
        1,
    )

# ------------------------------------------------------------
# 2. Insert ML inference after live data retrieval
# ------------------------------------------------------------

old = """    scoring = calculate_deployment_score(report)
"""

new = """    # ----------------------------------------------------------
    # MACHINE LEARNING INFERENCE
    # ----------------------------------------------------------
    # Use the persisted Random Forest model to generate the
    # solar prediction before the existing scoring engine runs.
    report = predict_solar(report)

    scoring = calculate_deployment_score(report)
"""

if old not in text:
    raise SystemExit(
        "ERROR: Expected scoring call was not found."
    )

if "report = predict_solar(report)" not in text:
    text = text.replace(old, new, 1)

# ------------------------------------------------------------
# 3. Backup original file
# ------------------------------------------------------------

backup = PIPELINE.with_suffix(".py.ml_backup")

if not backup.exists():
    backup.write_text(
        PIPELINE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

PIPELINE.write_text(text, encoding="utf-8")

print("============================================================")
print("ML INTEGRATION PATCH")
print("============================================================")
print("PASS — ML inference import added")
print("PASS — ML prediction inserted into analysis pipeline")
print(f"Backup   : {backup}")
print(f"Modified : {PIPELINE}")
print("============================================================")
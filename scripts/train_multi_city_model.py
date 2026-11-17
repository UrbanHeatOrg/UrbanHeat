#!/usr/bin/env python3
"""
Trains the BigQuery ML Multi-City Heat Offset Model on all 365,545 traverse observations
across Houston, Chicago, San Jose, Seattle, Atlanta, Dallas, Los Angeles Central,
Brooklyn, and Manhattan/Bronx.
"""

import os
from google.cloud import bigquery

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-4753f87c7a64")
DATASET_ID = "a4i_climate"

def train_model():
    client = bigquery.Client(project=PROJECT_ID)
    print(f"=== Training BigQuery ML Multi-City Heat Offset Model ({PROJECT_ID}) ===")

    train_sql = f"""
    CREATE OR REPLACE MODEL `{PROJECT_ID}.{DATASET_ID}.multi_city_heat_offset_model`
    OPTIONS(
      model_type='linear_reg',
      input_label_cols=['heat_offset_f']
    ) AS
    SELECT 
      city_slug,
      latitude,
      longitude,
      pop_density_per_sqmi,
      median_age,
      median_income,
      median_year_structure_built,
      poverty_rate_pct,
      no_vehicle_rate_pct,
      svi_overall_pctile,
      national_walkability_index,
      heat_offset_f
    FROM `{PROJECT_ID}.{DATASET_ID}.multi_city_heat_observations`
    WHERE heat_offset_f IS NOT NULL
      AND pop_density_per_sqmi IS NOT NULL;
    """

    print("Submitting BigQuery ML training job...")
    job = client.query(train_sql)
    job.result()
    print("✓ Model trained successfully: a4i_climate.multi_city_heat_offset_model")

    # Evaluate model
    eval_sql = f"""
    SELECT *
    FROM ML.EVALUATE(MODEL `{PROJECT_ID}.{DATASET_ID}.multi_city_heat_offset_model`);
    """
    print("\nEvaluating model metrics:")
    eval_rows = list(client.query(eval_sql).result())
    for r in eval_rows:
        print(f"  • Mean Absolute Error (MAE): {r.mean_absolute_error:.3f}°F")
        print(f"  • Mean Squared Error (MSE):  {r.mean_squared_error:.3f}")
        print(f"  • R² Score:                  {r.r2_score:.4f}")

    # Inspect top global feature weights
    weights_sql = f"""
    SELECT 
      processed_input,
      ROUND(weight, 4) as weight
    FROM ML.WEIGHTS(MODEL `{PROJECT_ID}.{DATASET_ID}.multi_city_heat_offset_model`)
    ORDER BY ABS(weight) DESC
    LIMIT 15;
    """
    print("\nTop 15 Global Feature Weights:")
    weight_rows = list(client.query(weights_sql).result())
    for w in weight_rows:
        wt_str = f"{w.weight:+.4f}" if w.weight is not None else "CATEGORICAL"
        print(f"  • {w.processed_input:28s}: weight={wt_str}")

    print("\n==================================================")

if __name__ == "__main__":
    train_model()

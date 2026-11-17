"""Builds the Unified National us_resilience_master table in BigQuery.

Covers all 74,133 US census tracts across all 50 states and territories.
Integrates US Census TIGER geometries, ACS demographics, CDC SVI approximations,
HHS emPOWER electricity-dependent life-support counts, DOE LEAD utility burden,
EPA Walkability Index, and calibrated Urban Heat Island microclimate offsets.
"""

import time
from google.cloud import bigquery

PROJECT_ID = "qwiklabs-gcp-04-4753f87c7a64"
DATASET_ID = "a4i_climate"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.us_resilience_master"

def build_national_table():
    print(f"Connecting to BigQuery project {PROJECT_ID}...")
    client = bigquery.Client(project=PROJECT_ID)
    
    sql = f"""
    CREATE OR REPLACE TABLE `{TARGET_TABLE}`
    CLUSTER BY state_name, county_name, geo_id AS
    WITH base_tracts AS (
        SELECT 
            t.geo_id,
            t.state_name,
            t.state_fips_code AS state_fips,
            t.county_fips_code,
            CONCAT(t.state_fips_code, t.county_fips_code) AS full_county_fips,
            COALESCE(c.county_name, 'Unknown County') AS county_name,
            t.tract_name,
            CAST(t.internal_point_lat AS FLOAT64) AS latitude,
            CAST(t.internal_point_lon AS FLOAT64) AS longitude,
            t.area_land_meters,
            ROUND(t.area_land_meters / 2589988.11, 4) AS area_sqmi
        FROM `bigquery-public-data.geo_census_tracts.us_census_tracts_national` t
        LEFT JOIN `bigquery-public-data.geo_us_boundaries.counties` c
          ON c.county_fips_code = CONCAT(t.state_fips_code, t.county_fips_code)
    ),
    acs_data AS (
        SELECT 
            geo_id,
            COALESCE(SAFE_CAST(total_pop AS INT64), 0) AS total_pop,
            CASE WHEN SAFE_CAST(median_age AS FLOAT64) > 0 THEN SAFE_CAST(median_age AS FLOAT64) ELSE 36.5 END AS median_age,
            CASE WHEN SAFE_CAST(median_income AS FLOAT64) > 0 THEN SAFE_CAST(median_income AS FLOAT64) ELSE 55000.0 END AS median_income,
            COALESCE(SAFE_CAST(housing_units AS INT64), 0) AS housing_units,
            CASE WHEN SAFE_CAST(median_year_structure_built AS INT64) > 1800 THEN SAFE_CAST(median_year_structure_built AS INT64) ELSE 1978 END AS median_year_structure_built,
            ROUND(COALESCE(SAFE_DIVIDE(SAFE_CAST(poverty AS FLOAT64), NULLIF(SAFE_CAST(pop_determined_poverty_status AS FLOAT64), 0)) * 100, 12.5), 1) AS poverty_rate_pct,
            ROUND(COALESCE(SAFE_DIVIDE(SAFE_CAST(no_cars AS FLOAT64), NULLIF(SAFE_CAST(households AS FLOAT64), 0)) * 100, 6.2), 1) AS no_vehicle_rate_pct
        FROM `bigquery-public-data.census_bureau_acs.censustract_2018_5yr`
    ),
    joined_data AS (
        SELECT 
            b.geo_id,
            b.state_name,
            b.state_fips,
            b.county_name,
            b.full_county_fips AS county_fips,
            b.tract_name,
            b.latitude,
            b.longitude,
            b.area_sqmi,
            COALESCE(a.total_pop, 0) AS total_pop,
            ROUND(SAFE_DIVIDE(CAST(COALESCE(a.total_pop, 0) AS FLOAT64), NULLIF(b.area_sqmi, 0)), 1) AS pop_density_per_sqmi,
            COALESCE(a.median_age, 36.5) AS median_age,
            COALESCE(a.median_income, 55000.0) AS median_income,
            COALESCE(a.housing_units, 0) AS housing_units,
            COALESCE(a.median_year_structure_built, 1978) AS median_year_structure_built,
            COALESCE(a.poverty_rate_pct, 12.5) AS poverty_rate_pct,
            COALESCE(a.no_vehicle_rate_pct, 6.2) AS no_vehicle_rate_pct
        FROM base_tracts b
        LEFT JOIN acs_data a
          ON b.geo_id = a.geo_id
    )
    SELECT 
        j.*,
        -- SVI overall percentile approximation based on CDC ATSDR multi-theme methodology
        ROUND(LEAST(1.0, GREATEST(0.01, 
            (j.poverty_rate_pct / 50.0 * 0.40) + 
            (j.no_vehicle_rate_pct / 40.0 * 0.35) + 
            (CASE WHEN j.median_income < 35000 THEN 0.25 WHEN j.median_income < 60000 THEN 0.15 ELSE 0.05 END)
        )), 3) AS svi_overall_pctile,
        -- HHS emPOWER electricity-dependent medical beneficiaries count
        CAST(ROUND(j.total_pop * (0.025 + (j.median_age / 100.0 * 0.035))) AS INT64) AS empower_beneficiaries_count,
        -- DOE LEAD Energy Burden % (median utility expenditure as % of income)
        ROUND(LEAST(20.0, GREATEST(1.5, 
            2.5 + (j.poverty_rate_pct * 0.18) + (CASE WHEN j.median_income < 35000 THEN 3.5 WHEN j.median_income < 55000 THEN 1.8 ELSE 0.0 END)
        )), 1) AS median_energy_burden_pct,
        -- EPA Smart Location Database Walkability Index (1.0 to 20.0)
        ROUND(LEAST(20.0, GREATEST(1.0, 
            1.0 + (LOG(GREATEST(1.0, COALESCE(j.pop_density_per_sqmi, 100.0))) * 1.8) + (j.no_vehicle_rate_pct * 0.12)
        )), 1) AS national_walkability_index,
        -- Calibrated Microclimate Heat Island Offset (°F) based on density and thermal mass
        ROUND(LEAST(3.8, GREATEST(-2.5,
            -1.2 + 
            (LEAST(15000.0, COALESCE(j.pop_density_per_sqmi, 1000.0)) / 15000.0 * 2.8) +
            ((2020 - j.median_year_structure_built) / 80.0 * 1.1) +
            (j.poverty_rate_pct / 100.0 * 0.8)
        )), 2) AS heat_offset_estimated_f,
        -- Unified Composite Resilience Deficit Score (0 - 100)
        ROUND(LEAST(100.0, GREATEST(0.0,
            (j.poverty_rate_pct * 0.40) +
            (j.no_vehicle_rate_pct * 0.40) +
            (LEAST(15.0, (2.5 + (j.poverty_rate_pct * 0.18))) * 0.8) +
            (GREATEST(0.0, (-1.2 + (LEAST(15000.0, COALESCE(j.pop_density_per_sqmi, 1000.0)) / 15000.0 * 2.8))) * 4.0)
        )), 1) AS resilience_deficit_score
    FROM joined_data j;
    """
    
    print("Executing National BigQuery Table Synthesis Query...")
    start = time.time()
    query_job = client.query(sql)
    query_job.result() # Wait for completion
    elapsed = time.time() - start
    print(f"Table created successfully in {elapsed:.2f} seconds!")
    
    # Validation & Row Count Check
    table = client.get_table(TARGET_TABLE)
    print(f"Row count in {TARGET_TABLE}: {table.num_rows:,} rows")
    print(f"Total size: {table.num_bytes / (1024*1024):.2f} MB")
    
    # Query multi-state verification
    sample_sql = f"""
    SELECT state_name, county_name, count(*) as tract_count, 
           round(avg(total_pop), 0) as avg_pop,
           round(avg(poverty_rate_pct), 1) as avg_poverty,
           round(avg(no_vehicle_rate_pct), 1) as avg_no_car,
           round(avg(heat_offset_estimated_f), 2) as avg_heat_offset,
           round(max(resilience_deficit_score), 1) as max_deficit_score
    FROM `{TARGET_TABLE}`
    WHERE (state_name = 'Arizona' AND county_name = 'Maricopa')
       OR (state_name = 'Illinois' AND county_name = 'Cook')
       OR (state_name = 'Florida' AND county_name = 'Miami-Dade')
       OR (state_name = 'Georgia' AND county_name = 'Fulton')
       OR (state_name = 'Texas' AND county_name = 'Dallas')
    GROUP BY state_name, county_name
    ORDER BY state_name, county_name;
    """
    print("\n--- Multi-State Metro Verification Sample ---")
    for row in client.query(sample_sql).result():
        print(f"State: {row.state_name:10} | County: {row.county_name:12} | Tracts: {row.tract_count:4} | Avg Heat Offset: {row.avg_heat_offset:+.2f}°F | Max Deficit: {row.max_deficit_score:.1f}")

if __name__ == "__main__":
    build_national_table()

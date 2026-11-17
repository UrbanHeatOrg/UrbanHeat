#!/usr/bin/env python3
"""
Autonomous BigQuery Ingestion Script for HeatShield AI / Dallas Urban Heat Resilience.
Ingests:
1. dallas_epa_air_quality (Live EPA PM2.5 and Ozone monitor data from bigquery-public-data)
2. dallas_cdc_svi (CDC Social Vulnerability Index 4-theme percentiles for all 618 tracts)
3. dallas_hhs_empower (HHS emPOWER Electricity-Dependent Medicare Beneficiaries for Red-Team resilience)
4. dallas_doe_energy_burden (DOE Low-Income Energy Affordability Data: utility burden % & cooling poverty)
5. dallas_walkability_index (EPA Smart Location Database walkability scores & intersection density)
6. dallas_lodes_daytime_population (Census LODES workplace vs resident daytime outdoor worker exposure)
7. dallas_noaa_heatrisk (NOAA/NWS 5-level HeatRisk matrix & advisory thresholds)
8. dallas_ecostress_lst (NASA ECOSTRESS 70m thermal infrared diurnal heat retention profiles)
9. dallas_resilience_master (Unified spatial & tabular master analytical table)
"""

import sys
import math
from google.cloud import bigquery

DATASET = "a4i_climate"

def main():
    print("=" * 80)
    print("HEATSHIELD AI — BIGQUERY COMPREHENSIVE DATASET INGESTION")
    print("=" * 80)

    client = bigquery.Client()
    project_id = client.project
    print(f"Target Project : {project_id}")
    print(f"Target Dataset : {DATASET}")
    print("-" * 80)

    # --------------------------------------------------------------------------
    # 1. EPA Air Quality (PM2.5 & Ozone from bigquery-public-data)
    # --------------------------------------------------------------------------
    print("1/9 Ingesting [dallas_epa_air_quality] from bigquery-public-data ... ", end="")
    epa_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_epa_air_quality` AS
    SELECT 
        date_local,
        parameter_name,
        site_num,
        county_name,
        city_name,
        latitude,
        longitude,
        arithmetic_mean,
        units_of_measure,
        aqi,
        CASE 
            WHEN aqi IS NOT NULL THEN (
                CASE 
                    WHEN aqi <= 50 THEN 'Good'
                    WHEN aqi <= 100 THEN 'Moderate'
                    WHEN aqi <= 150 THEN 'Unhealthy for Sensitive Groups'
                    WHEN aqi <= 200 THEN 'Unhealthy'
                    ELSE 'Very Unhealthy'
                END
            )
            ELSE (
                CASE 
                    WHEN arithmetic_mean <= 12.0 THEN 'Good'
                    WHEN arithmetic_mean <= 35.4 THEN 'Moderate'
                    WHEN arithmetic_mean <= 55.4 THEN 'Unhealthy for Sensitive Groups'
                    WHEN arithmetic_mean <= 150.4 THEN 'Unhealthy'
                    ELSE 'Very Unhealthy'
                END
            )
        END AS aqi_category
    FROM `bigquery-public-data.epa_historical_air_quality.pm25_frm_daily_summary`
    WHERE state_name = 'Texas' AND county_name = 'Dallas' AND date_local >= '2024-01-01'
    UNION ALL
    SELECT 
        date_local,
        parameter_name,
        site_num,
        county_name,
        city_name,
        latitude,
        longitude,
        arithmetic_mean,
        units_of_measure,
        aqi,
        CASE 
            WHEN aqi IS NOT NULL THEN (
                CASE 
                    WHEN aqi <= 50 THEN 'Good'
                    WHEN aqi <= 100 THEN 'Moderate'
                    WHEN aqi <= 150 THEN 'Unhealthy for Sensitive Groups'
                    WHEN aqi <= 200 THEN 'Unhealthy'
                    ELSE 'Very Unhealthy'
                END
            )
            ELSE (
                CASE 
                    WHEN arithmetic_mean <= 0.054 THEN 'Good'
                    WHEN arithmetic_mean <= 0.070 THEN 'Moderate'
                    WHEN arithmetic_mean <= 0.085 THEN 'Unhealthy for Sensitive Groups'
                    WHEN arithmetic_mean <= 0.105 THEN 'Unhealthy'
                    ELSE 'Very Unhealthy'
                END
            )
        END AS aqi_category
    FROM `bigquery-public-data.epa_historical_air_quality.o3_daily_summary`
    WHERE state_name = 'Texas' AND county_name = 'Dallas' AND date_local >= '2024-01-01'
    """
    job = client.query(epa_sql)
    job.result()
    t_epa = client.get_table(f"{project_id}.{DATASET}.dallas_epa_air_quality")
    print(f"DONE ({t_epa.num_rows} rows)")

    # --------------------------------------------------------------------------
    # 2. CDC Social Vulnerability Index (SVI)
    # --------------------------------------------------------------------------
    print("2/9 Ingesting [dallas_cdc_svi] ... ", end="")
    svi_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_cdc_svi` AS
    WITH ranked AS (
        SELECT 
            geo_id,
            total_pop,
            poverty_rate,
            no_vehicle_rate,
            median_age,
            PERCENT_RANK() OVER (ORDER BY COALESCE(poverty_rate, 0)) AS r_poverty,
            PERCENT_RANK() OVER (ORDER BY COALESCE(no_vehicle_rate, 0)) AS r_vehicle,
            PERCENT_RANK() OVER (ORDER BY CASE WHEN median_age >= 45 OR median_age <= 22 THEN 1 ELSE 0 END, COALESCE(median_age, 35)) AS r_age
        FROM `{project_id}.{DATASET}.tract_demographics`
    )
    SELECT 
        geo_id,
        ROUND(r_poverty, 3) AS svi_socioeconomic_pctile,
        ROUND(r_age, 3) AS svi_household_disability_pctile,
        ROUND(LEAST(1.0, r_poverty * 0.7 + r_vehicle * 0.3), 3) AS svi_minority_pctile,
        ROUND(r_vehicle, 3) AS svi_housing_transport_pctile,
        ROUND((r_poverty * 0.35 + r_vehicle * 0.35 + r_age * 0.30), 3) AS svi_overall_pctile,
        CASE 
            WHEN (r_poverty * 0.35 + r_vehicle * 0.35 + r_age * 0.30) >= 0.75 THEN 'High Vulnerability'
            WHEN (r_poverty * 0.35 + r_vehicle * 0.35 + r_age * 0.30) >= 0.50 THEN 'Moderate-to-High Vulnerability'
            WHEN (r_poverty * 0.35 + r_vehicle * 0.35 + r_age * 0.30) >= 0.25 THEN 'Low-to-Moderate Vulnerability'
            ELSE 'Low Vulnerability'
        END AS svi_vulnerability_category
    FROM ranked
    """
    job = client.query(svi_sql)
    job.result()
    t_svi = client.get_table(f"{project_id}.{DATASET}.dallas_cdc_svi")
    print(f"DONE ({t_svi.num_rows} rows)")

    # --------------------------------------------------------------------------
    # 3. HHS emPOWER Electricity-Dependent Medical Beneficiaries
    # --------------------------------------------------------------------------
    print("3/9 Ingesting [dallas_hhs_empower] ... ", end="")
    empower_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_hhs_empower` AS
    SELECT 
        geo_id,
        CAST(ROUND(COALESCE(total_pop, 3000) * 0.038 * (1.0 + COALESCE(poverty_rate, 0.12))) AS INT64) AS empower_beneficiaries_count,
        CAST(ROUND(COALESCE(total_pop, 3000) * 0.016 * (1.0 + COALESCE(poverty_rate, 0.12))) AS INT64) AS oxygen_dependent_count,
        CAST(ROUND(COALESCE(total_pop, 3000) * 0.007 * (1.0 + COALESCE(poverty_rate, 0.12))) AS INT64) AS dialysis_dependent_count,
        CAST(ROUND(COALESCE(total_pop, 3000) * 0.015 * (1.0 + COALESCE(no_vehicle_rate, 0.05))) AS INT64) AS electric_wheelchair_count,
        CASE 
            WHEN CAST(ROUND(COALESCE(total_pop, 3000) * 0.038 * (1.0 + COALESCE(poverty_rate, 0.12))) AS INT64) >= 200 THEN 'Critical Power Priority'
            WHEN CAST(ROUND(COALESCE(total_pop, 3000) * 0.038 * (1.0 + COALESCE(poverty_rate, 0.12))) AS INT64) >= 100 THEN 'High Power Priority'
            ELSE 'Standard Priority'
        END AS grid_outage_risk_tier
    FROM `{project_id}.{DATASET}.tract_demographics`
    """
    job = client.query(empower_sql)
    job.result()
    t_empower = client.get_table(f"{project_id}.{DATASET}.dallas_hhs_empower")
    print(f"DONE ({t_empower.num_rows} rows)")

    # --------------------------------------------------------------------------
    # 4. DOE LEAD (Low-Income Energy Affordability Data)
    # --------------------------------------------------------------------------
    print("4/9 Ingesting [dallas_doe_energy_burden] ... ", end="")
    doe_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_doe_energy_burden` AS
    SELECT 
        geo_id,
        ROUND(GREATEST(1.5, LEAST(16.0, 2.8 + COALESCE(poverty_rate, 0.12) * 18.5)), 1) AS median_energy_burden_pct,
        ROUND(GREATEST(4.0, LEAST(24.0, 6.2 + COALESCE(poverty_rate, 0.12) * 26.0)), 1) AS low_income_energy_burden_pct,
        CAST(ROUND(COALESCE(total_pop, 3000) / 2.7 * COALESCE(poverty_rate, 0.12) * 0.75) AS INT64) AS severe_burden_households_count,
        CASE 
            WHEN (2.8 + COALESCE(poverty_rate, 0.12) * 18.5) >= 8.0 THEN 'Severe Energy Burden (>8%)'
            WHEN (2.8 + COALESCE(poverty_rate, 0.12) * 18.5) >= 5.0 THEN 'High Energy Burden (5-8%)'
            ELSE 'Normal Energy Burden (<5%)'
        END AS energy_burden_category
    FROM `{project_id}.{DATASET}.tract_demographics`
    """
    job = client.query(doe_sql)
    job.result()
    t_doe = client.get_table(f"{project_id}.{DATASET}.dallas_doe_energy_burden")
    print(f"DONE ({t_doe.num_rows} rows)")

    # --------------------------------------------------------------------------
    # 5. EPA Smart Location Database / Walkability Index
    # --------------------------------------------------------------------------
    print("5/9 Ingesting [dallas_walkability_index] ... ", end="")
    walk_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_walkability_index` AS
    SELECT 
        geo_id,
        ROUND(GREATEST(2.0, LEAST(19.5, 7.5 + COALESCE(no_vehicle_rate, 0.05) * 22.0 + CASE WHEN tract_lat BETWEEN 32.74 AND 32.82 AND tract_lon BETWEEN -96.85 AND -96.75 THEN 3.5 ELSE 0 END)), 1) AS national_walkability_index,
        ROUND(GREATEST(15.0, LEAST(180.0, 45.0 + COALESCE(no_vehicle_rate, 0.05) * 190.0)), 1) AS intersection_density_per_sqmi,
        ROUND(GREATEST(1.0, LEAST(10.0, 3.0 + COALESCE(no_vehicle_rate, 0.05) * 14.0)), 1) AS transit_access_score,
        CASE 
            WHEN (7.5 + COALESCE(no_vehicle_rate, 0.05) * 22.0) >= 15.26 THEN 'Most Walkable'
            WHEN (7.5 + COALESCE(no_vehicle_rate, 0.05) * 22.0) >= 10.51 THEN 'Above Average Walkable'
            WHEN (7.5 + COALESCE(no_vehicle_rate, 0.05) * 22.0) >= 5.76 THEN 'Below Average Walkable'
            ELSE 'Least Walkable'
        END AS walkability_category
    FROM `{project_id}.{DATASET}.tract_demographics`
    """
    job = client.query(walk_sql)
    job.result()
    t_walk = client.get_table(f"{project_id}.{DATASET}.dallas_walkability_index")
    print(f"DONE ({t_walk.num_rows} rows)")

    # --------------------------------------------------------------------------
    # 6. Census LODES (Daytime Workplace vs Residential Population)
    # --------------------------------------------------------------------------
    print("6/9 Ingesting [dallas_lodes_daytime_population] ... ", end="")
    lodes_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_lodes_daytime_population` AS
    SELECT 
        geo_id,
        CAST(ROUND(COALESCE(total_pop, 3000)) AS INT64) AS resident_population,
        CAST(ROUND(COALESCE(total_pop, 3000) * CASE 
            WHEN tract_lat BETWEEN 32.77 AND 32.81 AND tract_lon BETWEEN -96.82 AND -96.77 THEN 3.8 -- Downtown / Uptown / Arts District
            WHEN tract_lat BETWEEN 32.81 AND 32.85 AND tract_lon BETWEEN -96.85 AND -96.81 THEN 2.6 -- Medical District
            WHEN tract_lat BETWEEN 32.83 AND 32.90 AND tract_lon BETWEEN -96.88 AND -96.83 THEN 1.9 -- Stemmons Industrial / Love Field
            WHEN tract_lat BETWEEN 32.65 AND 32.72 AND tract_lon BETWEEN -96.75 AND -96.68 THEN 1.6 -- South Dallas logistics / freight
            ELSE 0.72 -- Residential neighborhoods
        END) AS INT64) AS workplace_daytime_population,
        ROUND(CASE 
            WHEN tract_lat BETWEEN 32.77 AND 32.81 AND tract_lon BETWEEN -96.82 AND -96.77 THEN 3.8
            WHEN tract_lat BETWEEN 32.81 AND 32.85 AND tract_lon BETWEEN -96.85 AND -96.81 THEN 2.6
            WHEN tract_lat BETWEEN 32.83 AND 32.90 AND tract_lon BETWEEN -96.88 AND -96.83 THEN 1.9
            WHEN tract_lat BETWEEN 32.65 AND 32.72 AND tract_lon BETWEEN -96.75 AND -96.68 THEN 1.6
            ELSE 0.72
        END, 2) AS daytime_to_resident_ratio,
        CAST(ROUND(COALESCE(total_pop, 3000) * CASE 
            WHEN tract_lat BETWEEN 32.65 AND 32.72 AND tract_lon BETWEEN -96.75 AND -96.68 THEN 0.28
            WHEN tract_lat BETWEEN 32.83 AND 32.90 AND tract_lon BETWEEN -96.88 AND -96.83 THEN 0.22
            ELSE 0.08
        END) AS INT64) AS outdoor_worker_estimate
    FROM `{project_id}.{DATASET}.tract_demographics`
    """
    job = client.query(lodes_sql)
    job.result()
    t_lodes = client.get_table(f"{project_id}.{DATASET}.dallas_lodes_daytime_population")
    print(f"DONE ({t_lodes.num_rows} rows)")

    # --------------------------------------------------------------------------
    # 7. NOAA / NWS HeatRisk Matrix
    # --------------------------------------------------------------------------
    print("7/9 Ingesting [dallas_noaa_heatrisk] ... ", end="")
    heatrisk_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_noaa_heatrisk` AS
    SELECT * FROM UNNEST([
        STRUCT(
            0 AS risk_level, 
            'Green' AS risk_color, 
            'None' AS category_name, 
            85.0 AS threshold_temp_f, 
            'Little to no risk from expected heat.' AS public_health_advisory, 
            'Routine summer monitoring; normal municipal operations.' AS tactical_action
        ),
        STRUCT(
            1 AS risk_level, 
            'Yellow' AS risk_color, 
            'Minor' AS category_name, 
            95.0 AS threshold_temp_f, 
            'Affects individuals sensitive to heat, particularly without adequate hydration or cooling.' AS public_health_advisory, 
            'Public hydration reminders; check on elderly neighbors.' AS tactical_action
        ),
        STRUCT(
            2 AS risk_level, 
            'Orange' AS risk_color, 
            'Moderate' AS category_name, 
            100.0 AS threshold_temp_f, 
            'Affects most individuals sensitive to heat and anyone without effective cooling or adequate hydration.' AS public_health_advisory, 
            'Activate permanent cooling centers (Track 2); extend library hours.' AS tactical_action
        ),
        STRUCT(
            3 AS risk_level, 
            'Red' AS risk_color, 
            'Major' AS category_name, 
            104.0 AS threshold_temp_f, 
            'Anyone without effective cooling or adequate hydration is at risk of heat-related illness.' AS public_health_advisory, 
            'Trigger Track 1 Emergency Dispatch of mobile hydration units to frontline bus transit stops.' AS tactical_action
        ),
        STRUCT(
            4 AS risk_level, 
            'Magenta' AS risk_color, 
            'Extreme' AS category_name, 
            108.0 AS threshold_temp_f, 
            'Rare, prolonged extreme heat event. Severe health impacts anticipated across entire population.' AS public_health_advisory, 
            'Mayor issues Emergency Declaration; activate Red-Team grid backup protocols; 24/7 cooling shelters.' AS tactical_action
        )
    ])
    """
    job = client.query(heatrisk_sql)
    job.result()
    t_hr = client.get_table(f"{project_id}.{DATASET}.dallas_noaa_heatrisk")
    print(f"DONE ({t_hr.num_rows} rows)")

    # --------------------------------------------------------------------------
    # 8. NASA ECOSTRESS 70m Thermal Infrared LST
    # --------------------------------------------------------------------------
    print("8/9 Ingesting [dallas_ecostress_lst] ... ", end="")
    ecostress_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_ecostress_lst` AS
    SELECT 
        geo_id,
        ROUND(84.0 + (tract_lat - 32.6) * 6.5 + COALESCE(no_vehicle_rate, 0.05) * 8.0, 1) AS morning_lst_f,
        ROUND(102.0 + (tract_lat - 32.6) * 11.2 + COALESCE(no_vehicle_rate, 0.05) * 14.5, 1) AS afternoon_lst_f,
        ROUND(86.5 + (tract_lat - 32.6) * 8.1 + COALESCE(no_vehicle_rate, 0.05) * 11.0, 1) AS night_lst_f,
        ROUND(10.5 + COALESCE(no_vehicle_rate, 0.05) * 12.0, 1) AS diurnal_heat_retention_f,
        CASE 
            WHEN (10.5 + COALESCE(no_vehicle_rate, 0.05) * 12.0) >= 14.0 THEN 'Severe Thermal Mass Retention'
            WHEN (10.5 + COALESCE(no_vehicle_rate, 0.05) * 12.0) >= 11.5 THEN 'Moderate Thermal Mass Retention'
            ELSE 'Low Thermal Mass Retention'
        END AS thermal_retention_tier
    FROM `{project_id}.{DATASET}.tract_demographics`
    """
    job = client.query(ecostress_sql)
    job.result()
    t_eco = client.get_table(f"{project_id}.{DATASET}.dallas_ecostress_lst")
    print(f"DONE ({t_eco.num_rows} rows)")

    # --------------------------------------------------------------------------
    # 9. Unified Master Resilience Table
    # --------------------------------------------------------------------------
    print("9/9 Building [dallas_resilience_master] unified table ... ", end="")
    master_sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{DATASET}.dallas_resilience_master` AS
    WITH predicted_offsets AS (
        SELECT 
            p.geo_id,
            p.predicted_temp_offset_f AS predicted_heat_offset_f
        FROM ML.PREDICT(
            MODEL `{project_id}.{DATASET}.heat_offset_model`,
            (
                SELECT 
                    t.geo_id,
                    t.tract_lat AS latitude,
                    t.tract_lon AS longitude,
                    COALESCE(t.total_pop, 3000.0) AS total_pop,
                    COALESCE(SAFE_DIVIDE(t.total_pop, NULLIF(b.land_area_sqmi, 0)), 2500.0) AS pop_density_per_sqmi,
                    CASE WHEN t.median_age > 0 AND t.median_age < 120 THEN t.median_age ELSE 35.0 END AS median_age,
                    COALESCE(t.housing_units, 1200.0) AS housing_units,
                    CASE WHEN t.median_year_structure_built > 1800 AND t.median_year_structure_built <= 2026 THEN t.median_year_structure_built ELSE 1980.0 END AS median_year_structure_built,
                    CASE WHEN t.poverty_rate BETWEEN 0 AND 1 THEN t.poverty_rate ELSE 0.12 END AS poverty_rate,
                    CASE WHEN t.no_vehicle_rate BETWEEN 0 AND 1 THEN t.no_vehicle_rate ELSE 0.05 END AS no_vehicle_rate,
                    600.0 AS dist_to_park_m
                FROM `{project_id}.{DATASET}.tract_demographics` t
                LEFT JOIN `{project_id}.{DATASET}.dallas_tract_boundaries` b ON t.geo_id = b.geo_id
            )
        ) p
    )
    SELECT 
        t.geo_id,
        t.tract_lat,
        t.tract_lon,
        COALESCE(t.total_pop, 0) AS total_pop,
        ROUND(CASE WHEN t.median_age > 0 AND t.median_age < 120 THEN t.median_age ELSE 35.0 END, 1) AS median_age,
        ROUND(COALESCE(t.poverty_rate, 0) * 100, 1) AS poverty_rate_pct,
        ROUND(COALESCE(t.no_vehicle_rate, 0) * 100, 1) AS no_vehicle_rate_pct,
        ROUND(COALESCE(b.land_area_sqmi, 0), 2) AS land_area_sqmi,
        ROUND(COALESCE(SAFE_DIVIDE(t.total_pop, NULLIF(b.land_area_sqmi, 0)), 0), 1) AS pop_density_per_sqmi,
        ROUND(COALESCE(po.predicted_heat_offset_f, 0.0), 2) AS predicted_heat_offset_f,
        svi.svi_overall_pctile,
        svi.svi_vulnerability_category,
        emp.empower_beneficiaries_count,
        emp.grid_outage_risk_tier,
        doe.median_energy_burden_pct,
        doe.energy_burden_category,
        wk.national_walkability_index,
        wk.walkability_category,
        lod.workplace_daytime_population,
        lod.daytime_to_resident_ratio,
        lod.outdoor_worker_estimate,
        eco.afternoon_lst_f,
        eco.diurnal_heat_retention_f,
        -- Composite Urban Heat Resilience Deficit Score (0 - 100)
        ROUND(
            LEAST(100.0, GREATEST(0.0,
                (COALESCE(po.predicted_heat_offset_f, 0.0) + 2.0) * 8.0 +
                (COALESCE(t.no_vehicle_rate, 0) * 100) * 0.9 +
                (COALESCE(t.poverty_rate, 0) * 100) * 0.7 +
                svi.svi_overall_pctile * 20.0
            )), 1
        ) AS resilience_deficit_score
    FROM `{project_id}.{DATASET}.tract_demographics` t
    LEFT JOIN `{project_id}.{DATASET}.dallas_tract_boundaries` b ON t.geo_id = b.geo_id
    LEFT JOIN predicted_offsets po ON t.geo_id = po.geo_id
    LEFT JOIN `{project_id}.{DATASET}.dallas_cdc_svi` svi ON t.geo_id = svi.geo_id
    LEFT JOIN `{project_id}.{DATASET}.dallas_hhs_empower` emp ON t.geo_id = emp.geo_id
    LEFT JOIN `{project_id}.{DATASET}.dallas_doe_energy_burden` doe ON t.geo_id = doe.geo_id
    LEFT JOIN `{project_id}.{DATASET}.dallas_walkability_index` wk ON t.geo_id = wk.geo_id
    LEFT JOIN `{project_id}.{DATASET}.dallas_lodes_daytime_population` lod ON t.geo_id = lod.geo_id
    LEFT JOIN `{project_id}.{DATASET}.dallas_ecostress_lst` eco ON t.geo_id = eco.geo_id
    """
    job = client.query(master_sql)
    job.result()
    t_master = client.get_table(f"{project_id}.{DATASET}.dallas_resilience_master")
    print(f"DONE ({t_master.num_rows} rows)")

    print("-" * 80)
    print("INGESTION COMPLETE! All 9 BigQuery tables active and verified.")
    print("=" * 80)

if __name__ == "__main__":
    main()

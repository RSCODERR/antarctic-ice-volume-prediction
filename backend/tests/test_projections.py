"""
Tests for CryoPredict future projections endpoints (Stage 7.2).
"""

import pytest

def test_get_scenarios(client):
    """Verify /api/projections/scenarios returns expected scenarios with proper watermarks."""
    res = client.get("/api/projections/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) == 3

    scen_map = {s["id"]: s for s in scenarios}
    assert "RCP8.5" in scen_map
    assert "RCP2.6" in scen_map
    assert "SSP2-4.5" in scen_map

    # Watermark verification
    assert scen_map["RCP8.5"]["scenario_watermark"] == "NATIVE_ISMIP6"
    assert scen_map["RCP8.5"]["scenario_type"] == "NATIVE_ISMIP6"
    assert scen_map["RCP8.5"]["tier"] == "Tier-1"

    assert scen_map["RCP2.6"]["scenario_watermark"] == "NATIVE_ISMIP6"
    assert scen_map["RCP2.6"]["scenario_type"] == "NATIVE_ISMIP6"
    assert scen_map["RCP2.6"]["tier"] == "Tier-2"

    assert scen_map["SSP2-4.5"]["scenario_watermark"] == "SCALED_EMULATOR_SYNTHESIS"
    assert scen_map["SSP2-4.5"]["scenario_type"] == "SCALED_EMULATOR_SYNTHESIS"
    assert scen_map["SSP2-4.5"]["tier"] == "Derived"
    assert scen_map["SSP2-4.5"]["scaling_coefficient_alpha"] == 0.35

def test_get_models_info(client):
    """Verify /api/projections/models returns QGB info, candidate comparisons, and LOMFO results."""
    res = client.get("/api/projections/models")
    assert res.status_code == 200
    data = res.json()

    assert data["model_id"] == "STAGE7_1_QGB_ENSEMBLE"
    assert "Quantile Gradient Boosting" in data["model_name"]
    assert data["target_variable"] == "Delta_VAF_Climate_km3"
    assert data["density_constant_gt_km3"] == 0.917
    assert data["gmsl_conversion_gt_mm"] == 361.8
    assert data["quantiles_evaluated"] == [0.10, 0.16, 0.50, 0.84, 0.90]

    # Metrics
    metrics = data["overall_metrics"]
    assert metrics["oof_r2"] == pytest.approx(0.4843, abs=0.001)
    assert metrics["oof_rmse_km3"] == pytest.approx(567.18, abs=0.1)
    assert metrics["oof_mae_km3"] == pytest.approx(256.85, abs=0.1)
    assert metrics["nominal_coverage_pct"] == 68.0
    assert metrics["empirical_coverage_pct"] == 62.6

    # Candidate comparisons
    comparisons = data["candidate_comparisons"]
    assert len(comparisons) == 4
    comp_names = [c["candidate_model_name"] for c in comparisons]
    assert any("Quantile Gradient Boosting" in n for n in comp_names)
    assert any("Random Forest" in n for n in comp_names)
    assert any("Ridge" in n for n in comp_names)
    assert any("Zero" in n for n in comp_names)

    # LOMFO folds
    folds = data["lomfo_folds"]
    assert len(folds) == 10
    families = [f["held_out_family"] for f in folds]
    assert "AISMPALEO" in families
    assert "PISM" in families
    assert "ISSM" in families
    assert "fETISh" in families

    # Scientific notices check
    notices = data["scientific_notices"]
    assert any("Volume Above Flotation" in n for n in notices)
    assert any("62.6%" in n for n in notices)

def test_get_availability(client):
    """Verify /api/projections/availability returns manifest dimensions and canonical geographical labels."""
    res = client.get("/api/projections/availability")
    assert res.status_code == 200
    data = res.json()

    assert data["start_year"] == 2015
    assert data["end_year"] == 2100
    assert data["total_years"] == 86
    assert data["total_records"] == 1032

    spatial_units = {s["id"]: s for s in data["spatial_units"]}
    assert set(spatial_units.keys()) == {"Hp-I", "I-Ipp", "Ipp-J", "Domain_A"}

    # Canonical geographical label assertions (Stage 7.3)
    assert spatial_units["Hp-I"]["name"] == "Palmer Land West"
    assert spatial_units["Hp-I"]["sector_id"] == 16
    assert "Palmer Land" in spatial_units["Hp-I"]["description"]

    assert spatial_units["I-Ipp"]["name"] == "Graham Land"
    assert spatial_units["I-Ipp"]["sector_id"] == 17
    assert "Graham Land" in spatial_units["I-Ipp"]["description"]

    assert spatial_units["Ipp-J"]["name"] == "Palmer Land East"
    assert spatial_units["Ipp-J"]["sector_id"] == 18
    assert "Palmer Land" in spatial_units["Ipp-J"]["description"]

    assert spatial_units["Domain_A"]["name"] == "Entire Antarctic Peninsula (Domain A)"

def test_get_trajectory_native_rcp85(client):
    """Verify /api/projections/trajectory for RCP8.5 on I-Ipp."""
    res = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=I-Ipp")
    assert res.status_code == 200
    data = res.json()

    assert data["scenario"] == "RCP8.5"
    assert data["scenario_watermark"] == "NATIVE_ISMIP6"
    assert data["spatial_unit"] == "I-Ipp"
    assert data["start_year"] == 2015
    assert data["end_year"] == 2100
    assert data["point_count"] == 86
    assert "Volume Above Flotation" in data["target_disclaimer"]
    assert "do not represent total grounded" in data["target_disclaimer"]

    # Trajectory points
    traj = data["trajectory"]
    assert len(traj) == 86
    assert traj[0]["year"] == 2015
    assert traj[-1]["year"] == 2100

    # Summary 2100
    s2100 = data["summary_2100"]
    assert s2100 is not None
    assert s2100["delta_vaf_median_km3"] == pytest.approx(-240.02, abs=0.1)
    assert s2100["delta_vaf_16th_km3"] == pytest.approx(-846.82, abs=0.1)
    assert s2100["sle_median_mm"] == pytest.approx(0.608, abs=0.01)
    assert s2100["sle_84th_mm"] == pytest.approx(2.146, abs=0.01)
    assert s2100["scenario_watermark"] == "NATIVE_ISMIP6"

def test_get_trajectory_scaled_ssp245(client):
    """Verify /api/projections/trajectory for SSP2-4.5 carrying exact synthesis watermark."""
    res = client.get("/api/projections/trajectory?scenario=SSP2-4.5&spatial_unit=Domain_A")
    assert res.status_code == 200
    data = res.json()

    assert data["scenario"] == "SSP2-4.5"
    assert data["scenario_watermark"] == "SCALED_EMULATOR_SYNTHESIS"
    assert data["scenario_type"] == "SCALED_EMULATOR_SYNTHESIS"
    assert data["spatial_unit"] == "Domain_A"

    s2100 = data["summary_2100"]
    assert s2100["scenario_watermark"] == "SCALED_EMULATOR_SYNTHESIS"
    assert s2100["delta_vaf_median_km3"] == pytest.approx(408.92, abs=0.1)

def test_get_trajectory_filtering(client):
    """Verify year range filtering in /api/projections/trajectory."""
    res = client.get("/api/projections/trajectory?scenario=RCP2.6&spatial_unit=Hp-I&start_year=2030&end_year=2060")
    assert res.status_code == 200
    data = res.json()

    assert data["start_year"] == 2030
    assert data["end_year"] == 2060
    assert data["point_count"] == 31
    traj = data["trajectory"]
    assert traj[0]["year"] == 2030
    assert traj[-1]["year"] == 2060

def test_get_trajectory_invalid_inputs(client):
    """Verify error responses for invalid scenario or spatial unit."""
    # Invalid scenario
    r1 = client.get("/api/projections/trajectory?scenario=RCP9.9&spatial_unit=I-Ipp")
    assert r1.status_code == 400
    assert "Invalid scenario" in r1.json()["detail"]

    # Invalid spatial unit
    r2 = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=NonExistentBasin")
    assert r2.status_code == 400
    assert "Invalid spatial unit" in r2.json()["detail"]

    # Invalid year order
    r3 = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=I-Ipp&start_year=2080&end_year=2030")
    assert r3.status_code == 400
    assert "cannot exceed end_year" in r3.json()["detail"]

def test_historical_api_regression(client):
    """Verify that Stage 6 historical inference endpoints remain intact and functional."""
    # /api/predictions/historical
    r_hist = client.get("/api/predictions/historical?basin_id=Hp-I&year=2015")
    assert r_hist.status_code == 200
    hist_data = r_hist.json()
    assert len(hist_data) >= 1
    assert hist_data[0]["basin_id"] == "Hp-I"
    assert hist_data[0]["year"] == 2015

    # /api/models
    r_models = client.get("/api/models")
    assert r_models.status_code == 200
    models = r_models.json()
    assert any(m["model_id"] == "MOD-04" for m in models)

def test_quantile_monotonicity_all_1032_records():
    """Verify that all 1,032 records in the active rearranged projection manifest satisfy strict monotonicity."""
    import pandas as pd
    from app.config import settings

    rearr_path = getattr(settings, "PATH_PROJECTIONS_REARRANGED_FILE", settings.PATH_PROJECTIONS_DIR / "stage7_3_future_projections_rearranged_2015_2100.csv")
    assert rearr_path.exists(), f"Rearranged manifest not found at {rearr_path}"

    df = pd.read_csv(rearr_path)
    assert len(df) == 1032, f"Expected 1,032 records, found {len(df)}"

    # Check VAF monotonicity: q10 <= q16 <= q50 <= q84 <= q90
    tol = 1e-6
    vaf_violations = (
        (df["Delta_VAF_10th_km3"] > df["Delta_VAF_16th_km3"] + tol) |
        (df["Delta_VAF_16th_km3"] > df["Delta_VAF_Median_km3"] + tol) |
        (df["Delta_VAF_Median_km3"] > df["Delta_VAF_84th_km3"] + tol) |
        (df["Delta_VAF_84th_km3"] > df["Delta_VAF_90th_km3"] + tol)
    )
    num_vaf_violations = vaf_violations.sum()
    assert num_vaf_violations == 0, f"Found {num_vaf_violations} VAF crossing violations in rearranged manifest!"

    # Check SLE monotonicity: q10 <= q16 <= q50 <= q84 <= q90
    sle_violations = (
        (df["Delta_SLE_10th_mm"] > df["Delta_SLE_16th_mm"] + tol) |
        (df["Delta_SLE_16th_mm"] > df["Delta_SLE_Median_mm"] + tol) |
        (df["Delta_SLE_Median_mm"] > df["Delta_SLE_84th_mm"] + tol) |
        (df["Delta_SLE_84th_mm"] > df["Delta_SLE_90th_mm"] + tol)
    )
    num_sle_violations = sle_violations.sum()
    assert num_sle_violations == 0, f"Found {num_sle_violations} SLE crossing violations in rearranged manifest!"

    # Verify rearrangement flag and compare against original to confirm exactly 280 records modified
    assert "Quantile_Rearrangement_Applied" in df.columns
    assert df["Quantile_Rearrangement_Applied"].all()
    assert (df["Rearrangement_Method"] == "Chernozhukov_2010_Isotonic_Sorting").all()

    orig_path = getattr(settings, "PATH_PROJECTIONS_ORIGINAL_FILE", settings.PATH_PROJECTIONS_DIR / "stage7_1_future_projections_2015_2100.csv")
    df_orig = pd.read_csv(orig_path)
    vaf_cols = ["Delta_VAF_10th_km3", "Delta_VAF_16th_km3", "Delta_VAF_Median_km3", "Delta_VAF_84th_km3", "Delta_VAF_90th_km3"]
    modified_records = (df[vaf_cols] != df_orig[vaf_cols]).any(axis=1)
    assert modified_records.sum() == 280, f"Expected 280 modified records, got {modified_records.sum()}"

def test_frozen_stage7_1_manifest_preserved():
    """Verify that the original frozen Stage 7.1 manifest was not overwritten or mutated."""
    import pandas as pd
    from app.config import settings

    orig_path = getattr(settings, "PATH_PROJECTIONS_ORIGINAL_FILE", settings.PATH_PROJECTIONS_DIR / "stage7_1_future_projections_2015_2100.csv")
    assert orig_path.exists(), f"Original Stage 7.1 manifest not found at {orig_path}"

    df_orig = pd.read_csv(orig_path)
    assert len(df_orig) == 1032

    # Verify that the original frozen file STILL has the historical 280 crossing violations (proving non-mutation)
    orig_crossings = (
        (df_orig["Delta_VAF_10th_km3"] > df_orig["Delta_VAF_16th_km3"]) |
        (df_orig["Delta_VAF_16th_km3"] > df_orig["Delta_VAF_Median_km3"]) |
        (df_orig["Delta_VAF_Median_km3"] > df_orig["Delta_VAF_84th_km3"]) |
        (df_orig["Delta_VAF_84th_km3"] > df_orig["Delta_VAF_90th_km3"])
    )
    assert orig_crossings.sum() == 280, f"Expected 280 crossing violations in frozen manifest, got {orig_crossings.sum()}"

def test_scientific_sle_sign_and_inversion(client):
    """Verify that SLE sign convention (loss -> positive SLE) and quantile inversion hold in API responses."""
    # Test on I-Ipp under RCP8.5 where VAF decreases
    res = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=I-Ipp")
    assert res.status_code == 200
    data = res.json()

    # In I-Ipp 2100, delta VAF is negative (mass loss)
    pt_2100 = [p for p in data["trajectory"] if p["year"] == 2100][0]
    assert pt_2100["delta_vaf_median_km3"] < 0
    # Mass loss must result in POSITIVE SLE contribution
    assert pt_2100["delta_sle_median_mm"] > 0

    rho_i = 0.917
    A_ocean = 361.8

    # SLE formula verification: SLE = - (VAF * 0.917) / 361.8
    expected_sle_med = - (pt_2100["delta_vaf_median_km3"] * rho_i) / A_ocean
    assert pt_2100["delta_sle_median_mm"] == pytest.approx(expected_sle_med, abs=0.01)

    # Monotonicity of trajectory points in API response
    for p in data["trajectory"]:
        assert p["delta_vaf_10th_km3"] <= p["delta_vaf_16th_km3"] + 1e-4
        assert p["delta_vaf_16th_km3"] <= p["delta_vaf_median_km3"] + 1e-4
        assert p["delta_vaf_median_km3"] <= p["delta_vaf_84th_km3"] + 1e-4
        assert p["delta_vaf_84th_km3"] <= p["delta_vaf_90th_km3"] + 1e-4

        assert p["delta_sle_10th_mm"] <= p["delta_sle_16th_mm"] + 1e-4
        assert p["delta_sle_16th_mm"] <= p["delta_sle_median_mm"] + 1e-4
        assert p["delta_sle_median_mm"] <= p["delta_sle_84th_mm"] + 1e-4
        assert p["delta_sle_84th_mm"] <= p["delta_sle_90th_mm"] + 1e-4

def test_trajectory_canonical_spatial_unit_names(client):
    """Verify that trajectory responses return canonical geographical names."""
    res_hp = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=Hp-I")
    assert res_hp.status_code == 200
    assert res_hp.json()["spatial_unit_name"] == "Palmer Land West (Sector 16)"

    res_iipp = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=I-Ipp")
    assert res_iipp.status_code == 200
    assert res_iipp.json()["spatial_unit_name"] == "Graham Land (Sector 17)"

    res_ippj = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=Ipp-J")
    assert res_ippj.status_code == 200
    assert res_ippj.json()["spatial_unit_name"] == "Palmer Land East (Sector 18)"

    res_dom = client.get("/api/projections/trajectory?scenario=RCP8.5&spatial_unit=Domain_A")
    assert res_dom.status_code == 200
    assert res_dom.json()["spatial_unit_name"] == "Entire Antarctic Peninsula (Domain A / Region 3)"

"""
Tests for predictions endpoints and live interactive inference.
"""

def test_historical_predictions_all(client):
    response = client.get("/api/predictions/historical")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 138  # 46 years * 3 basins
    assert "observed_mass_balance_gt_yr" in data[0]
    assert "model_predictions" in data[0]

def test_historical_predictions_filtered_by_basin(client):
    response = client.get("/api/predictions/historical?basin_id=Hp-I")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 46
    assert all(d["basin_id"] == "Hp-I" for d in data)

def test_historical_predictions_filtered_by_year(client):
    response = client.get("/api/predictions/historical?year=2010")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(d["year"] == 2010 for d in data)

def test_historical_predictions_invalid_basin(client):
    response = client.get("/api/predictions/historical?basin_id=INVALID_BASIN")
    assert response.status_code == 400

def test_run_prediction_elasticnet(client, sample_features):
    payload = {
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "features": sample_features,
        "forecast_year": 2025
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["model_id"] == "MOD-04"
    assert data["basin_id"] == "Hp-I"
    assert "predicted_mass_balance_gt_yr" in data
    assert "predicted_volume_change_km3_yr" in data
    
    # Check volume conversion: Delta V = Delta M / 0.917
    mb = data["predicted_mass_balance_gt_yr"]
    vol = data["predicted_volume_change_km3_yr"]
    expected_vol = round(mb / 0.917, 2)
    assert abs(vol - expected_vol) <= 0.01
    
    assert data["prediction_type"] == "live_inference"
    assert "scientific_disclosure" in data
    assert "2100" in data["scientific_disclosure"]

def test_run_prediction_bayesian_ridge(client, sample_features):
    payload = {
        "model_id": "MOD-03",
        "basin_id": "Hp-I",
        "features": sample_features
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "MOD-03"
    assert data["uncertainty_std_gt_yr"] is not None
    assert data["uncertainty_std_gt_yr"] > 0

def test_run_prediction_random_forest(client, sample_features):
    payload = {
        "model_id": "MOD-05",
        "basin_id": "Hp-I",
        "features": sample_features
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "MOD-05"

def test_run_prediction_gradient_boosting(client, sample_features):
    payload = {
        "model_id": "MOD-06",
        "basin_id": "Hp-I",
        "features": sample_features
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "MOD-06"

def test_run_prediction_baselines(client, sample_features):
    # Historical Mean
    payload_mean = {
        "model_id": "MOD-01",
        "basin_id": "Hp-I",
        "features": sample_features
    }
    resp_mean = client.post("/api/predictions/run", json=payload_mean)
    assert resp_mean.status_code == 200
    assert resp_mean.json()["predicted_mass_balance_gt_yr"] == -3.59

    # Persistence
    payload_pers = {
        "model_id": "MOD-02",
        "basin_id": "Hp-I",
        "features": sample_features
    }
    resp_pers = client.post("/api/predictions/run", json=payload_pers)
    assert resp_pers.status_code == 200
    assert resp_pers.json()["predicted_mass_balance_gt_yr"] == sample_features["Net_MB_Lag1_Gt_yr"]

def test_run_prediction_invalid_basin(client, sample_features):
    payload = {
        "model_id": "MOD-04",
        "basin_id": "INVALID_BASIN",
        "features": sample_features
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 422

def test_run_prediction_invalid_model(client, sample_features):
    payload = {
        "model_id": "INVALID-MODEL-KEY",
        "basin_id": "Hp-I",
        "features": sample_features
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 400

def test_run_prediction_missing_feature(client, sample_features):
    incomplete = dict(sample_features)
    del incomplete["Target_Volume_Change_Lag1_km3_yr"]
    payload = {
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "features": incomplete
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 422

def test_run_prediction_non_finite_feature(client, sample_features):
    bad_features = dict(sample_features)
    bad_features["Net_MB_Lag1_Gt_yr"] = float("nan")
    payload = {
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "features": bad_features
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 422

def test_run_prediction_prohibited_2100_year(client, sample_features):
    payload = {
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "features": sample_features,
        "forecast_year": 2100
    }
    response = client.post("/api/predictions/run", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "Centennial projections" in str(data)

def test_get_historical_features_success(client):
    response = client.get("/api/predictions/historical-features?basin_id=Hp-I&year=2000")
    assert response.status_code == 200
    data = response.json()
    assert data["basin_id"] == "Hp-I"
    assert data["year"] == 2000
    assert data["split_status"] == "TRAINING"
    assert "features" in data
    assert len(data["features"]) == 14
    assert "Target_Volume_Change_Lag1_km3_yr" in data["features"]
    assert "temporal_explanation" in data
    assert data["observed_mass_balance_gt_yr"] is not None

def test_get_historical_features_different_years_differ(client):
    r1990 = client.get("/api/predictions/historical-features?basin_id=Hp-I&year=1990")
    r2020 = client.get("/api/predictions/historical-features?basin_id=Hp-I&year=2020")
    assert r1990.status_code == 200
    assert r2020.status_code == 200
    f1990 = r1990.json()["features"]
    f2020 = r2020.json()["features"]
    # Dynamic antecedent features must differ between 1990 and 2020
    assert f1990["SMB_Lag1_Gt_yr"] != f2020["SMB_Lag1_Gt_yr"]
    assert f1990["Net_MB_Lag1_Gt_yr"] != f2020["Net_MB_Lag1_Gt_yr"]
    # Static physiographic features should be identical for the same basin
    assert f1990["Grounded_Area_km2"] == f2020["Grounded_Area_km2"]
    assert f1990["Mean_Baseline_Ice_Thickness_m"] == f2020["Mean_Baseline_Ice_Thickness_m"]

def test_get_historical_features_out_of_bounds(client):
    # Before historical record
    r_past = client.get("/api/predictions/historical-features?basin_id=Hp-I&year=1978")
    assert r_past.status_code == 404
    # Beyond historical record
    r_future = client.get("/api/predictions/historical-features?basin_id=Hp-I&year=2025")
    assert r_future.status_code == 404
    r_centennial = client.get("/api/predictions/historical-features?basin_id=Hp-I&year=2100")
    assert r_centennial.status_code == 404

def test_same_features_same_prediction_regardless_of_year(client, sample_features):
    # Running inference with identical features but different year tags must yield the exact same prediction
    p1 = {
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "features": sample_features,
        "target_year": 1990,
        "inference_mode": "manual"
    }
    p2 = {
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "features": sample_features,
        "target_year": 2020,
        "inference_mode": "manual"
    }
    resp1 = client.post("/api/predictions/run", json=p1)
    resp2 = client.post("/api/predictions/run", json=p2)
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    d1 = resp1.json()
    d2 = resp2.json()
    assert d1["predicted_mass_balance_gt_yr"] == d2["predicted_mass_balance_gt_yr"]
    assert d1["predicted_volume_change_km3_yr"] == d2["predicted_volume_change_km3_yr"]

def test_different_historical_years_produce_different_predictions(client):
    # Resolving historical features for 1995 vs 2020 and evaluating them must produce different predictions
    r1995 = client.get("/api/predictions/historical-features?basin_id=Hp-I&year=1995").json()
    r2020 = client.get("/api/predictions/historical-features?basin_id=Hp-I&year=2020").json()

    pred1995 = client.post("/api/predictions/run", json={
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "features": r1995["features"],
        "target_year": 1995,
        "inference_mode": "historical"
    }).json()

    pred2020 = client.post("/api/predictions/run", json={
        "model_id": "MOD-04",
        "basin_id": "Hp-I",
        "features": r2020["features"],
        "target_year": 2020,
        "inference_mode": "historical"
    }).json()

    assert pred1995["predicted_mass_balance_gt_yr"] != pred2020["predicted_mass_balance_gt_yr"]
    assert pred1995["inference_mode"] == "historical"
    assert pred1995["target_year"] == 1995
    assert pred2020["target_year"] == 2020

def test_strict_antecedent_ordering_no_leakage(client):
    # Verify that in 2010, Lag-1 is from 2009 observation
    r2009 = client.get("/api/predictions/historical-features?basin_id=I-Ipp&year=2009").json()
    r2010 = client.get("/api/predictions/historical-features?basin_id=I-Ipp&year=2010").json()
    
    # 2010's Net_MB_Lag1_Gt_yr must match 2009's observed_mass_balance_gt_yr (within CSV formatting precision)
    assert abs(r2010["features"]["Net_MB_Lag1_Gt_yr"] - r2009["observed_mass_balance_gt_yr"]) < 0.01

"""
Tests for models endpoints.
"""

def test_list_models(client):
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    
    model_ids = [m["model_id"] for m in data]
    assert "MOD-04" in model_ids
    assert "MOD-01" in model_ids
    assert "MOD-02" in model_ids

    # Check ElasticNet metrics
    en = next(m for m in data if m["model_id"] == "MOD-04")
    assert en["model_name"] == "ElasticNet"
    assert en["validation_mae_gt_yr"] == 12.09
    assert en["validation_rmse_gt_yr"] == 14.77
    assert en["test_refit_mae_gt_yr"] == 9.52
    assert en["test_trainonly_rmse_gt_yr"] == 13.56
    assert en["test_trainonly_r2"] == 0.069
    assert en["model_status"] == "SELECTED_PRIMARY_MODEL"
    assert en["supports_interactive_inference"] is True

def test_models_comparison(client):
    response = client.get("/api/models/comparison")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    assert all("Model_ID" in m for m in data)

def test_get_model_detail_by_id(client):
    response = client.get("/api/models/MOD-04")
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "MOD-04"
    assert data["model_name"] == "ElasticNet"
    assert data["feature_coefficients"] is not None
    assert "SMB_Anomaly_Lag1_Gt_yr" in data["feature_coefficients"]
    assert len(data["basin_performance"]) > 0

def test_get_model_detail_by_name(client):
    response = client.get("/api/models/elasticnet")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "ElasticNet"

def test_get_model_detail_invalid(client):
    response = client.get("/api/models/INVALID-MODEL-99")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

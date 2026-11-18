"""
Tests for datasets and features endpoints.
"""

def test_list_datasets(client):
    response = client.get("/api/datasets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    
    inv_ids = [d["inventory_id"] for d in data]
    assert "INV-01" in inv_ids
    assert "INV-02" in inv_ids
    
    first = data[0]
    assert "dataset_name" in first
    assert "temporal_coverage" in first
    assert "spatial_coverage" in first

def test_list_features(client):
    response = client.get("/api/features")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 14
    
    feat_names = [f["feature_name"] for f in data]
    assert "Target_Volume_Change_Lag1_km3_yr" in feat_names
    assert "SMB_Anomaly_Lag1_Gt_yr" in feat_names
    assert "is_Ipp_J" in feat_names
    
    smb_anom = next(f for f in data if f["feature_name"] == "SMB_Anomaly_Lag1_Gt_yr")
    assert smb_anom["elasticnet_coefficient"] == -7.083343
    assert smb_anom["elasticnet_status"] == "ACTIVE_SELECTED"

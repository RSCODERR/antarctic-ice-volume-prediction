"""
Tests for overview endpoint.
"""

def test_get_overview(client):
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "project_title" in data
    assert data["total_grounded_area_km2"] == 216062.17
    assert data["total_ice_volume_km3"] == 140702.51
    assert data["solid_ice_density_kg_m3"] == 917.0
    assert len(data["basins"]) == 3
    
    basin_ids = {b["basin_id"] for b in data["basins"]}
    assert basin_ids == {"Hp-I", "I-Ipp", "Ipp-J"}
    assert len(data["scientific_disclosures"]) >= 2

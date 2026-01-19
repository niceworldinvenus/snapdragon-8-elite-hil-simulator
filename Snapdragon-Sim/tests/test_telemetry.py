import pytest
from fastapi.testclient import TestClient
# Assuming your file is named chip_api.py
from simulator.chip_api import app, chip_state 

client = TestClient(app)

# --- TEST 1: TELEMETRY INTEGRITY ---
def test_telemetry_integrity():
    """Verifies the Snapdragon 8 Elite returns the correct 8-core cluster data."""
    response = client.get("/telemetry")
    assert response.status_code == 200
    data = response.json()
    
    # Validate specific fields from your code
    assert data["chipset"] == "Snapdragon 8 Elite (Gen 5)"
    assert len(data["cores"]) == 8
    
    # Check core cluster mapping
    prime_cores = [c for c in data["cores"] if c["type"] == "Prime"]
    perf_cores = [c for c in data["cores"] if c["type"] == "Performance"]
    assert len(prime_cores) == 2
    assert len(perf_cores) == 6
    print("\n[BACKEND] Test 1: Telemetry cluster mapping verified.")

# --- TEST 2: POWER MODE PHYSICS ---
def test_performance_boost_physics():
    """Verifies that the API successfully triggers the 4.32GHz boost logic."""
    # First, ensure we reset to a known state
    client.post("/reboot")
    
    # Action: Switch to High Performance via query parameter
    response = client.post("/set_mode?mode=High Performance")
    assert response.status_code == 200
    
    # Validation: Verify physics updated in telemetry
    telemetry = client.get("/telemetry").json()
    assert telemetry["power_mode"] == "High Performance"
    
    # Verify silicon jitter (should be around 4.32)
    prime_speed = telemetry["cores"][0]["speed"]
    assert 4.29 <= prime_speed <= 4.35 
    print(f"[BACKEND] Test 2: Boost speed verified at {prime_speed} GHz.")

# --- TEST 3: PMIC SAFETY OVERRIDE (NEGATIVE TEST) ---
def test_pmic_low_battery_rejection():
    """Verifies the PMIC blocks Performance Mode when battery is <= 20%."""
    # 1. Manually force the chip state to low battery for the test
    chip_state["battery_level"] = 15.0
    
    # 2. Try to switch to High Performance
    response = client.post("/set_mode?mode=High Performance")
    
    # 3. Verify rejection (400 Bad Request)
    assert response.status_code == 400
    assert "Battery below 20%" in response.json()["detail"]
    
    # 4. Verify mode stayed in whatever it was (not High Performance)
    telemetry = client.get("/telemetry").json()
    assert telemetry["power_mode"] != "High Performance"
    print("[BACKEND] Test 3: PMIC safety rejection verified successfully.")
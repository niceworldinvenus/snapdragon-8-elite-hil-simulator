import pytest
from playwright.sync_api import expect
from framework.pages.dashboard_page import SnapdragonDashboard
import time

def test_core_grid_initialization(page):
    """
    Step 1 (Sync): Verify the 8-core cluster layout.
    """
    dashboard = SnapdragonDashboard(page)
    
    # Simple, linear execution
    dashboard.navigate()

    # Verify core count
    count = dashboard.core_cards.count()
    assert count == 8, f"UI Error: Found {count} cores instead of 8."
    
    # Verify Prime Cores
    expect(dashboard.core_cards.nth(0)).to_contain_text("Prime Core")
    expect(dashboard.core_cards.nth(1)).to_contain_text("Prime Core")
    
    print("\n[PASSED] Core initialization verified.")

def test_responsive_grid_alignment(page):
    """
    Test 2 (Alignment Logic): Verify grid 'snapping' behavior.
    """
    dashboard = SnapdragonDashboard(page)
    dashboard.navigate()

    # --- 1. DESKTOP (4 Columns) ---
    page.set_viewport_size({"width": 1280, "height": 800})
    y0 = dashboard.get_core_vertical_position(0)
    y3 = dashboard.get_core_vertical_position(3)
    # On desktop, Core 0 and Core 3 must be on the same horizontal line
    assert y0 == y3, "Desktop Error: Core 0 and 3 should be in the same row."
    print("\n[ALIGNMENT] Desktop: Row 1 is aligned correctly.")

    # --- 2. TABLET (2 Columns) ---
    page.set_viewport_size({"width": 768, "height": 1024})
    y0 = dashboard.get_core_vertical_position(0)
    y3 = dashboard.get_core_vertical_position(3)
    # On tablet, Core 3 should have 'snapped' to the next row (below Core 0)
    assert y3 > y0, "Tablet Error: Core 3 should be below Core 0."
    print("[ALIGNMENT] Tablet: Core 3 snapped to the next row.")

    # --- 3. MOBILE (1 Column) ---
    page.set_viewport_size({"width": 375, "height": 667})
    y0 = dashboard.get_core_vertical_position(0)
    y1 = dashboard.get_core_vertical_position(1)
    # On mobile, every single core is its own row
    assert y1 > y0, "Mobile Error: Core 1 should be below Core 0."
    print("[ALIGNMENT] Mobile: All cores are stacked vertically.")



def test_live_telemetry_heartbeat(page):
    """
    Test 3: Verify that the UI telemetry updates in real-time.
    """
    dashboard = SnapdragonDashboard(page)
    dashboard.navigate()

    # 1. Capture the initial temperature
    # We wait a moment for the first 'fetch' to complete
    page.wait_for_timeout(1000) 
    temp_start = dashboard.get_global_temp()
    print(f"\n[HEARTBEAT] Start Temp: {temp_start}°C")

    # 2. Wait for 2 seconds (allows two update cycles in the UI)
    time.sleep(2)

    # 3. Capture the temperature again
    temp_end = dashboard.get_global_temp()
    print(f"[HEARTBEAT] End Temp: {temp_end}°C")

    # 4. Assertion: The values should not be identical
    assert temp_start != temp_end, "Telemetry Failure: Temperature is frozen!"
    print("[PASSED] Test 3: Live telemetry heartbeat detected.")

from playwright.sync_api import expect

def test_manual_mode_transition(page):
    """
    Test 4: Verify clicking PERFORMANCE button boosts chip clock speeds.
    """
    dashboard = SnapdragonDashboard(page)
    dashboard.navigate()

    # 1. Verify we start in a 'Balanced' state
    initial_speed = dashboard.get_prime_core_speed()
    print(f"\n[TRANSITION] Starting Speed: {initial_speed} GHz")
    dashboard.click_reset_soc()
    assert initial_speed < 4.0, "Setup Error: Chip did not start in Balanced mode."

    # 2. Action: Click the Performance button
    print("[TRANSITION] Clicking PERFORMANCE button...")
    dashboard.click_performance()

    # 3. Verify UI text update
    # expect() is smart: it waits for the text to appear automatically
    expect(page.locator("#mode-text")).to_have_text("Mode: High Performance")

    # 4. Verify Hardware Speed update
    # We wait 1.5s to ensure the JS 'update()' function has fetched the new data
    page.wait_for_timeout(1500)
    boosted_speed = dashboard.get_prime_core_speed()
    print(f"[TRANSITION] Boosted Speed: {boosted_speed} GHz")
    
    # 4.32 GHz is our target for Prime Cores in High Performance mode
    assert boosted_speed > 4.0, f"Physics Error: , got {boosted_speed}"

    print("[PASSED] Test 4: UI Button -> Hardware API -> Dashboard Sync verified.")    

def test_thermal_throttling_visuals(page):
    """
    Test 5: Verify that the UI displays a red alert during thermal overheating.
    """
    dashboard = SnapdragonDashboard(page)
    dashboard.navigate()

    # 1. Start the heat-up process
    print("\n[THERMAL] Switching to High Performance to generate heat...")
    dashboard.click_performance()

    # 2. Monitor until Throttling occurs
    # We use a loop to wait because the simulator takes time to heat up
    print("[THERMAL] Waiting for temperature to hit 85°C threshold...")
    
    # We'll give it a maximum of 30 seconds to overheat
    success = False
    for _ in range(30):
        current_status = dashboard.get_thermal_status()
        current_temp = page.locator("#global-temp").inner_text()
        
        print(f"[LIVE] Status: {current_status} | Temp: {current_temp}")
        
        if current_status == "THROTTLING":
            success = True
            break
        page.wait_for_timeout(1000) # Check every second

    # 3. Assertions
    assert success, "Safety Failure: Chip reached high temp but did not trigger Throttling UI!"
    
    # Verify the red blinking CSS class is active
    assert dashboard.is_throttling_style_active(), "Visual Failure: 'throttling' CSS class not found."
    
    print("[PASSED] Test 5: Thermal Throttling alert and visuals verified.")

def test_pmic_battery_auto_override(page):
    """
    Test 6: Verify PMIC forces 'Balance' mode when battery hits 20%.
    """
    dashboard = SnapdragonDashboard(page)
    dashboard.navigate()

    # 1. Set to Performance Mode to accelerate battery drain
    print("\n[PMIC] Setting to High Performance...")
    dashboard.click_performance()
    
    # 2. Wait until battery drops to the critical threshold (20%)
    print("[PMIC] Monitoring battery drain (Waiting for 20%)...")
    
    overridden = False
    # We'll check for up to 60 seconds
    for _ in range(240):
        level = dashboard.get_battery_level()
        mode = dashboard.get_current_mode_text()
        
        print(f"[LIVE] Battery: {level}% | {mode}")
        
        # The logic: If battery <= 20, mode should NOT be High Performance
        if level <= 20:
            if "Saver" in mode:
                overridden = True
                break
        
        page.wait_for_timeout(1000)

    # 3. Assertions
    assert overridden, "Safety Failure: PMIC did not force Balance mode at 20% battery!"
    
    # 4. Final Verification: Speed should be back to Balanced (~3.53 GHz)
    current_speed = dashboard.get_prime_core_speed()
    print(f"[PMIC] Current Prime Core Speed: {current_speed} GHz")
    assert current_speed < 4.0, f"Hardware Failure: Speed still boosted at {current_speed} GHz"

    print("[PASSED] Test 6: PMIC Battery Safety Override verified.")

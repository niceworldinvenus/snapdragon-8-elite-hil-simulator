import pytest
import httpx

# The address of our "Hardware" simulator
SIMULATOR_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="function")
async def power_cycle():
    """
    This is a FIXTURE. 
    It runs BEFORE the test to ensure the chip is fresh.
    """
    async with httpx.AsyncClient() as client:
        # --- SETUP: Reboot the chip ---
        print("\n[HIL] Initiating Power Cycle... Rebooting Snapdragon SoC.")
        await client.post(f"{SIMULATOR_URL}/reboot")
        
        # This 'yield' is where the actual test happens
        yield 
        
        # --- TEARDOWN: Clean up after the test ---
        print("[HIL] Test finished. Chip state logged.")
from playwright.sync_api import Page

class SnapdragonDashboard:
    def __init__(self, page: Page):
        self.page = page
        self.url = "http://127.0.0.1:8000/"
        
        # This locator finds all 8 core cards
        self.core_cards = page.locator(".core-card")
        
        # This locator finds the Prime cores specifically by their CSS class
        self.prime_cores = page.locator(".core-card.prime")

    def navigate(self):
        # No 'await' here
        self.page.goto(self.url)  

    def get_core_vertical_position(self, index: int) -> float:
  
        box = self.core_cards.nth(index).bounding_box()
        return box['y'] if box else -1   
    
    def get_global_temp(self) -> float:
   
    # Locates the temperature div, gets the text, and removes the '°C'
        temp_text = self.page.locator("#global-temp").inner_text()
        # "45.2°C" -> "45.2" -> 45.2
        return float(temp_text.replace("°C", "")) 

    # framework/pages/dashboard_page.py

    def click_reset_soc(self):
        self.page.get_by_role("button", name="RESET SoC").click()

    def click_performance(self):
        """Clicks the Performance button to boost speeds."""
        self.page.locator(".btn-perf").click()

    def click_balanced(self):
        """Clicks the Balanced button to normalize speeds."""
        self.page.locator(".btn-bal").click()

    def get_prime_core_speed(self) -> float:
        """Reads the current speed of the first Prime core (Core 0)."""
        # Locates the speed value inside the first core card
        speed_text = self.core_cards.nth(0).locator(".stat").inner_text()
        # "3.53 GHz" -> 3.53
        return float(speed_text.split(" ")[0]) 
    

    def get_thermal_status(self) -> str:
        """Reads the text from the status indicator (e.g., OPTIMAL or THROTTLING)."""
        return self.page.locator("#status-text").inner_text()

    def is_throttling_style_active(self) -> bool:
        """Checks if the 'throttling' CSS class is applied to the status text."""
        # This checks for the red blinking animation class
        classes = self.page.locator("#status-text").get_attribute("class")
        return "throttling" in (classes or "")
    

    def get_battery_level(self) -> int:
        """Reads the current battery percentage from the dashboard."""
        # Locates the span with id 'bat-val'
        bat_text = self.page.locator("#bat-val").inner_text()
        return float(bat_text)

    def get_current_mode_text(self) -> str:
        """Reads the current power mode text (e.g., 'Mode: Balance')."""
        return self.page.locator("#mode-text").inner_text()
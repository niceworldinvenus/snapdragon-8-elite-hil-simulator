Snapdragon 8 Elite HIL Simulator & Validation Suite
📱 Project Overview
This project is a Hardware-in-the-Loop (HIL) Simulator for the Snapdragon 8 Elite (Gen 5) System-on-a-Chip (SoC). It simulates real-time hardware telemetry, including 8-core cluster dynamics, thermal throttling behaviors, and Power Management IC (PMIC) safety protocols.

The system is designed with a Dual-Layer Validation Architecture, ensuring that both the hardware logic (Backend API) and the monitoring interface (Frontend UI) operate within safety parameters.

🛠 Tech Stack
Backend/Simulator: FastAPI (Python) - Handles physics-based telemetry and state machine logic.

Frontend Dashboard: HTML5, CSS3 (Tailwind-inspired), JavaScript (ES6) - Real-time data visualization.

Automated Testing: * Pytest: API logic and hardware state validation.

Playwright: E2E UI testing and responsive layout verification.

🚀 Key Engineering Features
8-Core Cluster Modeling: Simulates 2x Prime Cores (Oryon) up to 4.32 GHz and 6x Performance Cores.

Thermal Throttling (Safety Governor): Logic-driven clock speed capping when the SoC exceeds 85°C, featuring recovery hysteresis.

PMIC Battery Override: Automatic transition to "Battery Saver" and "Ultra Saver" modes based on critical battery thresholds (20% and 5%).

Real-time Telemetry: 1Hz heartbeat sync between the hardware state machine and the dashboard.

🧪 Automated Testing Suite (Regression Rig)
The project includes a robust regression suite to ensure system stability during software updates.

1. Backend Logic Tests (Pytest)
Located in tests/test_backend.py. Validates:

Telemetry Integrity: Ensures correct JSON structure and core counts.

Physics Accuracy: Verifies clock speed boosts in High-Performance mode.

Safety Rejection: Confirms the API rejects unsafe power requests when battery is low.

2. UI/UX Automation (Playwright)
Located in tests/test_ui.py. Validates:

Responsive Layout: Grid alignment on Mobile, Tablet, and Desktop.

Visual Alerts: Verification of red "Throttling" alerts and CSS animations.

E2E Safety Flow: Automated verification of the PMIC auto-override in the browser.

🚦 Getting Started
Prerequisites
Python 3.9+

Node.js (for Playwright browsers)

Installation
Clone the repo:

Bash

git clone the repository
cd snapdragon-8-elite-hil-simulator
Install dependencies:

Bash

pip install -r requirements.txt
playwright install chromium
Running the Simulator
Bash

uvicorn main:app --reload
Navigate to http://127.0.0.1:8000 to view the dashboard.

Running the Test Rig
Bash

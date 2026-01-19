from fastapi import FastAPI, HTTPException, Request, Response, Cookie
from fastapi.responses import HTMLResponse
from typing import Optional
import random
import uuid

app = FastAPI(title="Snapdragon 8 Elite (Gen 5) HIL Simulator")

# --- Multi-Tenant Store ---
# This dictionary maps session_id -> SnapdragonSimulator instance
# This ensures every browser gets its own private "hardware" object
user_sessions = {}

class SnapdragonSimulator:
    def __init__(self, session_id: str):
        self.session_id = session_id
        # Every chip starts at a fresh factory state
        self.state = {
            "battery_level": 100.0,
            "global_temp": 40.0,
            "power_mode": "Balance",
            "is_throttling": False,
            "cores": [
                {"id": i, "type": "Prime", "speed": 3.53, "temp": 40.0} if i < 2 
                else {"id": i, "type": "Performance", "speed": 2.80, "temp": 40.0} 
                for i in range(8)
            ]
        }

    def update_physics(self):
        s = self.state
        
        # 1. Logic for Power Modes
        if s["battery_level"] <= 5: s["power_mode"] = "Ultra Saver"
        elif s["battery_level"] <= 20: s["power_mode"] = "Battery Saver"

        if s["power_mode"] == "High Performance":
            prime_t, perf_t, drain, heat = 4.32, 3.53, 0.45, 2.2
        elif s["power_mode"] == "Balance":
            prime_t, perf_t, drain, heat = 3.53, 2.80, 0.15, 0.4
        else: # Power Savers
            prime_t, perf_t, drain, heat = 1.20, 0.80, 0.05, -1.5

        # 2. Thermal Throttling Governor
        if s["global_temp"] > 85: s["is_throttling"] = True
        elif s["global_temp"] < 65: s["is_throttling"] = False

        if s["is_throttling"]:
            prime_t, perf_t, heat = 1.80, 1.40, -3.5

        # 3. Apply changes with Silicon Jitter (Randomness)
        s["battery_level"] = max(0, round(s["battery_level"] - drain, 2))
        s["global_temp"] = max(35, round(s["global_temp"] + heat + random.uniform(-0.5, 0.5), 1))

        for core in s["cores"]:
            target = prime_t if core["type"] == "Prime" else perf_t
            core["speed"] = round(target + random.uniform(-0.03, 0.03), 2)
            core["temp"] = round(s["global_temp"] + random.uniform(-1.0, 1.0), 1)
        
        return s

@app.get("/telemetry")
async def get_telemetry(response: Response, chip_session: Optional[str] = Cookie(None)):
    # 1. IDENTIFY: If no cookie is present, this is a new browser/visit
    if not chip_session:
        chip_session = str(uuid.uuid4())
        # Set the cookie so the browser identifies itself in the next request
        response.set_cookie(key="chip_session", value=chip_session)
    
    # 2. ASSIGN: Create or get the specific simulator for this cookie
    if chip_session not in user_sessions:
        user_sessions[chip_session] = SnapdragonSimulator(chip_session)
    
    sim = user_sessions[chip_session]
    state = sim.update_physics()
    
    return {
        "device_id": chip_session,
        "chipset": "Snapdragon 8 Elite (Gen 5)",
        "battery": state["battery_level"],
        "power_mode": state["power_mode"],
        "thermal_status": "THROTTLING" if state["is_throttling"] else "OPTIMAL",
        "global_temp": state["global_temp"],
        "cores": state["cores"]
    }

@app.post("/set_mode")
async def set_mode(mode: str, chip_session: Optional[str] = Cookie(None)):
    if not chip_session or chip_session not in user_sessions:
        raise HTTPException(status_code=400, detail="No active session found")
        
    sim = user_sessions[chip_session]
    if mode not in ["High Performance", "Balance"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    if sim.state["battery_level"] <= 20:
        raise HTTPException(status_code=400, detail="Battery too low for performance modes")
    
    sim.state["power_mode"] = mode
    return {"status": f"Successfully switched to {mode}"}

@app.post("/reboot")
async def reboot(chip_session: Optional[str] = Cookie(None)):
    if chip_session in user_sessions:
        # Reset the simulator object for this specific user
        user_sessions[chip_session] = SnapdragonSimulator(chip_session)
    return {"status": "SoC Rebooted"}

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Responsive Visual Interface for the Snapdragon 8 Elite Monitor"""
    return """
    <html>
        <head>
            <title>Snapdragon 8 Elite Monitor</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                :root {
                    --bg: #0a0a0a;
                    --card: #1a1a1a;
                    --prime: #f1c40f;
                    --perf: #3498db;
                    --danger: #e74c3c;
                }

                body { font-family: 'Inter', sans-serif; background: var(--bg); color: white; padding: 15px; margin: 0; }
                
                /* Responsive Header */
                .header { 
                    display: flex; 
                    flex-direction: column; 
                    gap: 10px; 
                    border-bottom: 1px solid #333; 
                    padding-bottom: 15px; 
                }
                
                /* Desktop Header: Above 1024px */
                @media (min-width: 1024px) {
                    .header { flex-direction: row; justify-content: space-between; align-items: center; }
                    body { padding: 40px; }
                }

                /* Responsive Grid System */
                .grid { 
                    display: grid; 
                    grid-template-columns: 1fr; /* Mobile: 1 Column */
                    gap: 15px; 
                    margin-top: 20px; 
                }

                /* Tablet: Between 600px and 1023px */
                @media (min-width: 600px) {
                    .grid { grid-template-columns: repeat(2, 1fr); }
                }

                /* Desktop: Above 1024px */
                @media (min-width: 1024px) {
                    .grid { grid-template-columns: repeat(4, 1fr); }
                }

                .core-card { 
                    background: var(--card); 
                    padding: 20px; 
                    border-radius: 12px; 
                    border-left: 5px solid var(--perf); 
                    transition: transform 0.2s ease;
                   
                }
                .core-card:hover { transform: translateY(-5px); }
                .prime { border-left-color: var(--prime); }

                /* Responsive Controls */
                .controls { 
                    background: var(--card); 
                    padding: 20px; 
                    border-radius: 12px; 
                    margin-top: 25px; 
                    display: flex; 
                    flex-direction: column; 
                    gap: 12px; 
                }

                @media (min-width: 768px) {
                    .controls { flex-direction: row; align-items: center; }
                }

                .btn { 
                    padding: 12px 20px; 
                    border: none; 
                    border-radius: 6px; 
                    cursor: pointer; 
                    font-weight: bold; 
                    font-size: 0.9em;
                    transition: 0.3s;
                    width: 100%; /* Full width on mobile */
                }

                @media (min-width: 768px) {
                    .btn { width: auto; }
                    .btn-reboot { margin-left: auto; }
                }

                .btn-perf { background: var(--danger); color: white; }
                .btn-bal { background: var(--perf); color: white; }
                .btn-reboot { background: #444; color: white; }
                .btn:active { transform: scale(0.98); }

                .stat { font-size: 1.3em; font-weight: bold; }
                .throttling { color: var(--danger); animation: blink 1s infinite; }
                @keyframes blink { 50% { opacity: 0.3; } }

                .battery-bar { width: 100%; background: #333; height: 12px; border-radius: 6px; margin: 15px 0; }
                #bat-fill { height: 100%; width: 100%; background: #2ecc71; border-radius: 6px; transition: 0.5s; }
                
                small { color: #888; text-transform: uppercase; letter-spacing: 1px; }
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <h1 style="margin:0;">Snapdragon 8 Elite</h1>
                    <p id="mode-text" style="color:#aaa; margin-top:5px;">Mode: Balance</p>
                </div>
                <div style="text-align: right">
                    <div class="stat" id="global-temp">--°C</div>
                    <div id="status-text" style="font-weight:bold; letter-spacing:1px; font-size:0.8em;">OPTIMAL</div>
                </div>
            </div>
            
            <div class="battery-bar"><div id="bat-fill"></div></div>
            <p style="margin-top:0;">Battery: <span id="bat-val" style="font-weight:bold;">100</span>%</p>

            <div class="controls">
                <span style="font-weight: bold; font-size:0.8em;">HARDWARE OVERRIDE:</span>
                <button class="btn btn-perf" onclick="setMode('High Performance')">PERFORMANCE</button>
                <button class="btn btn-bal" onclick="setMode('Balance')">BALANCED</button>
                <button class="btn btn-reboot" onclick="rebootChip()">RESET SoC</button>
            </div>

            <div class="grid" id="core-grid"></div>

            <script>
                async function setMode(mode) {
                    try {
                        const res = await fetch(`/set_mode?mode=${encodeURIComponent(mode)}`, { method: 'POST' });
                        if (!res.ok) {
                            const error = await res.json();
                            alert("PMIC Warning: " + error.detail);
                        }
                    } catch (e) { console.error(e); }
                }

                async function rebootChip() {
                    await fetch('/reboot', { method: 'POST' });
                }

                async function update() {
                    try {
                        const res = await fetch('/telemetry');
                        const data = await res.json();
                        
                        document.getElementById('mode-text').innerText = "Mode: " + data.power_mode;
                        document.getElementById('global-temp').innerText = data.global_temp + "°C";
                        document.getElementById('bat-val').innerText = data.battery;
                        document.getElementById('bat-fill').style.width = data.battery + "%";
                        
                        const status = document.getElementById('status-text');
                        status.innerText = data.thermal_status;
                        status.className = data.thermal_status === 'THROTTLING' ? 'throttling' : '';

                        const fill = document.getElementById('bat-fill');
                        if (data.battery <= 5) fill.style.backgroundColor = '#e74c3c';
                        else if (data.battery <= 20) fill.style.backgroundColor = '#f1c40f';
                        else fill.style.backgroundColor = '#2ecc71';

                        const grid = document.getElementById('core-grid');
                        grid.innerHTML = data.cores.map(c => `
                            <div class="core-card ${c.type === 'Prime' ? 'prime' : ''}">
                                <small>${c.type} Core ${c.id}</small>
                                <div class="stat">${c.speed} GHz</div>
                                <small style="color:#666">${c.temp}°C</small>
                            </div>
                        `).join('');
                    } catch (e) { console.error("Update Sync Error", e); }
                }
                setInterval(update, 1000);
                update(); 
            </script>
        </body>
    </html>
    """



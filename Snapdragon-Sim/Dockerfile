FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Environment setup for stability
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# 1. Upgrade pip first
RUN python -m pip install --upgrade pip

# 2. Install Core Web Frameworks
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# 3. Install Testing Engines
RUN pip install --no-cache-dir pytest pytest-asyncio httpx

# 4. Install Automation Tools
RUN pip install --no-cache-dir playwright pytest-playwright

# 5. Install Playwright Browsers (Chromium)
RUN playwright install chromium

# 6. Copy Project Files
COPY . .

EXPOSE 8000

# Path based on your simulator/chip_api.py structure
CMD ["uvicorn", "simulator.chip_api:app", "--host", "0.0.0.0", "--port", "8000"]
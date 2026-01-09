# 1. Use the official Playwright-Python image (includes Chromium)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 2. Set the working directory
WORKDIR /app

# 3. Copy everything into the container
COPY . /app

# 4. Install your Python dependencies
# We use -r requirements.txt to be professional and consistent
RUN pip install --no-cache-dir -r requirements.txt

# 5. Link Playwright to the browsers already in the image
RUN playwright install chromium

# 6. Expose the port FastAPI runs on
EXPOSE 8000

# 7. Start the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]


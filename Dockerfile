FROM python:3.9-slim

# Set a working directory
WORKDIR /app

# Install dependencies for Chrome + Selenium
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libdrm-dev \
    libxkbcommon0 \
    libgtk-3-0 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (hardcoded version)
RUN wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_116.0.5845.96-1_amd64.deb && \
    apt-get update && apt-get install -y /tmp/google-chrome.deb && \
    rm -rf /tmp/google-chrome.deb /var/lib/apt/lists/*

# Install ChromeDriver (matching Chrome version)
RUN wget -q -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make app discoverable to Python
ENV PYTHONPATH=/app

# Default entrypoint
ENTRYPOINT ["python"]
CMD ["/app/scrapers/football-data.py"]

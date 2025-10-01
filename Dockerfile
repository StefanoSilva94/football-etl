FROM python:3.9-slim

# Set a working directory
WORKDIR /app

# Install required packages: tools (wget, unzip, gnupg) + Chrome runtime dependencies
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

# Add Google’s signing key + repository for Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver matching the installed Chrome version
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    CHROME_MAJOR_VERSION=${CHROME_VERSION%%.*} && \
    wget -q -O /tmp/chromedriver.zip \
      "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_MAJOR_VERSION}.0.0.0/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make app discoverable to Python
ENV PYTHONPATH=/app

# Default entrypoint
ENTRYPOINT ["python"]
CMD ["/app/scrapers/football-data.py"]

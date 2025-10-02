FROM python:3.9-slim

# Set a working directory
WORKDIR /app

# Install dependencies for Chrome + Selenium
RUN apt-get update && apt-get install -y \
    wget \
    curl\
    unzip \
    gnupg \
    ca-certificates \
    xvfb \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libatk1.0-0 \
    libdrm-dev \
    libxkbcommon0 \
    libgtk-3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends

# Copy project files
COPY . /app/

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg &&\
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] https://dl.google.com/linux/chrome/deb stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Print Chrome version to verify
RUN google-chrome --version

# Install ChromeDriver (matching Chrome version)
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/134.0.6998.165/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64


#RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
#    CHROME_MAJOR=${CHROME_VERSION%%.*} && \
#    echo "Installed Chrome version: $CHROME_VERSION, major: $CHROME_MAJOR" && \
#    wget -q -O /tmp/chromedriver.zip \
#      "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR}/chromedriver_linux64.zip" && \
#    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
#    chmod +x /usr/local/bin/chromedriver && \
#    rm /tmp/chromedriver.zip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make app discoverable to Python
ENV PYTHONPATH=/app

# Default entrypoint
ENTRYPOINT ["python"]
CMD ["/app/scrapers/football-data.py"]

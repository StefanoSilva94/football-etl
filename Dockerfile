# Use a Python base image
FROM python:3.9-slim

# Set a working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app/

# Install any dependencies if needed
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["/app/scrapers/football-data.py"]

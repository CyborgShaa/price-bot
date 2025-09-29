# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python script into the container
COPY price_bot.py .

# This command keeps the container running forever.
CMD ["sleep", "infinity"]

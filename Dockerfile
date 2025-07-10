# Use a standard, slim Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Update the package manager and install ffmpeg (essential for the bot)
# --no-install-recommends saves space
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy ONLY the requirements file into the container
# This is a Docker best practice to use the build cache effectively
COPY requirements.txt .

# Install the Python packages from your clean requirements.txt file
# This command ONLY reads requirements.txt and nothing else
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your application's source code
COPY . .

# Set the command to run when the container starts
CMD ["python", "src/main.py"]

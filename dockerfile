# Use an official Python runtime as the base image
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy the script and dependencies to the container
COPY pod-monitor.py requirements.txt ./

# Install the necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable
ENV WEBHOOK_URL 'https://outlook.office.com/webhook/{webhook_id}/{webhook_secret}/{channel_id}'

# Run the script
CMD ["python", "pod-monitor.py"]

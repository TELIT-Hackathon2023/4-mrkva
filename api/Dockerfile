# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file into the Docker image
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libpq-dev gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the command to start uWSGI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
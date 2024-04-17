# Use an official Python runtime as a parent image
FROM python:3.11.4

# Set the PIP_ROOT_USER_ACTION environment variable
ENV PIP_ROOT_USER_ACTION=ignore

# Set the working directory in the container
WORKDIR /app

# Create a virtual environment
RUN python -m venv /app/venv

# Install system dependencies (example for PostgreSQL)
RUN apt-get update && apt-get install -y libpq-dev

# Update setuptools and pip
RUN /app/venv/bin/python -m pip install --upgrade pip setuptools

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run server.py when the container launches
CMD ["/app/venv/bin/python", "server.py"]


# # Use an official Python runtime as a parent image
# FROM python:3.11.4

# # Set the working directory in the container
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Install any needed dependencies specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Make port 5000 available to the world outside this container
# EXPOSE 5000

# # Run server.py when the container launches
# CMD ["python", "server.py"]

# Use an official Python runtime as a parent image
FROM python:3.11.4

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install virtualenv
RUN pip install --no-cache-dir virtualenv

# Create a virtual environment
RUN virtualenv venv

# Activate the virtual environment
SHELL ["venv/bin/activate"]

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run server.py when the container launches
CMD ["python", "server.py"]

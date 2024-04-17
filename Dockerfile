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

# Create a virtual environment
RUN python -m venv /app/venv

# Make sure pip uses the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run server.py when the container launches
CMD ["/app/venv/bin/python", "server.py"]


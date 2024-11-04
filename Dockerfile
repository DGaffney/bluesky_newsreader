# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y nano tmux rsync cron make

# Set a working directory inside the container
WORKDIR /usr/src/app

# Install the Python dependencies
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy and set permissions for the startup scripts
COPY app/start.sh /usr/src/app/start.sh
RUN chmod 700 /usr/src/app/start.sh
COPY app/entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod 700 /usr/src/app/entrypoint.sh

# Expose the FastAPI port
EXPOSE 8000

# Set the entrypoint script
ENTRYPOINT ["/usr/src/app/start.sh"]

# Set the default command
CMD ["/usr/src/app/start.sh"]

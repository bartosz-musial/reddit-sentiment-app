# Use a lightweight Python image
FROM python:3.11-slim

# Set the timezone to Europe/Warsaw
ENV TZ=Europe/Warsaw

# Set working directory inside the container
WORKDIR /app

# Copy dependencies file to the container
COPY requirements.txt .

# Install dependencies (including psycopg2-binary if listed)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Set the default command to run the application
CMD ["python", "-m", "backend.main"]
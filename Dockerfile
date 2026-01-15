# stage I : Build Stage

FROM python:3.11.4-slim AS builder

# Set environment variables to prevent Python from writing .pyc files & Ensure Python output is not buffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required by TensorFlow
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    libhdf5-dev \
    libprotobuf-dev \
    protobuf-compiler \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /build

COPY requirements.txt .

# Install dependencies from requirements.txt first
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Copy the application code
COPY . .


# Install the package in editable mode (without utils dependency)
RUN pip install --no-cache-dir --prefix=/install -e . --no-deps


# stage II : Runtime

FROM python:3.11.4-slim 

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# copy only installed Python packages
COPY --from=builder /install /usr/local

COPY . .

# Expose the port that Flask will run on
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]
# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Create a non-root user for Hugging Face security compliance
# Hugging Face Spaces run as user 1000 by default
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Copy the rest of the application code
COPY --chown=user . /code

EXPOSE 7860

#
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app.main:app"]

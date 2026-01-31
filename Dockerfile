FROM python:3.11-slim

WORKDIR /app

# Create instance directory for SQLite database
RUN mkdir -p /app/instance

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for production
ENV FLASK_DEBUG=False
ENV HOST=0.0.0.0
ENV PORT=5000

# Expose port
EXPOSE 5000

# Use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "main:app"]
FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Make start script executable
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"] 
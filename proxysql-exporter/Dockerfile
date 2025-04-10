# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Copy your application code
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 9104

# Run the app
CMD ["python", "app.py"]

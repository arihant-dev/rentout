FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1 
# Cloud Run supplies the PORT env var (default 8080). Use it when starting the server.
# Use a start script to print environment and run the server (helps debugging startup errors).
EXPOSE 8080
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
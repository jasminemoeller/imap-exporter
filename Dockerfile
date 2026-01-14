FROM python:3-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir prometheus-client pyyaml

# Copy the exporter script
COPY imap-exporter.py /app/imap-exporter.py

# Make it executable
RUN chmod +x /app/imap-exporter.py

# Expose metrics port
EXPOSE 9226

# Default command
ENTRYPOINT ["python3", "/app/imap-exporter.py"]
CMD ["--config", "/app/config.yml"]
# IMAP Quota Exporter

A Prometheus exporter for monitoring IMAP mailbox quota usage across multiple accounts.

## Features

- 📊 Monitor multiple IMAP accounts from a single exporter
- 📈 Export quota usage, limits, and connection status as Prometheus metrics
- ⚙️ Configurable check intervals
- 🔒 Support for SSL/TLS IMAP connections
- 🐳 Lightweight Docker container
- 📝 Simple YAML configuration

## Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `imap_quota_used_kb` | Gauge | IMAP quota used in kilobytes | `account` |
| `imap_quota_limit_kb` | Gauge | IMAP quota limit in kilobytes | `account` |
| `imap_up` | Gauge | IMAP connection status (1=up, 0=down) | `account` |

## Quick Start

### Using Docker
```bash
# Pull the image
docker pull ghcr.io/yourusername/imap-exporter:latest

# Create a config file
cat > config.yml << EOF
check_interval: 900  # Check every 15 minutes

accounts:
  - name: personal
    server: imap.example.com
    port: 993
    username: user@example.com
    password: your-password
EOF

# Run the exporter
docker run -d \
  --name imap-exporter \
  -p 9226:9226 \
  -v $(pwd)/config.yml:/app/config.yml:ro \
  ghcr.io/yourusername/imap-exporter:latest
```

### Using Docker Compose
```yaml
services:
  imap_exporter:
    image: ghcr.io/yourusername/imap-exporter:latest
    restart: unless-stopped
    ports:
      - "9226:9226"
    volumes:
      - ./config.yml:/app/config.yml:ro
```

Then run:
```bash
docker-compose up -d
```

## Configuration

Create a `config.yml` file:
```yaml
# Check interval in seconds (default: 900 = 15 minutes)
check_interval: 900

accounts:
  # First account
  - name: personal
    server: imap.ionos.de
    port: 993
    username: personal@example.com
    password: your-password

  # Second account
  - name: work
    server: imap.gmail.com
    port: 993
    username: work@gmail.com
    password: app-specific-password

  # Add as many accounts as needed
  - name: another-account
    server: mail.example.com
    port: 993
    username: user@example.com
    password: password123
```

### Configuration Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `check_interval` | No | 900 | Interval between IMAP checks in seconds |
| `accounts[].name` | Yes | - | Unique identifier for the account (used as Prometheus label) |
| `accounts[].server` | Yes | - | IMAP server hostname |
| `accounts[].port` | No | 993 | IMAP port (typically 993 for SSL/TLS) |
| `accounts[].username` | Yes | - | IMAP username/email |
| `accounts[].password` | Yes | - | IMAP password |

### Custom Config Path

You can specify a custom config file location:
```bash
docker run -d \
  -v /path/to/my-config.yml:/etc/imap/config.yml:ro \
  -p 9226:9226 \
  ghcr.io/yourusername/imap-exporter:latest \
  --config /etc/imap/config.yml
```

## Prometheus Configuration

Add this to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'imap-exporter'
    scrape_interval: 5m
    static_configs:
      - targets: ['localhost:9226']
```

## Example Queries

### Quota usage percentage
```promql
(imap_quota_used_kb / imap_quota_limit_kb) * 100
```

### Quota used in GB
```promql
imap_quota_used_kb / 1024 / 1024
```

### Quota remaining in GB
```promql
(imap_quota_limit_kb - imap_quota_used_kb) / 1024 / 1024
```

### Accounts over 80% quota
```promql
(imap_quota_used_kb / imap_quota_limit_kb) > 0.8
```

### Account connection status
```promql
imap_up
```

## Grafana Dashboard

Example Grafana panel configurations:

### Quota Usage Gauge
- **Query:** `(imap_quota_used_kb{account="personal"} / imap_quota_limit_kb{account="personal"}) * 100`
- **Visualization:** Gauge
- **Unit:** Percent (0-100)
- **Thresholds:** 
  - Green: 0-70
  - Yellow: 70-85
  - Red: 85-100

### Quota Over Time
- **Query:** `imap_quota_used_kb / 1024 / 1024`
- **Visualization:** Time series
- **Unit:** GB
- **Legend:** `{{account}}`

## Security Considerations

⚠️ **Important:** The config file contains passwords in plain text!

- Set proper file permissions: `chmod 600 config.yml`
- Add `config.yml` to `.gitignore`
- Consider using Docker secrets for production:
```yaml
services:
  imap_exporter:
    image: ghcr.io/yourusername/imap-exporter:latest
    secrets:
      - imap_config
    command: ["--config", "/run/secrets/imap_config"]

secrets:
  imap_config:
    file: ./config.yml
```

## Tested Mail Providers

- ✅ IONOS
- ✅ Gmail (requires app-specific password)
- ✅ Generic IMAP servers

*Feel free to report compatibility with other providers!*

## Building from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/imap-exporter.git
cd imap-exporter

# Build the Docker image
docker build -t imap-exporter:latest .

# Run it
docker run -d \
  -v $(pwd)/config.yml:/app/config.yml:ro \
  -p 9226:9226 \
  imap-exporter:latest
```

## Development

### Running locally (without Docker)
```bash
# Install dependencies
pip install prometheus-client pyyaml

# Run the exporter
python3 imap-exporter.py --config config.yml
```

### Testing
```bash
# Check metrics endpoint
curl http://localhost:9226/metrics

# Expected output:
# imap_quota_used_kb{account="personal"} 6470764.0
# imap_quota_limit_kb{account="personal"} 12582912.0
# imap_up{account="personal"} 1.0
```

## Troubleshooting

### Connection refused
- Check IMAP server and port
- Verify firewall rules
- Ensure SSL/TLS is supported on the specified port

### Authentication failed
- Verify username and password
- For Gmail: use an app-specific password, not your regular password
- Check if 2FA requires special authentication

### No quota data
- Some IMAP servers don't support GETQUOTAROOT
- Check exporter logs for error messages

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Support

If you encounter issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions

## Changelog

See [Releases](https://github.com/yourusername/imap-exporter/releases) for version history and changes.
# ProxySQL Monitoring Stack

This repository contains a lightweight, containerized setup to monitor [ProxySQL](https://proxysql.com/) using:

- **FastAPI** — a custom exporter for ProxySQL internal metrics  
- **Prometheus** — to scrape and store time-series data  
- **Grafana** — for real-time visualization  
- **Docker Compose** — to spin everything up easily


---


## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/KanavRajFarishta/proxySQL-monitoring.git
cd proxySQL-monitoring
```

2. **Build and start the stack**

```bash
docker-compose up --build
```

3. **Access the services**

| Service     | URL                          |
|-------------|------------------------------|
| FastAPI     | http://localhost:8000/metrics |
| Prometheus  | http://localhost:9090         |
| Grafana     | http://localhost:3000         |

---

## Grafana Dashboard

To use the included dashboard:

1. Open [http://localhost:3000](http://localhost:3000)  
2. Login with:
   - Username: `admin`
   - Password: `admin`
3. Go to "Import" → Upload `resources/dashboard.json`

---

## Metrics Exported

The FastAPI-based exporter connects to ProxySQL’s admin interface and exposes:

- Query digest statistics
- Backend server status
- Connection pool usage
- Query counts and errors

All available at:
```
http://localhost:8000/metrics
```

---

## Prometheus Configuration

Prometheus scrapes metrics from the exporter every 5 seconds:

```yaml
scrape_configs:
  - job_name: 'proxysql_exporter'
    static_configs:
      - targets: ['fastapi:8000']
```

You can modify `prometheus.yml` to tune scrape intervals or add alerting rules.

---

## Deployment Details

- **FastAPI** runs as a Docker container with dependencies defined in `requirements.txt`
- **Prometheus** reads from `prometheus.yml`
- **Grafana** auto-loads dashboards and data sources from the `grafana/provisioning/` directory
- **Docker Compose** manages all services and their networking

---

## Related Blog

For a detailed explanation of architecture, reasoning, and setup:  
📖 [Read the blog post →](https://kanavrajfarishta.online/blog/posts/proxysql-monitoring/)

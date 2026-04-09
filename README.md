# Cloud Honeypot with Attack Dashboard

A simulated vulnerable web server that captures and logs real attack attempts. Built with Flask, MySQL, and Nginx — fully containerized with Docker.

## What It Does

- Exposes fake login and admin pages to attract attackers
- Logs every request: IP, country, credentials tried, user agent, path, attack type
- Detects brute force attempts and suspicious path probes automatically
- Enriches IPs with country data via MaxMind GeoLite2
- Displays everything in a live dashboard with Chart.js visualizations

## Stack

| Layer    | Technology         |
|----------|--------------------|
| Backend  | Python, Flask      |
| Database | MySQL 8            |
| Frontend | HTML, CSS, Chart.js|
| Proxy    | Nginx              |
| Infra    | Docker, docker-compose |

## Quick Start

**Prerequisites:** Docker and docker-compose installed.

```bash
git clone <your-repo-url>
cd cloud-honeypot
docker-compose up --build
```

Then open:
- `http://localhost/` — honeypot home page
- `http://localhost/login` — fake login page
- `http://localhost/admin` — fake admin panel
- `http://localhost/dashboard` — attack dashboard

## Project Structure

```
cloud-honeypot/
├── app.py                  # Flask routes
├── config.py               # DB config via environment variables
├── db.py                   # MySQL connection
├── geo_lookup.py           # IP → country via MaxMind
├── utils/
│   └── detector.py         # Attack classification logic
├── templates/
│   ├── dashboard.html      # Attack dashboard
│   ├── login.html          # Fake login page
│   ├── admin.html          # Fake admin panel
│   └── nginx/
│       └── default.conf    # Nginx reverse proxy config
├── static/
│   └── style.css
├── geoip/
│   └── GeoLite2-Country.mmdb
├── schema.sql              # Database schema
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Attack Detection

| Attack Type      | Trigger                                      |
|------------------|----------------------------------------------|
| `login_attempt`  | Any POST to /login                           |
| `brute_force`    | 5+ login attempts from same IP in 5 minutes  |
| `admin_probe`    | Any access to /admin                         |
| `suspicious_path`| Paths like `.env`, `wp-login.php`, `.git`    |
| `unknown_probe`  | Any other unrecognized path                  |

## Local Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # edit with your DB credentials
mysql -u root -p < schema.sql  # set up the database
python app.py
```

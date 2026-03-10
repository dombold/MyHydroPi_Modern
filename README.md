# HydroPi Modern

A self-hosted Raspberry Pi pool monitor with a web interface. HydroPi reads data from Atlas Scientific and DS18B20 sensors, controls power outlets via GPIO relays, and lets you monitor and manage everything from any browser on your local network.

---

## What It Does

| Feature | Description |
|---|---|
| **Dashboard** | Live sensor readings (pH, ORP, salinity, temperature) and relay/outlet states |
| **Timers** | Schedule on/off times for each power outlet |
| **Graphs** | Historical sensor data over 1 day to 1 year |
| **Dosage Calculator** | Enter your test strip readings and get exact chemical dosage amounts |
| **Settings** | Configure alert thresholds, sensor polling interval, email alerts, and system controls |

---

## Requirements

- Raspberry Pi (any model with GPIO — tested on Pi 3/4/5)
- Python 3.11+
- Node.js 18+ and npm (for building the frontend — build once, not needed at runtime)
- MariaDB / MySQL
- Atlas Scientific sensors (pH, ORP, EC, RTD) connected via I²C or UART
- DS18B20 temperature sensor connected via 1-Wire

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url> /home/pi/hydropi
cd /home/pi/hydropi
```

### 2. Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> If you are installing on a Raspberry Pi, uncomment the `RPi.GPIO` line in `requirements.txt` before running pip install.

### 3. Set up the database

Create a MariaDB database and user:

```sql
CREATE DATABASE hydropidb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hydropi_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON hydropidb.* TO 'hydropi_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Configure the environment

Copy the example and edit it:

```bash
cp .env.example .env
nano .env
```

| Variable | Description |
|---|---|
| `DB_HOST` | Database host (usually `localhost`) |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `DB_NAME` | Database name |
| `EMAIL_FROM` | Gmail address to send alerts from |
| `EMAIL_PASSWORD` | Gmail app password (not your login password) |
| `EMAIL_SERVER` | SMTP server (default: `smtp.gmail.com`) |
| `EMAIL_PORT` | SMTP port (default: `587`) |
| `USE_MOCK` | Set to `false` on real hardware, `true` for testing with dummy data |

### 5. Build the frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

The built files are placed in `backend/static/` and served automatically by the API server. You do not need Node.js running at runtime.

---

## Running

### Development (with hot-reload)

Start the API server:

```bash
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend dev server (optional — only needed if editing the UI):

```bash
cd frontend
npm run dev
```

Open `http://<pi-ip-address>:8000` in your browser.

### Production (as a system service)

Install the provided systemd services so HydroPi starts automatically on boot:

```bash
sudo cp systemd/hydropi-api.service /etc/systemd/system/
sudo cp systemd/hydropi-daemon.service /etc/systemd/system/
sudo cp systemd/hydropi-dns-update.service /etc/systemd/system/
sudo cp systemd/hydropi-dns-update.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable hydropi-api hydropi-daemon hydropi-dns-update.timer
sudo systemctl start hydropi-api hydropi-daemon
```

Check status:

```bash
sudo systemctl status hydropi-api
sudo journalctl -u hydropi-api -f
```

Open `http://<pi-ip-address>:8000` from any device on the same network.

---

## Using the Web Interface

### Dashboard

The dashboard is your main at-a-glance view. It refreshes automatically.

**Sensor Readings panel** shows the current value and 24-hour average for each sensor. If a reading falls outside the configured alert range the row is highlighted in red.

- **Pause** — temporarily stops sensor polling (useful while adding chemicals so you don't get false alerts).
- **Delete Old** — removes historical readings older than a chosen number of days to free up database space.

**Power Outlets panel** shows the live state (On/Off) and current mode of each relay-controlled outlet. Use the **On / Off / Auto** buttons to override a relay:

| Mode | Behaviour |
|---|---|
| **Auto** | Outlet is controlled by the timer schedule |
| **On** | Outlet is forced on regardless of schedule |
| **Off** | Outlet is forced off regardless of schedule |

---

### Timers

Each power outlet has its own timer card. Each card can hold multiple on/off time pairs. Set a start time and stop time, then click **Save**. The outlet will switch automatically when running in **Auto** mode.

Times use your browser's local time zone.

---

### Graphs

Select a sensor from the list and choose a time range (1D, 1W, 1M, 3M, 6M, 1Y) to view its historical readings. Hover over the chart to see individual values.

---

### Dosage Calculator

Enter the reading from your test kit or test strips for each chemical. Click **Check** (or press Enter) to get a dosage recommendation based on your pool size.

| Chemical | Target Range |
|---|---|
| Stabiliser (CYA) | 30–50 mg/L |
| Total Alkalinity | 80–150 mg/L |
| Total Chlorine | 3–5 mg/L |
| Calcium Hardness | 150–250 mg/L |

Pool size is set in **Settings → Pool Size (L)**.

---

### Settings

**Alert Thresholds** — set the safe high and low value for each sensor. If a live reading goes outside this range, the dashboard highlights it and an alert email is sent (if email is configured).

**System Settings** — configure timing and pool size:

| Setting | Description |
|---|---|
| Sensor Interval (s) | How often sensors are polled |
| Email Reset Delay (s) | Minimum time between repeat alert emails |
| Pause Duration (s) | How long the Pause button suppresses readings |
| Pool Size (L) | Used by the Dosage Calculator |
| Alert Email Address | The address that receives alert emails |

Click **Save Settings** to apply changes immediately without restarting.

**System Controls** — restart or shut down the Raspberry Pi from the browser. A confirmation dialog is shown before either action is taken. After a shutdown you will need physical access to power the Pi back on.

---

## Logs

Logs are written to `/var/log/hydropi/daemon.log` by default. Change the path with the `LOG_FILE` environment variable.

```bash
tail -f /var/log/hydropi/daemon.log
```

---

## Updating

```bash
cd /home/pi/hydropi
git pull

# Rebuild the frontend
cd frontend && npm install && npm run build && cd ..

# Restart the service
sudo systemctl restart hydropi-api
```

---

## Licence

Free to use and modify for personal use. See the original MyHydroPi project for background and context.

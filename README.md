# Integrated WAF Orchestrator

An experimental **Web Application Firewall (WAF) orchestration platform** with a built-in honeypot, analytics dashboard, and modular architecture.  
The project is designed for **research, monitoring, and demonstration** of web-application security concepts.


---

## Features
- **Integrated WAF Service** – Filters and logs malicious traffic.
- **Honeypot Logic** – Captures attacker behavior for analysis.
- **Streamlit Dashboard** – Live visualization of traffic and security metrics.
- **Modular Design** – Separate apps (`honey_app`, `real_app`) for testing.
- **SQLite Database** – Stores logs, comments, and captured data.

---

## Project Structure
```
Integrated_WAF_Orchestrator/
│
├─ app_runner.py           # Entry point to start services
├─ orchestrator.py         # Orchestration logic for WAF + honeypot
├─ proxy_service.py        # Reverse proxy & traffic routing
├─ waf_service.py          # Core WAF filtering rules
├─ streamlit_dashboard.py  # Security analytics UI
│
├─ honey_app/              # Honeypot web app (PHP)
│   ├─ index.php
│   ├─ config.php
│   └─ ...
│
├─ real_app/               # Simulated vulnerable web app (PHP)
│   ├─ index.php
│   ├─ config.php
│   └─ ...
│
├─ target_app_templates/   # Honeypot templates & helper scripts
├─ user_data/              # Data captured from attacks
├─ business/               # Business model/reference PDFs
└─ fine_tuned_model/       # Placeholder for ML models
```

---

## Installation & Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/Integrated_WAF_Orchestrator.git
   cd Integrated_WAF_Orchestrator
   ```

2. **Create a virtual environment & install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/Mac
   # or venv\Scripts\activate on Windows

   pip install -r requirements.txt
   ```

3. **Start the orchestrator**
   ```bash
   python app_runner.py
   ```
   This launches the WAF, honeypot, and proxy services.

4. **Run the dashboard (optional)**
   ```bash
   streamlit run streamlit_dashboard.py
   ```

---

## Usage
- Point your browser to the configured port (default: `http://localhost:8081` for apps).
- Access the dashboard at the Streamlit port (default: `http://localhost:8501`).

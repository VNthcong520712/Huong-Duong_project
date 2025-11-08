# Huong Duong Project

Short description
-----------------
This repository contains a small web project for the Huong Duong site. The project serves HTML pages (with CSS and JavaScript) and is backed by a local database. The server is implemented in Python. The live domain name for the project is: duanhuongduong.shop.

What this project includes
--------------------------
- A Python-based server (simple backend to serve pages / APIs).
- Front-end pages written in HTML, with CSS and JavaScript for styling and behavior.
- A local database for application data (default: SQLite or another local DB you choose).
- Configuration ready to point the domain duanhuongduong.shop to the server.

Quick start (developer)
-----------------------
1. Clone the repository
   git clone https://github.com/VNthcong520712/Huong-Duong_project.git
   cd Huong-Duong_project

2. Create and activate a Python virtual environment
   python3 -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate      # Windows (PowerShell/CMD)

3. Install dependencies (if a requirements file exists)
   pip install -r requirements.txt
   If there is no requirements.txt, install the packages your server uses (Flask, Django, etc.) as needed:
   pip install flask
   or
   pip install django

4. Configure the app (replace filenames / env vars below with actual ones)
   - If the project uses environment variables, set them:
     export APP_ENV=development
     export SECRET_KEY="your-secret-key"
   - If the project uses a specific server file, run that file. Common examples:
     python app.py
     python server.py
   - If using Flask (example):
     export FLASK_APP=app.py
     flask run --host=0.0.0.0 --port=8000
   - For a very simple static file server (if applicable):
     python -m http.server 8000

5. Database (local)
   - By default the project uses a local DB. If using SQLite, a file like `data/database.db` will be used/created.
   - If you have an initialization/migration script, run it:
     python scripts/init_db.py
     or
     python manage.py migrate   # for Django projects
   - If no DB init script exists, starting the server may auto-create the database file.

6. Accessing the site
   - Locally: http://localhost:8000 (replace port if different)
   - With a public server and DNS configured: https://duanhuongduong.shop (ensure DNS A/AAAA record points to your server IP and TLS is configured)

Domain & TLS
------------
- The project domain is: duanhuongduong.shop
- Point an A record from duanhuongduong.shop to your server's public IP address.
- Use a reverse proxy (Nginx) and a process manager (Gunicorn, systemd) for production.
- Obtain a TLS certificate from Let's Encrypt (certbot) and configure HTTPS for the domain.

Security & deployment notes
---------------------------
- Keep the SECRET_KEY and other secrets out of version control (use environment variables or a secrets store).
- Do not expose your local database file publicly — use proper file permissions and firewall rules.
- For production, use a WSGI server (Gunicorn/uWSGI) behind Nginx. Consider containerization (Docker) for easier deployment.
- Regularly back up the local database.

Project structure (example)
---------------------------
- /templates or /www  — HTML files (front-end)
- /static            — CSS and JavaScript files
- app.py / server.py — Python server entry point
- requirements.txt   — Python dependencies (optional)
- data/              — local database files (e.g. SQLite db)
- scripts/           — helper scripts (db init, migrations)

How you can help improve this README
------------------------------------
- Tell me the exact Python entrypoint filename (for example `app.py`, `server.py`, or Django `manage.py`) and I will update the “Quick start” commands to be exact.
- If you use a specific framework (Flask, Django, FastAPI, etc.), tell me and I'll add framework-specific setup and examples (migrations, run commands, typical environment variables).
- If you already have a requirements.txt, init scripts, or a preferred production setup (nginx+gunicorn, Dockerfile), share them and I will include customized instructions.

Contact
-------
Maintainer: VNthcong520712
Repository: https://github.com/VNthcong520712/Huong-Duong_project

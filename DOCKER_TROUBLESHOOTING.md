# 🐳 Docker Troubleshooting Guide

**INF2003 Group 11 — E-Commerce Clickstream & Transaction Analytics**

This guide covers common Docker issues your lecturer might encounter when setting up the project. Each problem has a diagnostic command and a fix.

---

## Quick Diagnostic Checklist

Run these commands to verify your Docker setup is healthy:

```bash
docker --version              # Should be 24.0+
docker compose version        # Should be v2.20+
docker ps                     # Should show no errors
docker info | grep -i "running"  # Should say "Server Version: ..."
```

If any of these fail or show errors, find the matching problem below.

---

## 🔴 Problem 1: "docker: command not found" / Docker not installed

**Symptoms:** Terminal says `docker: command not found` or `'docker' is not recognized`

**Diagnose:**
```bash
which docker        # Mac/Linux — should show a path
where docker        # Windows — should show a path
```

**Fix:**
1. Download Docker Desktop from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **Windows:** Install and restart your computer. Docker Desktop must be running (whale icon in system tray).
3. **Mac:** Install the `.dmg`, drag to Applications, open Docker Desktop once.
4. **Linux:** Follow [Docker's Linux install guide](https://docs.docker.com/engine/install/).

---

## 🔴 Problem 2: Docker Desktop is installed but not running

**Symptoms:** `docker ps` shows `error during connect: ... pipe ... The system cannot find the file specified`

**Diagnose:**
- **Windows:** Look for the whale icon 🐳 in the system tray (bottom-right corner). If it's not there, Docker Desktop isn't running.
- **Mac:** Check the menu bar for the Docker whale icon.

**Fix:**
1. Open Docker Desktop from your Start Menu / Applications folder.
2. Wait for the whale icon to stop animating and become steady.
3. Run `docker ps` again — it should show an empty table (no errors).

---

## 🔴 Problem 3: "port is already allocated" / port conflict

**Symptoms:**
```
Error response from daemon: Ports are not available:
port 5432 is already allocated
port 3000 is already allocated
```

**Diagnose — find what's using the port:**
```bash
# Windows (PowerShell)
netstat -ano | findstr ":5432"
netstat -ano | findstr ":3000"
netstat -ano | findstr ":8000"
netstat -ano | findstr ":27017"

# Mac/Linux
lsof -i :5432
lsof -i :3000
```

**Fix — Option 1: Stop the conflicting program**
The PID shown by the command above tells you which program is using the port. Common culprits:
- Port `5432`: Another PostgreSQL installation
- Port `3000`: Another React/Node dev server
- Port `8000`: Another Python app
- Port `27017`: Another MongoDB installation

Stop or quit that program, then run `docker-compose up` again.

**Fix — Option 2: Change the ports**
Edit `docker-compose.yml` and change the left-side port number (host port) to something free:
```yaml
ports:
  - "5433:5432"    # Changed from 5432 to 5433
```
Then update connection strings accordingly.

---

## 🔴 Problem 4: WSL2 not installed / not running (Windows only)

**Symptoms on Windows:**
```
Docker Desktop requires a newer WSL kernel version
```
or Docker Desktop starts but containers don't work.

**Diagnose:**
```powershell
wsl --status
wsl --list --verbose
```

**Fix:**
1. Open PowerShell as Administrator
2. Run: `wsl --install`
3. Restart your computer
4. Open Docker Desktop → Settings → Resources → WSL Integration → Enable

---

## 🔴 Problem 5: "Cannot connect to the Docker daemon" (Linux)

**Symptoms:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
Is the docker daemon running?
```

**Fix:**
```bash
# Start the Docker service
sudo systemctl start docker

# (Optional) Enable auto-start on boot
sudo systemctl enable docker

# (Optional) Add your user to the docker group to avoid sudo
sudo usermod -aG docker $USER
# Then log out and back in
```

---

## 🔴 Problem 6: "no configuration file provided" / docker-compose not found

**Symptoms:** `docker-compose: command not found`

**Diagnose:**
```bash
docker compose version    # Note: NO hyphen in "docker compose" (v2)
docker-compose --version  # Old v1 command (deprecated)
```

**Fix:**
Docker Compose v2 is bundled with Docker Desktop since 2022. Use `docker compose` (space, not hyphen):
```bash
docker compose up         # ✅ correct
docker-compose up         # ❌ old syntax, may not work
```

---

## 🔴 Problem 7: Containers exit immediately / keep restarting

**Symptoms:** `docker-compose up` starts containers but they crash with `exit code 1` or keep restarting.

**Diagnose:**
```bash
# See the logs for a specific container
docker logs ecommerce-backend
docker logs ecommerce-postgres
docker logs ecommerce-mongodb
```

**Common causes & fixes:**

| Log message | Cause | Fix |
|-------------|-------|-----|
| `FATAL: database "ecommerce_db" does not exist` | PostgreSQL didn't initialize properly | `docker-compose down -v` then `docker-compose up` |
| `ModuleNotFoundError: No module named 'fastapi'` | Backend image didn't build | `docker-compose build --no-cache backend` |
| `connection refused` | Database not ready when backend started | Normal — docker-compose retries. Wait 30 seconds. |
| `EACCES: permission denied` | Volume mount permission issue (Linux/Mac) | `sudo chown -R $USER:$USER ./data ./backend` |

---

## 🔴 Problem 8: "pull access denied" / Docker Hub rate limiting

**Symptoms:**
```
Error response from daemon: pull access denied for postgres
or
toomanyrequests: You have reached your pull rate limit
```

**Fix:**
Docker Hub limits anonymous pulls to 100 per 6 hours. If you hit the limit:
1. Create a free Docker Hub account at [hub.docker.com](https://hub.docker.com)
2. Log in from terminal: `docker login`
3. Try again: `docker-compose up`

Or wait — the limit resets every 6 hours.

---

## 🔴 Problem 9: Docker Desktop "out of memory" / containers slow

**Symptoms:** Containers start but are very slow, or Docker Desktop shows high memory usage.

**Diagnose:**
```bash
docker stats
```

**Fix:**
1. Open Docker Desktop → Settings (gear icon) → Resources
2. Increase memory limit:
   - **Recommended for this project:** at least **4 GB RAM**, **2 CPUs**
3. Apply & Restart Docker Desktop

---

## 🔴 Problem 10: Windows file sharing / volume mount issues

**Symptoms:** Changes to files on your host don't appear inside the container, or vice versa.

**Diagnose:**
```bash
docker exec ecommerce-backend ls /data    # Should show CSV files
docker exec ecommerce-backend ls /app     # Should show main.py, config.py, etc.
```

**Fix:**
1. Open Docker Desktop → Settings → Resources → File Sharing
2. Make sure your project folder (`C:\Users\...\INF2003-Grp11`) is listed
3. If using OneDrive (like `C:\Users\...\OneDrive\Desktop\...`), OneDrive may be locking files. Try moving the project outside OneDrive:
   ```
   C:\Projects\INF2003-Grp11
   ```

---

## 🔴 Problem 11: Docker build fails / "exec format error"

**Symptoms:**
```
exec /usr/local/bin/docker-entrypoint.sh: exec format error
```
Or build hangs at `RUN pip install`.

**Fix — Option 1: Clear build cache**
```bash
docker-compose build --no-cache
docker-compose up
```

**Fix — Option 2: Architecture mismatch (Apple Silicon Mac)**
If you're on an M1/M2/M3 Mac and pulled x86 images:
```bash
# Add platform to docker-compose.yml services:
postgres:
    platform: linux/amd64
mongodb:
    platform: linux/amd64
```

---

## 🔴 Problem 12: "Error starting userland proxy" (Windows)

**Symptoms:** Port binding fails silently or with a proxy error.

**Diagnose:**
```bash
netsh interface ipv4 show excludedportrange protocol=tcp
```

**Fix:**
1. Stop the Windows NAT service:
   ```powershell
   net stop winnat
   ```
2. Start Docker Desktop
3. Start the NAT service again:
   ```powershell
   net start winnat
   ```
4. Try `docker-compose up` again

---

## 🟡 Common Workflow Issues

### "I ran docker-compose up but the website shows 'Loading products...' forever"

The data loader hasn't finished yet. Check the terminal output — look for `ecommerce-data-loader` lines. Wait for `ecommerce-data-loader exited with code 0`. Then refresh the browser.

### "I made code changes but they don't appear"

The `docker-compose.yml` uses volume mounts (`./backend:/app`) so code changes ARE live. But if you changed `requirements.txt` or any Dockerfile, you need to rebuild:
```bash
docker-compose build --no-cache backend
docker-compose up
```

### "docker-compose down -v didn't delete the data"

Some Docker Desktop versions have a bug with volume removal. Delete volumes manually:
```bash
docker volume rm inf2003-grp11_postgres_data
docker volume rm inf2003-grp11_mongo_data
```

---

## 🟢 Fresh Start — Guaranteed Clean State

If NOTHING works, run this complete nuke-and-rebuild:

```bash
# 1. Stop everything
docker-compose down -v

# 2. Remove any leftover containers/images
docker rm -f ecommerce-postgres ecommerce-mongodb ecommerce-backend ecommerce-frontend 2>/dev/null
docker system prune -af

# 3. Rebuild from scratch
docker-compose build --no-cache

# 4. Start fresh
docker-compose up
```

This downloads fresh images, rebuilds everything, and starts with empty databases. It's the nuclear option but it fixes almost everything.

---

## 📞 Still stuck?

Run this diagnostic command and share the output:

```bash
echo "=== Docker Version ===" && docker version && \
echo "=== Docker Compose Version ===" && docker compose version && \
echo "=== Running Containers ===" && docker ps -a && \
echo "=== Port Usage ===" && (netstat -ano 2>/dev/null || lsof -i -P -n 2>/dev/null | grep LISTEN) && \
echo "=== Disk Space ===" && docker system df
```

This shows exactly what's running, what ports are taken, and how much disk space Docker is using.

---

*INF2003 Group 11 — Team Hanzalians — June 2026*

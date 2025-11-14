# 🚀 Deployment Guide - ISOQAR Application

## GitHub Actions CI/CD Pipeline

Aplikacija koristi GitHub Actions za automatski CI/CD proces sa tri glavna stage-a:

### 📋 Pipeline Stages

1. **Lint** - Code quality & security checks
2. **Build** - Build & test aplikacije
3. **Deploy** - Automatski deploy na production server

---

## 🔧 Setup GitHub Secrets

Pre nego što pokreneš deployment, potrebno je da konfigurišeš sledeće GitHub Secrets:

### Kako dodati secrets:
1. Idi na GitHub repository
2. Settings → Secrets and variables → Actions
3. Klikni "New repository secret"
4. Dodaj sledeće secrets:

### Required Secrets:

| Secret Name | Opis | Primer vrednosti |
|------------|------|------------------|
| `SSH_PRIVATE_KEY` | SSH privatni ključ za pristup serveru | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SERVER_HOST` | IP adresa ili hostname servera | `192.168.1.100` ili `server.example.com` |
| `SERVER_USER` | SSH korisničko ime | `deploy` ili `ubuntu` |
| `DEPLOY_PATH` | Putanja do aplikacije na serveru | `/home/deploy/isoqar-app` |
| `APP_URL` | URL aplikacije (za health check) | `http://your-server-ip` |

---

## 🔑 Generisanje SSH ključa za deployment

### Na lokalnoj mašini:

```bash
# Generiši novi SSH key pair
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key

# Ispiši PRIVATNI ključ (dodaj u GitHub Secret: SSH_PRIVATE_KEY)
cat ~/.ssh/github_deploy_key

# Ispiši JAVNI ključ (dodaj na server)
cat ~/.ssh/github_deploy_key.pub
```

### Na serveru:

```bash
# Logiraj se na server
ssh your-user@your-server

# Dodaj javni ključ u authorized_keys
echo "ssh-ed25519 AAAAC3... github-actions-deploy" >> ~/.ssh/authorized_keys

# Postavi prava
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### Testiranje SSH konekcije:

```bash
# Sa lokalne mašine
ssh -i ~/.ssh/github_deploy_key your-user@your-server
```

---

## 📦 Server Setup (Prvi put)

### 1. Instaliraj Docker i Docker Compose na serveru:

```bash
# Update sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instaliraj Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dodaj korisnika u docker grupu
sudo usermod -aG docker $USER

# Instaliraj Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verifikuj instalaciju
docker --version
docker-compose --version
```

### 2. Kloniraj repository na server:

```bash
# Kreiraj deployment folder
mkdir -p /home/deploy/isoqar-app
cd /home/deploy/isoqar-app

# Kloniraj repo (koristi deploy key ili personal access token)
git clone https://github.com/your-username/isoqar-app.git .

# Kreiraj .env fajl
cp .env.example .env
nano .env  # Podesi environment varijable
```

### 3. Konfiguriši environment varijable (.env):

```env
# Database
DATABASE_URL=postgresql://postgres:your-strong-password@db:5432/isoqar_prod
POSTGRES_DB=isoqar_prod
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-password

# Django
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-server-ip

# Email (opciono)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Prvi deployment (manuelno):

```bash
# Build i pokreni kontejnere
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d

# Proveri status
docker-compose -f docker-compose.dev.yml ps

# Proveri logove
docker-compose -f docker-compose.dev.yml logs -f web
```

---

## 🔄 Automatski Deployment Workflow

### Kada se aktivira:

- **Push na `master` ili `main` branch** → Automatski deploy
- **Push na `develop` branch** → Samo lint i build (bez deploya)
- **Pull Request** → Samo lint i build

### Deployment proces:

1. ✅ **Lint stage** - Code quality checks
   - Black (code formatting)
   - isort (import sorting)
   - Flake8 (style guide)
   - Bandit (security)
   - Safety (dependency vulnerabilities)

2. 🔨 **Build stage** - Build & test
   - Setup PostgreSQL test database
   - Run Django checks
   - Run migrations
   - Collect static files
   - Run tests
   - Build Docker image

3. 🚀 **Deploy stage** - Production deployment
   - SSH u server
   - Pull latest code
   - Backup database
   - Build Docker images
   - Restart containers
   - Run migrations
   - Collect static files
   - Health check

---

## 🔧 Manualni Deployment

Ako želiš da deployas manuelno (bez GitHub Actions):

```bash
# SSH u server
ssh deploy@your-server

# Navigiraj u app folder
cd /home/deploy/isoqar-app

# Pull latest code
git pull origin master

# Rebuild i restart
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d

# Run migrations
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

# Collect static
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput
```

---

## ⏪ Rollback

### Automatski rollback (GitHub Actions):

1. Idi na GitHub → Actions
2. Odaberi "CI/CD Pipeline" workflow
3. Klikni "Run workflow"
4. Odaberi "rollback" job

### Manualni rollback:

```bash
# SSH u server
ssh deploy@your-server
cd /home/deploy/isoqar-app

# Vrati se na prethodni commit
git log --oneline  # Vidi commit history
git reset --hard HEAD~1  # Vrati se 1 commit unazad

# Rebuild i restart
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

---

## 📊 Monitoring & Logs

### Provera statusa kontejnera:

```bash
docker-compose -f docker-compose.dev.yml ps
```

### Logovi:

```bash
# Svi logovi
docker-compose -f docker-compose.dev.yml logs -f

# Samo web kontejner
docker-compose -f docker-compose.dev.yml logs -f web

# Samo database
docker-compose -f docker-compose.dev.yml logs -f db
```

### Health check:

```bash
# Proveri da li aplikacija radi
curl http://your-server-ip/health/

# Proveri Django admin
curl http://your-server-ip/admin/
```

---

## 🔒 Security Best Practices

1. **SSH ključevi**:
   - Koristi različite SSH ključeve za različite svrhe
   - Nikad ne deli privatne ključeve
   - Redovno rotiraj ključeve

2. **Secrets**:
   - Nikad ne commituj `.env` fajlove
   - Koristi jake lozinke za bazu
   - Promeni `SECRET_KEY` u produkciji

3. **Server**:
   - Konfiguriši firewall (ufw)
   - Omogući samo potrebne portove (80, 443, 22)
   - Redovno ažuriraj sistem

4. **Docker**:
   - Redovno ažuriraj Docker images
   - Skeniraj images za vulnerabilities
   - Koristi non-root user u kontejnerima

---

## 🆘 Troubleshooting

### Problem: SSH konekcija ne radi

```bash
# Proveri SSH konfiguraciju
ssh -vvv deploy@your-server

# Proveri permissions na serveru
ls -la ~/.ssh/
```

### Problem: Docker kontejneri ne startuju

```bash
# Proveri logove
docker-compose -f docker-compose.dev.yml logs

# Proveri disk space
df -h

# Proveri Docker status
sudo systemctl status docker
```

### Problem: Database migration greška

```bash
# Uđi u web kontejner
docker-compose -f docker-compose.dev.yml exec web bash

# Proveri migracije
python manage.py showmigrations

# Fake migration (ako je potrebno)
python manage.py migrate --fake app_name migration_name
```

### Problem: Static files se ne učitavaju

```bash
# Proveri STATIC_ROOT
docker-compose -f docker-compose.dev.yml exec web python manage.py findstatic --verbosity 2 admin/css/base.css

# Ponovo collect static
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput --clear
```

---

## 📞 Support

Za pomoć kontaktiraj DevOps tim ili otvori issue na GitHub-u.

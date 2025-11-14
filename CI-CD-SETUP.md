# 🚀 CI/CD Setup Guide

## Pregled

GitHub Actions CI/CD pipeline automatizuje:
- ✅ **Lint** - Code quality & security checks
- 🔨 **Build** - Build & test aplikacije  
- 🚀 **Deploy** - Automatski deploy na production server

---

## 📋 Brzi Start

### 1. Konfiguriši GitHub Secrets

Idi na: **GitHub Repository → Settings → Secrets and variables → Actions**

Dodaj sledeće secrets:

| Secret | Vrednost | Primer |
|--------|----------|--------|
| `SSH_PRIVATE_KEY` | SSH privatni ključ | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SERVER_HOST` | IP ili hostname servera | `192.168.1.100` |
| `SERVER_USER` | SSH korisničko ime | `deploy` |
| `DEPLOY_PATH` | Putanja do app-a | `/home/deploy/isoqar-app` |
| `APP_URL` | URL aplikacije | `http://192.168.1.100` |

### 2. Generiši SSH ključ

```bash
# Generiši novi SSH key pair
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy

# Kopiraj PRIVATNI ključ (za GitHub Secret)
cat ~/.ssh/github_deploy

# Kopiraj JAVNI ključ (za server)
cat ~/.ssh/github_deploy.pub
```

### 3. Dodaj javni ključ na server

```bash
# SSH u server
ssh your-user@your-server

# Dodaj ključ
echo "ssh-ed25519 AAAAC3... github-actions" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. Testiraj SSH konekciju

```bash
ssh -i ~/.ssh/github_deploy deploy@your-server
```

---

## 🔄 Workflow Stages

### Stage 1: Lint (Code Quality)

**Šta radi:**
- ✅ Black - code formatting check
- ✅ isort - import sorting check
- ✅ Flake8 - style guide enforcement
- ✅ Bandit - security vulnerability scanning
- ✅ Safety - dependency vulnerability check

**Kada se pokreće:**
- Na svaki push
- Na svaki pull request

### Stage 2: Build & Test

**Šta radi:**
- 🔧 Setup PostgreSQL test database
- ✅ Run Django system checks
- 🗄️ Run database migrations
- 📦 Collect static files
- 🧪 Run tests
- 🐳 Build Docker image
- ✅ Test Docker image

**Kada se pokreće:**
- Posle uspešnog lint stage-a
- Na svaki push
- Na svaki pull request

### Stage 3: Deploy

**Šta radi:**
- 📥 Pull latest code na serveru
- 💾 Backup database
- 🔨 Build Docker images
- 🔄 Restart containers
- 🗄️ Run migrations
- 📦 Collect static files
- ✅ Health check

**Kada se pokreće:**
- **SAMO** na push na `master` ili `main` branch
- **NE** pokreće se na pull request-ovima
- **NE** pokreće se na `develop` branch-u

---

## 🎯 Deployment Strategije

### Automatski Deploy

```bash
# Push na master branch → automatski deploy
git push origin master
```

### Manualni Deploy

1. Idi na **GitHub → Actions**
2. Odaberi **"Manual Deploy"** workflow
3. Klikni **"Run workflow"**
4. Odaberi environment (production/staging)
5. Klikni **"Run workflow"**

### Rollback

1. Idi na **GitHub → Actions**
2. Odaberi **"CI/CD Pipeline"** workflow
3. Klikni **"Run workflow"**
4. Odaberi **"rollback"** job

---

## 📊 Monitoring

### Health Check Endpoints

```bash
# Basic health check
curl http://your-server/health/

# Readiness check (database + migrations)
curl http://your-server/health/ready/

# Liveness check (simple ping)
curl http://your-server/health/live/
```

### Logovi

```bash
# GitHub Actions logovi
GitHub → Actions → Odaberi workflow run

# Server logovi
ssh deploy@your-server
cd /home/deploy/isoqar-app
docker-compose -f docker-compose.dev.yml logs -f
```

---

## 🔧 Lokalni Development

### Testiranje Lint-a lokalno

```bash
# Install linting tools
pip install flake8 black isort bandit safety

# Run checks
black --check .
isort --check-only .
flake8 .
bandit -r .
safety check
```

### Testiranje Build-a lokalno

```bash
# Run tests
python manage.py test

# Build Docker image
docker build -t isoqar-app:test .

# Test Docker image
docker run --rm isoqar-app:test python manage.py check
```

---

## 🆘 Troubleshooting

### Problem: "Permission denied (publickey)"

**Rešenje:**
```bash
# Proveri da li je SSH ključ dodat u GitHub Secrets
# Proveri da li je javni ključ dodat na server
cat ~/.ssh/authorized_keys

# Testiranje SSH konekcije
ssh -vvv deploy@your-server
```

### Problem: "Database migration failed"

**Rešenje:**
```bash
# SSH u server
ssh deploy@your-server
cd /home/deploy/isoqar-app

# Proveri migracije
docker-compose -f docker-compose.dev.yml exec web python manage.py showmigrations

# Manuelno pokreni migracije
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### Problem: "Docker build failed"

**Rešenje:**
```bash
# Proveri disk space
df -h

# Očisti Docker cache
docker system prune -a

# Rebuild
docker-compose -f docker-compose.dev.yml build --no-cache
```

### Problem: Lint greške blokiraju deployment

**Rešenje:**
```bash
# Lokalno ispravi greške
black .
isort .

# Commit i push
git add .
git commit -m "Fix linting errors"
git push
```

---

## 📝 Best Practices

### 1. Branch Strategy

```
master/main  → Production (auto-deploy)
develop      → Development (no deploy)
feature/*    → Feature branches (no deploy)
```

### 2. Commit Messages

```bash
# Dobro
git commit -m "feat: Add IAF/EAC codes page"
git commit -m "fix: Resolve pagination issue in auditor detail"
git commit -m "docs: Update deployment guide"

# Loše
git commit -m "update"
git commit -m "fix bug"
```

### 3. Pre Push Checklist

- [ ] Lokalno testiraj promene
- [ ] Run linting tools
- [ ] Run tests
- [ ] Update dokumentaciju ako je potrebno
- [ ] Proveri da li su secrets ažurirani

### 4. Deployment Checklist

- [ ] Backup database pre deploya
- [ ] Proveri health check posle deploya
- [ ] Proveri logove za greške
- [ ] Testiraj kritične funkcionalnosti
- [ ] Imaj rollback plan

---

## 🔐 Security

### SSH Ključevi

- ✅ Koristi različite ključeve za različite svrhe
- ✅ Nikad ne commituj privatne ključeve
- ✅ Redovno rotiraj ključeve (svakih 90 dana)
- ✅ Koristi passphrase za dodatnu zaštitu

### Secrets Management

- ✅ Nikad ne hardcode-uj secrets u kodu
- ✅ Koristi GitHub Secrets za osetljive podatke
- ✅ Redovno ažuriraj lozinke
- ✅ Koristi jake lozinke (min 16 karaktera)

### Server Security

- ✅ Konfiguriši firewall (ufw)
- ✅ Omogući samo potrebne portove (22, 80, 443)
- ✅ Koristi fail2ban za zaštitu od brute-force napada
- ✅ Redovno ažuriraj sistem

---

## 📚 Dodatni Resursi

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detaljna deployment dokumentacija

---

## 💬 Podrška

Za pomoć:
1. Proveri [Troubleshooting](#-troubleshooting) sekciju
2. Proveri GitHub Actions logove
3. Proveri server logove
4. Otvori issue na GitHub-u

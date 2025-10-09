# 🔐 SSL Setup za isoqar.geo-biz.com

## Trenutno Stanje
- ✅ HTTP radi na portu 80
- ❌ HTTPS nije konfigurisan (nema SSL certifikata)

## Opcije za SSL

### Opcija 1: cPanel SSL Proxy (NAJLAKŠE) ⭐

**Preporučeno ako koristiš cPanel hosting**

1. **U cPanel-u:**
   - Idi na **SSL/TLS** → **Manage SSL sites**
   - Instaliraj SSL certifikat za `isoqar.geo-biz.com`
   - Idi na **Application Manager** ili **Proxy Setup**
   - Podesi:
     - HTTPS (443) → `localhost:80`
     - HTTP (80) → `localhost:80`

2. **Docker ostaje na HTTP portu 80**
   - cPanel će automatski dodati HTTPS
   - Korisnici pristupaju preko HTTPS
   - cPanel proxy-uje na Docker HTTP

3. **Prednosti:**
   - ✅ Automatsko obnavljanje certifikata
   - ✅ Jednostavno održavanje
   - ✅ cPanel upravlja SSL-om

---

### Opcija 2: Let's Encrypt u Docker-u

**Ako želiš SSL direktno u Docker-u**

#### Korak 1: Generiši SSL certifikate

```bash
# Na serveru
sudo apt-get install certbot

# Generiši certifikat (zaustavi Docker prvo)
docker compose -p iasoqar-app down

# Generiši certifikat
sudo certbot certonly --standalone -d isoqar.geo-biz.com -d www.isoqar.geo-biz.com

# Certifikati će biti u:
# /etc/letsencrypt/live/isoqar.geo-biz.com/fullchain.pem
# /etc/letsencrypt/live/isoqar.geo-biz.com/privkey.pem
```

#### Korak 2: Kopiraj certifikate u projekat

```bash
# Kreiraj ssl folder
mkdir -p ~/iasoqar-app/nginx/ssl

# Kopiraj certifikate
sudo cp /etc/letsencrypt/live/isoqar.geo-biz.com/fullchain.pem ~/iasoqar-app/nginx/ssl/
sudo cp /etc/letsencrypt/live/isoqar.geo-biz.com/privkey.pem ~/iasoqar-app/nginx/ssl/

# Podesi permisije
sudo chown darko:darko ~/iasoqar-app/nginx/ssl/*
```

#### Korak 3: Omogući SSL u docker-compose.yml

```yaml
nginx:
  volumes:
    - ./nginx/ssl:/etc/nginx/ssl:ro  # Uncomment ovu liniju
  ports:
    - "80:80"
    - "443:443"  # Uncomment ovu liniju
```

#### Korak 4: Omogući HTTPS u nginx/default.conf

Uncomment HTTPS server blok (linije 28-63)

#### Korak 5: Restart Docker

```bash
docker compose -p iasoqar-app down
docker compose -p iasoqar-app up -d --build
```

#### Korak 6: Automatsko obnavljanje (Cron job)

```bash
# Dodaj u crontab
sudo crontab -e

# Dodaj liniju (obnavlja svaka 3 meseca)
0 0 1 */3 * certbot renew --quiet && cp /etc/letsencrypt/live/isoqar.geo-biz.com/*.pem /home/darko/iasoqar-app/nginx/ssl/ && docker compose -p iasoqar-app restart nginx
```

---

### Opcija 3: Cloudflare SSL (Besplatno)

1. **Dodaj domen na Cloudflare**
2. **Promeni nameservere** na Cloudflare nameservere
3. **Omogući SSL** u Cloudflare dashboard-u
4. **Podesi "Full" SSL mode**
5. **Docker ostaje na HTTP** - Cloudflare dodaje HTTPS

**Prednosti:**
- ✅ Besplatno
- ✅ Automatsko obnavljanje
- ✅ DDoS zaštita
- ✅ CDN

---

## Trenutna Konfiguracija

### HTTP Only (Trenutno Aktivno)
```
Korisnik → http://isoqar.geo-biz.com:80 → Nginx:80 → Django:8000
```

### Sa cPanel SSL Proxy (Preporučeno)
```
Korisnik → https://isoqar.geo-biz.com:443 → cPanel SSL → Docker Nginx:80 → Django:8000
```

### Sa Docker SSL
```
Korisnik → https://isoqar.geo-biz.com:443 → Nginx:443 (SSL) → Django:8000
```

---

## Provera Nakon Podešavanja

```bash
# Proveri HTTP
curl http://isoqar.geo-biz.com

# Proveri HTTPS
curl https://isoqar.geo-biz.com

# Proveri SSL certifikat
openssl s_client -connect isoqar.geo-biz.com:443 -servername isoqar.geo-biz.com

# Proveri Docker kontejnere
docker compose -p iasoqar-app ps

# Proveri Nginx logove
docker compose -p iasoqar-app logs nginx
```

---

## Preporuka

**Koristi Opciju 1 (cPanel SSL Proxy)** ako:
- ✅ Već imaš cPanel hosting
- ✅ Želiš jednostavno održavanje
- ✅ Ne želiš da se brineš o obnavljanju certifikata

**Koristi Opciju 2 (Let's Encrypt)** ako:
- ✅ Imaš root pristup serveru
- ✅ Želiš potpunu kontrolu
- ✅ Nemaš cPanel

**Koristi Opciju 3 (Cloudflare)** ako:
- ✅ Želiš dodatnu zaštitu i CDN
- ✅ Želiš besplatno rešenje
- ✅ Možeš promeniti nameservere

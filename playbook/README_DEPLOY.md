# 🚀 Deployment Playbook - Rešavanje Docker Permission Problema

## Problem
```
Error response from daemon: cannot stop container: permission denied
```

## Uzrok
Korisnik `darko` nema prava da upravlja Docker kontejnerima jer nije član `docker` grupe.

## Rešenje

### Opcija 1: Automatski (Playbook)
Playbook sada automatski:
1. Proverava da li je korisnik `darko` u `docker` grupi
2. Dodaje ga u grupu ako nije
3. Resetuje Docker sesiju
4. Nastavlja sa deployment-om

### Opcija 2: Manuelno (Na serveru)
Ako i dalje ima problema, izvršite manuelno na serveru:

```bash
# 1. Dodaj korisnika u docker grupu
sudo usermod -aG docker darko

# 2. Proveri da li je dodat
groups darko

# 3. Logout/Login ili resetuj sesiju
newgrp docker

# 4. Proveri da li radi
docker ps
```

### Opcija 3: Koristi sudo (Privremeno rešenje)
Ako gore ne radi, možeš koristiti `sudo` direktno:

```yaml
- name: docker compose down
  ansible.builtin.shell: sudo docker compose down
  args:
    chdir: /home/darko/iasoqar-app
```

## Izmene u Playbook-u

### Dodato:
1. **Provera Docker grupe** - Proverava da li korisnik ima pristup
2. **Automatsko dodavanje u grupu** - Dodaje korisnika ako treba
3. **Reset sesije** - Aktivira novu grupu
4. **ignore_errors: yes** - Na `docker compose down` da ne puca ako kontejneri nisu pokrenuti

## Pokretanje

```bash
# Iz AWX-a ili komandne linije
ansible-playbook -i inventory deploy_app.yml
```

## Napomene

⚠️ **Važno:** Nakon dodavanja u `docker` grupu, korisnik mora da se logout/login ili da se resetuje sesija da bi promene stupile na snagu.

✅ **Preporuka:** Prvo manuelno dodaj korisnika u grupu na serveru, pa onda pokreni playbook.

## Provera

Nakon deployment-a, proveri:

```bash
# Na serveru
docker ps
docker compose ps
```

Trebalo bi da vidiš pokrenute kontejnere bez grešaka.

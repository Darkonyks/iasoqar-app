# 🔧 Docker Permission Denied - Troubleshooting

## Problem
Čak ni `sudo docker compose stop` ne može da zaustavi kontejner:
```
Error response from daemon: cannot stop container: permission denied
```

## Mogući Uzroci

### 1. AppArmor ili SELinux Blokira Docker
Docker daemon može biti blokiran od strane security modula.

### 2. Kontejner je Zaštićen (Protected)
Kontejner može imati posebne zaštite koje sprečavaju zaustavljanje.

### 3. Docker Daemon Problem
Docker daemon može imati problema sa permisijama.

### 4. Corrupted Container State
Kontejner može biti u nevalidnom stanju.

## Dijagnostika - Izvršite na Serveru

```bash
# 1. Proveri status Docker daemon-a
sudo systemctl status docker

# 2. Proveri Docker logove
sudo journalctl -u docker -n 50

# 3. Proveri AppArmor status
sudo aa-status | grep docker

# 4. Proveri SELinux (ako je na RHEL/CentOS)
getenforce

# 5. Proveri kontejner detalje
sudo docker inspect iasoqar-app-nginx-1

# 6. Proveri Docker daemon konfiguraciju
cat /etc/docker/daemon.json

# 7. Proveri procese
ps aux | grep docker
```

## Rešenja

### Rešenje 1: Force Kill Kontejner
```bash
# 1. Probaj force stop
sudo docker stop -t 0 iasoqar-app-nginx-1

# 2. Ako ne radi, force kill
sudo docker kill iasoqar-app-nginx-1

# 3. Ako i dalje ne radi, kill proces direktno
CONTAINER_PID=$(sudo docker inspect -f '{{.State.Pid}}' iasoqar-app-nginx-1)
sudo kill -9 $CONTAINER_PID
```

### Rešenje 2: Restartuj Docker Daemon
```bash
# 1. Restartuj Docker servis
sudo systemctl restart docker

# 2. Proveri status
sudo systemctl status docker

# 3. Pokušaj ponovo
sudo docker compose down
```

### Rešenje 3: Isključi AppArmor za Docker (Privremeno)
```bash
# 1. Proveri AppArmor profile
sudo aa-status | grep docker

# 2. Stavi Docker u complain mode
sudo aa-complain /etc/apparmor.d/docker

# 3. Ili potpuno isključi
sudo systemctl stop apparmor
sudo systemctl disable apparmor

# 4. Restartuj Docker
sudo systemctl restart docker
```

### Rešenje 4: Očisti Docker Sistem
```bash
# 1. Zaustavi sve kontejnere (force)
sudo docker ps -q | xargs -r sudo docker kill

# 2. Ukloni sve kontejnere
sudo docker ps -aq | xargs -r sudo docker rm -f

# 3. Očisti sistem
sudo docker system prune -af --volumes

# 4. Restartuj Docker
sudo systemctl restart docker
```

### Rešenje 5: Reinstaliraj Docker (Krajnje rešenje)
```bash
# 1. Zaustavi Docker
sudo systemctl stop docker

# 2. Ukloni Docker pakete
sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 3. Očisti Docker fajlove
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

# 4. Reinstaliraj Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Dodaj korisnika u docker grupu
sudo usermod -aG docker darko

# 6. Restartuj sistem
sudo reboot
```

## Brzo Rešenje za Deployment

Ako hitno trebaš da deploy-uješ, probaj:

```bash
# 1. Force kill sve
sudo docker kill $(sudo docker ps -q)

# 2. Ukloni sve kontejnere
sudo docker rm -f $(sudo docker ps -aq)

# 3. Pokreni iznova
cd ~/iasoqar-app
sudo docker compose up -d --build
```

## Prevencija

Nakon što rešiš problem, dodaj u playbook:

```yaml
- name: Force stop kontejnera ako ne radi normalno
  ansible.builtin.shell: |
    sudo docker kill $(sudo docker ps -q) || true
    sudo docker rm -f $(sudo docker ps -aq) || true
  args:
    chdir: /home/darko/iasoqar-app
  ignore_errors: yes
  
- name: Pokreni docker compose
  ansible.builtin.shell: sudo docker compose up -d --build
  args:
    chdir: /home/darko/iasoqar-app
```

## Provera Nakon Rešavanja

```bash
# 1. Proveri da kontejneri rade
sudo docker ps

# 2. Proveri logove
sudo docker compose logs -f

# 3. Proveri nginx
curl http://localhost

# 4. Proveri aplikaciju
curl http://localhost:8000
```

## Kontakt za Pomoć

Ako ništa ne radi, pošalji output od:
```bash
sudo docker version
sudo docker info
sudo systemctl status docker
sudo journalctl -u docker -n 100
```

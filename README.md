# Progress Tracker

Персональный трекер навыков с REST API, PostgreSQL, MongoDB и HTTPS.

## Стек

- FastAPI (Python)
- PostgreSQL — журнал прогресса
- MongoDB — каталог навыков
- Nginx + Let's Encrypt — reverse-proxy и SSL
- Docker Compose

## Развёртывание на новом сервере

### Требования
- Ubuntu 24.04 LTS
- Домен с A-записью, указывающей на IP сервера
- GitHub-аккаунт с доступом к репозиторию

### Пошагово

1. Подключиться к серверу:
   ```bash
   ssh root@<IP_СЕРВЕРА>

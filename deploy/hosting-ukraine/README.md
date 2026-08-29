# Hosting Ukraine — Quest (www.kvest-marafon.com)

Акаунт: `as626693` · тариф Бізнес 2G · **MySQL** (у тарифі) · Python 3.12+ · Gunicorn.

Канонічний хост: **www.kvest-marafon.com**.  
Кореневий каталог сайту: `/home/as626693/kvest-marafon.com/www/`.

---

## 1. Панель adm.tools (інфра)

### Домен і SSL

1. Сайт `www.kvest-marafon.com` прив’язаний.
2. SSL Let’s Encrypt + редірект http → https.
3. Редірект apex → www (за потреби).

### Сайт → проксування

1. **Налаштування сайту** → вкладка **Основні налаштування** → **Веб-сервер** → **Проксування трафіку** → Зберегти.
2. **Налаштування веб-застосунку** → записати локальний IP і порт → `HU_BIND_HOST` / `HU_BIND_PORT`.

### Python

1. **Налаштування хостинг-акаунта** → Python **3.12+** (достатньо 3.14).
2. SSH: `source ~/.bashrc` → `python -V`.

### MySQL (у вартості хостингу)

1. Ліве меню **MYSQL → Бази даних**.
2. Створити базу (бажано **MySQL 8.x** — Django 5.2 не підтримує 5.7).
3. Створити користувача, прив’язати до бази, зберегти пароль.
4. Дані підключення (хост, порт, ім’я БД, логін) — з картки БД у панелі.
5. Зібрати `DATABASE_URL`:
   `mysql://USER:PASSWORD@HOST:3306/DBNAME`  
   Якщо в паролі є спецсимволи (`@`, `#`, `%` тощо) — URL-encode їх.

Cloud PostgreSQL **не потрібен**.

### Каталог сайту

Код у `/home/as626693/kvest-marafon.com/www/` (шлях з панелі).  
`media/` і `staticfiles/` writable.

---

## 2. Перший деплой (SSH)

```bash
cd /home/as626693/kvest-marafon.com/www
# git clone / rsync коду сюди

cp deploy/hosting-ukraine/.env.production.example .env
# відредагувати .env: SECRET_KEY, DATABASE_URL (mysql://...), HU_BIND_*, LiqPay, Resend

# якщо python = 3.14:
PYTHON_BIN=python3.14 SEED=1 bash deploy/hosting-ukraine/bootstrap.sh
# або: PYTHON_BIN=python SEED=1 bash deploy/hosting-ukraine/bootstrap.sh
```

У панелі **Налаштування веб-застосунку**:

| Поле | Значення |
|------|----------|
| Каталог запуску | `/home/as626693/kvest-marafon.com/www` |
| Команда запуску | `bash deploy/hosting-ukraine/start.sh` |

Зберегти → запустити. Логи — «Логи застосунку».

---

## 3. Оновлення коду

```bash
cd /home/as626693/kvest-marafon.com/www
git pull
PYTHON_BIN=python bash deploy/hosting-ukraine/bootstrap.sh
# у панелі: Перезапустити веб-застосунок
```

`SEED=1` — лише перший раз.

---

## 4. Чекліст

- [ ] DNS + SSL (www і apex)
- [ ] Проксування; gunicorn на IP:порт з панелі
- [ ] MySQL 8.x; `migrate` OK
- [ ] `https://www.kvest-marafon.com/api/v1/health/` → `{"status":"ok"}`
- [ ] Адмінка /static/ і upload `/media/`
- [ ] `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS`
- [ ] LiqPay / Resend / адмін-пароль

---

## Файли

| Файл | Призначення |
|------|-------------|
| `bootstrap.sh` | venv, pip, migrate, collectstatic (+ опційний seed) |
| `start.sh` | gunicorn bind на `HU_BIND_HOST:HU_BIND_PORT` |
| `.env.production.example` | шаблон `.env` (MySQL) |

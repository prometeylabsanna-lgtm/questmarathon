# Hosting Ukraine — Quest (www.kvest-marafon.com)

Акаунт: `as626693` · тариф Бізнес 2G · Cloud PostgreSQL · Python 3.12 · Gunicorn.

Канонічний хост: **www.kvest-marafon.com**.

---

## 1. Панель adm.tools (інфра)

### Домен і SSL

1. Прив’язати `kvest-marafon.com` і `www` до хостинг-акаунта.
2. DNS (A/AAAA або NS у HU) на IP з панелі.
3. SSL Let’s Encrypt для apex + www.
4. Редірект apex → www.

### Сайт → проксування

1. **Налаштування сайту** → веб-сервер **Проксування трафіку**.
2. **Налаштування веб-застосунку** → записати локальний IP і порт (зазвичай `3000`).
3. Ці значення → `HU_BIND_HOST` / `HU_BIND_PORT` у `.env`.

### Python

1. **Налаштування хостинг-акаунта** → Python **3.12**.
2. SSH: `source ~/.bashrc` → `python3.12 -V`.

### Cloud PostgreSQL

1. Замовити інстанс PostgreSQL **16**.
2. Створити БД і користувача.
3. **Безпека** → додати хостинг-акаунт `as626693`.
4. Зібрати `DATABASE_URL`:
   `postgresql://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require`
5. Перевірка з SSH (якщо `require` падає — спробувати `prefer`).

### Каталог сайту

Код у корені сайту (шлях з панелі, напр. `~/kvest-marafon.com/`).  
`media/` і `staticfiles/` мають бути writable.

---

## 2. Перший деплой (SSH)

```bash
cd ~/kvest-marafon.com   # фактичний шлях сайту
# git clone / rsync коду сюди

cp deploy/hosting-ukraine/.env.production.example .env
# відредагувати .env: SECRET_KEY, DATABASE_URL, HU_BIND_*, LiqPay, Resend

bash deploy/hosting-ukraine/bootstrap.sh
# перший раз зі seed CMS/адміна:
# SEED=1 bash deploy/hosting-ukraine/bootstrap.sh
```

У панелі **Налаштування веб-застосунку**:

| Поле | Значення |
|------|----------|
| Каталог запуску | корінь проєкту (де `manage.py`) |
| Команда запуску | `bash deploy/hosting-ukraine/start.sh` |

Зберегти → запустити. Логи — блок «Логи застосунку».

---

## 3. Оновлення коду

```bash
cd ~/kvest-marafon.com
git pull
bash deploy/hosting-ukraine/bootstrap.sh   # без SEED
# у панелі: Перезапустити веб-застосунок
```

`migrate` / `collectstatic` — у bootstrap; **не** в start-команді.  
`seed_demo` — лише одноразово (`SEED=1`).

Supervisor для веб-процесу не потрібен (рестарт через проксування HU).

---

## 4. Чекліст

- [ ] DNS + SSL (www і apex)
- [ ] Проксування; gunicorn на IP:порт з панелі
- [ ] Cloud PG з `as626693`; migrate OK
- [ ] `https://www.kvest-marafon.com/api/v1/health/` → `{"status":"ok"}`
- [ ] Адмінка /static/ (Unfold) і upload `/media/`
- [ ] `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` — обидва хости
- [ ] `PAYMENTS_DEV_BYPASS=False`; LiqPay URL на www
- [ ] Resend + `DEFAULT_FROM_EMAIL`; SPF/DKIM за потреби
- [ ] Адмін-пароль не дефолтний; `ADMIN_PASSWORD_FORCE=False`
- [ ] Бекап Cloud PG + за потреби cron dump/media

---

## Файли

| Файл | Призначення |
|------|-------------|
| `bootstrap.sh` | venv, pip, migrate, collectstatic (+ опційний seed) |
| `start.sh` | gunicorn bind на `HU_BIND_HOST:HU_BIND_PORT` |
| `.env.production.example` | шаблон `.env` на сервері |

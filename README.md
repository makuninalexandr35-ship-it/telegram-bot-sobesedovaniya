# ИИ-тренажёр собеседований

Telegram-бот проводит последовательные HR-, профессиональные, стресс-, кейсовые и
поведенческие интервью. Вопросы учитывают профиль, вакансию, резюме и предыдущие ответы;
приложение хранит историю, рассчитывает оценку детерминированно и не показывает весь
сценарий заранее. Это первая эксплуатационная версия: платёжный провайдер ещё не подключён.

## Архитектура и безопасность

* `app/bot` — команды, inline-кнопки и FSM (Redis хранит только временное состояние).
* `app/services` — интервью, оценивание, документы, тарифы, rate limit и заменяемый ИИ.
* `app/repositories` — доступ к SQLAlchemy; PostgreSQL остаётся источником истории.
* `app/database` и `alembic` — модели и начальная миграция.
* `app/prompts` — системные инструкции вне handlers. Документы и сообщения явно помечаются
  как недоверенные данные; инструкции из них не исполняются.

Секреты берутся только из окружения. Полные документы не пишутся в обычный лог. Удаление
`User` каскадно удаляет профиль, интервью и связанные результаты. PDF-сканы без текстового
слоя не распознаются: OCR намеренно не входит в MVP.

## Что установить

Рекомендуются Git, Docker Desktop (включает Compose) и 2 ГБ свободной памяти. Для запуска
без Docker нужен Python 3.12+: скачайте его с python.org, при установке отметьте добавление
в `PATH`, затем проверьте `python --version`. Docker устанавливается с docs.docker.com;
проверьте `docker compose version`.

## Telegram и OpenAI

1. Откройте официального `@BotFather`, выполните `/newbot`, задайте имя и username.
2. Скопируйте выданный токен только в локальный `.env`; при утечке отзовите его в BotFather.
3. Создайте API-ключ в кабинете OpenAI. Ключ не даёт боту Telegram-доступа и также хранится
   только в `.env`. У аккаунта ИИ должен быть настроен биллинг.

```bash
git clone <адрес-репозитория>
cd telegram-bot-sobesedovaniya
cp .env.example .env
```

Откройте `.env`, замените placeholders, задайте сложный `POSTGRES_PASSWORD` и синхронно
обновите пароль внутри `DATABASE_URL`. `ADMIN_TELEGRAM_IDS` — числовые Telegram ID через
запятую. Модель меняется через `OPENAI_MODEL`. Цены токенов по умолчанию равны нулю;
актуальные значения можно внести в параметры `MODEL_*_PRICE_PER_MILLION`.

## Запуск в Docker

Миграции выполняются отдельной командой, а не каждым экземпляром бота:

```bash
docker compose build
docker compose up -d postgres redis
docker compose run --rm bot alembic upgrade head
docker compose up -d bot
docker compose logs -f bot
```

Проверка: откройте бота, отправьте `/start`, пройдите шесть шагов и откройте меню. Команды:
`/start`, `/menu`, `/interview`, `/progress`, `/profile`, `/settings`, `/help`, `/cancel`,
`/delete_data` и `/admin`. Последняя доступна только ID из окружения.

Остановка без удаления данных и полное удаление локальных volumes:

```bash
docker compose down
docker compose down -v  # необратимо удалит локальную БД
```

## Запуск без Docker

PostgreSQL и Redis всё равно должны работать. Укажите их адреса в `.env` (обычно
`localhost` вместо имён контейнеров).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e '.[dev]'
alembic upgrade head
python -m app.main
```

Новая миграция после изменения моделей:

```bash
alembic revision --autogenerate -m "описание изменения"
alembic upgrade head
```

## Проверки

Unit-тесты не обращаются к OpenAI. Перед публикацией выполните:

```bash
pytest
ruff check .
python -m compileall -q app tests
docker compose config
```

Для полноценной интеграционной проверки нужны реальные тестовые токены, PostgreSQL, Redis
и разрешённый сетевой доступ. Не используйте production-ключи в CI.

## Резервное копирование, сервер и обновление

Создание и восстановление дампа (файл храните зашифрованным):

```bash
docker compose exec -T postgres pg_dump -U interview -Fc interview_bot > backup.dump
docker compose exec -T postgres pg_restore -U interview -d interview_bot --clean --if-exists < backup.dump
```

Для сервера установите Docker, закройте PostgreSQL/Redis от внешней сети, скопируйте проект
и `.env` с правами `chmod 600 .env`, затем выполните команды запуска. Настройте firewall,
резервные копии и ротацию логов. Обновление:

```bash
git pull --ff-only
docker compose build bot
docker compose run --rm bot alembic upgrade head
docker compose up -d bot
```

Перед обновлением сделайте дамп. Никогда не коммитьте `.env`, не отправляйте его в чат и
не помещайте в образ. В production используйте secret manager и регулярно меняйте ключи.

## Ограничения MVP

Оплата не имитируется: модели и сервис тарифов лишь создают безопасную точку расширения.
OCR отсутствует. Стоимость ИИ зависит от внешнего тарифа и задаётся конфигурацией. Для
рассылки требуется подтверждение администратора; реализацию конкретного платёжного и
рассылочного провайдера следует добавить до коммерческого запуска.

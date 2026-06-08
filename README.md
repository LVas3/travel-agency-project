# Travel Agency Project

Python-проект для автоматизации работы туристического агентства: регистрация клиентов, подбор туров, бронирования, отзывы, справочники, договоры и статистика.

## Реализовано по требованиям

1. IDEF0, IDEF3, DFD диаграммы — `diagrams/idef0.md`, `diagrams/idef3.md`, `diagrams/dfd.md`.
2. UML диаграммы — `diagrams/uml_use_case.md`, `diagrams/uml_class.md`, `diagrams/sequence_booking.md`.
3. Схема БД — `database_schema.sql`, `diagrams/database_er.md`, SQLAlchemy-модели `server/models.py`.
4. Git-репозиторий с двумя ветками — `main` и `feature/tests-and-diagrams`.
5. Сквозные и модульные тесты — папка `server/tests`.
6. Работа с БД через SQL-запросы — `server/repositories/tour_repository_sql.py`.
7. Работа с БД через ORM — `server/repositories/tour_repository_orm.py` и CRUD в `server/main.py`.
8. Шаблон проектирования Repository — папка `server/repositories`.

Подробная таблица соответствия требованиям находится в `docs/requirements_checklist.md`.

## Стек

- Python
- FastAPI
- SQLite
- SQLAlchemy ORM
- Tkinter/ttk
- Pytest
- Mermaid Markdown diagrams

## Установка

Открыть папку `travel_agency_project` в VS Code.

Создать виртуальное окружение:

```powershell
python -m venv venv
```

Активировать окружение в Windows:

```powershell
venv\Scripts\activate
```

Установить зависимости:

```powershell
pip install -r requirements.txt
```

При проблеме с `bcrypt` выполнить:

```powershell
pip uninstall bcrypt -y
pip install bcrypt==4.0.1
```

## Запуск сервера

Из папки `travel_agency_project`:

```powershell
uvicorn server.main:app --reload
```

Документация API:

```text
http://127.0.0.1:8000/docs
```

Главная страница:

```text
http://127.0.0.1:8000/
```

## Запуск клиента

Во втором терминале:

```powershell
python client\app.py
```

## Данные администратора

```text
login: admin
password: admin123
```

## Тесты

```powershell
python -m pytest -q server/tests
```

Ожидаемый результат:

```text
8 passed
```

Тесты используют отдельную SQLite-БД и не портят рабочую базу.

## Работа с БД

По умолчанию используется база:

```text
sqlite:///./travel_agency.db
```

Для тестов или другого окружения можно задать переменную:

```powershell
$env:TRAVEL_AGENCY_DATABASE_URL="sqlite:///./test_travel_agency.db"
```

## SQL и ORM режимы

Для туров реализованы два режима работы с базой:

```text
/tours?mode=orm
/tours?mode=sql
```

`mode=orm` использует SQLAlchemy ORM, `mode=sql` использует прямые SQL-запросы.

## Публикация на GitHub

Инструкция находится в `docs/github_setup.md`.

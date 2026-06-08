# Проверка требований к проекту

| № | Требование | Где реализовано |
|---|---|---|
| 1 | IDEF0, IDEF3, DFD диаграммы | `diagrams/idef0.md`, `diagrams/idef3.md`, `diagrams/dfd.md` |
| 2 | UML Use Case, Class, Sequence | `diagrams/uml_use_case.md`, `diagrams/uml_class.md`, `diagrams/sequence_booking.md` |
| 3 | Схема БД | `database_schema.sql`, `diagrams/database_er.md`, модели `server/models.py` |
| 4 | GitHub-репозиторий минимум с двумя ветками | подготовлен локальный git-репозиторий; ветки: `main`, `feature/tests-and-diagrams`; инструкция: `docs/github_setup.md` |
| 5 | Сквозные и модульные тесты | `server/tests/test_api.py`, `server/tests/test_repositories.py`, `server/tests/test_auth.py` |
| 6 | Взаимодействие с БД через SQL-запросы | `server/repositories/tour_repository_sql.py` |
| 7 | Взаимодействие с БД через ORM | `server/repositories/tour_repository_orm.py`, CRUD endpoints в `server/main.py` |
| 8 | Шаблон проектирования | Repository: `server/repositories/base.py`, `tour_repository_orm.py`, `tour_repository_sql.py` |

## Результат проверки тестов

```text
8 passed
```

Проверка выполнялась командой:

```bash
python -m pytest -q server/tests
```

# Шаблон проектирования Repository

В проекте реализован шаблон Repository для сущности `Tour`.

## Цель

Отделить бизнес-логику API от конкретного способа работы с базой данных. Endpoint `/tours` не знает, как именно выполняются операции: через ORM или через прямой SQL.

## Компоненты

| Компонент | Назначение |
|---|---|
| `server/repositories/base.py` | Интерфейс Repository |
| `server/repositories/tour_repository_orm.py` | Реализация через SQLAlchemy ORM |
| `server/repositories/tour_repository_sql.py` | Реализация через SQL-запросы |
| `get_tour_repo()` в `server/main.py` | Выбор реализации по параметру `mode=orm/sql` |

## Использование

```text
POST /tours?mode=orm  -> TourRepositoryOrm
POST /tours?mode=sql  -> TourRepositorySql
GET  /tours?mode=orm  -> TourRepositoryOrm
GET  /tours?mode=sql  -> TourRepositorySql
```

Такой подход позволяет выполнить сразу два требования: взаимодействие с БД через ORM и взаимодействие с БД через SQL-запросы.

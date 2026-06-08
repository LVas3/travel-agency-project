from decimal import Decimal
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session
from server import schemas


class TourRepositorySql:
    """Repository pattern: CRUD и поиск туров через прямые SQL-запросы."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_sql_params(tour: schemas.TourCreate) -> dict:
        data = tour.model_dump()
        if isinstance(data["price"], Decimal):
            data["price"] = float(data["price"])
        if isinstance(data["start_date"], date):
            data["start_date"] = data["start_date"].isoformat()
        if isinstance(data["end_date"], date):
            data["end_date"] = data["end_date"].isoformat()
        return data

    def add(self, tour: schemas.TourCreate):
        sql = text("""
            INSERT INTO tours(name, type, description, price, start_date, end_date)
            VALUES (:name, :type, :description, :price, :start_date, :end_date)
        """)
        result = self.db.execute(sql, self._to_sql_params(tour))
        self.db.commit()
        return self.get(result.lastrowid)

    def delete(self, tour_id: int) -> bool:
        result = self.db.execute(text("DELETE FROM tours WHERE id = :id"), {"id": tour_id})
        self.db.commit()
        return result.rowcount > 0

    def update(self, tour_id: int, tour: schemas.TourCreate):
        params = self._to_sql_params(tour)
        params["id"] = tour_id
        result = self.db.execute(text("""
            UPDATE tours
            SET name=:name, type=:type, description=:description,
                price=:price, start_date=:start_date, end_date=:end_date
            WHERE id=:id
        """), params)
        self.db.commit()
        if result.rowcount == 0:
            return None
        return self.get(tour_id)

    def get(self, tour_id: int):
        row = self.db.execute(
            text("SELECT id, name, type, description, price, start_date, end_date FROM tours WHERE id=:id"),
            {"id": tour_id},
        ).mappings().first()
        return dict(row) if row else None

    def search(self, name: str | None = None, tour_type: str | None = None, max_price: float | None = None):
        sql = "SELECT id, name, type, description, price, start_date, end_date FROM tours WHERE 1=1"
        params = {}
        if name:
            sql += " AND lower(name) LIKE lower(:name)"
            params["name"] = f"%{name}%"
        if tour_type:
            sql += " AND type = :type"
            params["type"] = tour_type
        if max_price is not None:
            sql += " AND price <= :max_price"
            params["max_price"] = max_price
        sql += " ORDER BY id DESC"
        rows = self.db.execute(text(sql), params).mappings().all()
        return [dict(row) for row in rows]

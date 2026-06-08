from sqlalchemy.orm import Session
from server import models, schemas


class TourRepositoryOrm:
    """Repository pattern: CRUD and search through SQLAlchemy ORM."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, tour: schemas.TourCreate) -> models.Tour:
        db_tour = models.Tour(**tour.model_dump())
        self.db.add(db_tour)
        self.db.commit()
        self.db.refresh(db_tour)
        return db_tour

    def get(self, tour_id: int):
        return self.db.query(models.Tour).filter(models.Tour.id == tour_id).first()

    def delete(self, tour_id: int) -> bool:
        tour = self.get(tour_id)
        if not tour:
            return False
        self.db.delete(tour)
        self.db.commit()
        return True

    def update(self, tour_id: int, data: schemas.TourCreate):
        tour = self.get(tour_id)
        if not tour:
            return None
        for key, value in data.model_dump().items():
            setattr(tour, key, value)
        self.db.commit()
        self.db.refresh(tour)
        return tour

    def search(self, name: str | None = None, tour_type: str | None = None, max_price: float | None = None):
        query = self.db.query(models.Tour)
        if name:
            query = query.filter(models.Tour.name.ilike(f"%{name}%"))
        if tour_type:
            query = query.filter(models.Tour.type == tour_type)
        if max_price is not None:
            query = query.filter(models.Tour.price <= max_price)
        return query.all()

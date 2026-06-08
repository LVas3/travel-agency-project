from decimal import Decimal
from datetime import date

from server import schemas
from server.repositories.tour_repository_orm import TourRepositoryOrm
from server.repositories.tour_repository_sql import TourRepositorySql


def make_tour(name: str) -> schemas.TourCreate:
    return schemas.TourCreate(
        name=name,
        type="tourist",
        description="Unit test tour",
        price=Decimal("700.00"),
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 7),
    )


def test_orm_repository_crud(db_session):
    repo = TourRepositoryOrm(db_session)
    tour = repo.add(make_tour("ORM Unit Tour"))

    assert tour.id is not None
    assert repo.get(tour.id).name == "ORM Unit Tour"
    assert len(repo.search(name="ORM Unit")) == 1

    updated = repo.update(tour.id, make_tour("ORM Unit Tour Updated"))
    assert updated.name == "ORM Unit Tour Updated"

    assert repo.delete(tour.id) is True
    assert repo.get(tour.id) is None


def test_sql_repository_crud(db_session):
    repo = TourRepositorySql(db_session)
    tour = repo.add(make_tour("SQL Unit Tour"))
    tour_id = tour["id"]

    assert tour_id is not None
    assert repo.get(tour_id)["name"] == "SQL Unit Tour"
    assert len(repo.search(name="SQL Unit")) == 1

    updated = repo.update(tour_id, make_tour("SQL Unit Tour Updated"))
    assert updated["name"] == "SQL Unit Tour Updated"

    assert repo.delete(tour_id) is True
    assert repo.get(tour_id) is None

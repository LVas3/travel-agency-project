from decimal import Decimal
from datetime import date
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from server.database import Base, engine, get_db
from server import models, schemas
from server.auth import hash_password, verify_password
from server.repositories.tour_repository_orm import TourRepositoryOrm
from server.repositories.tour_repository_sql import TourRepositorySql

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Travel Agency API")

TOUR_TYPES = ["cruise", "resort", "tourist", "business", "exclusive"]


def create_default_admin():
    db = next(get_db())
    try:
        admin = db.query(models.User).filter(models.User.login == "admin").first()
        if not admin:
            admin = models.User(login="admin", password_hash=hash_password("admin123"), role="admin")
            db.add(admin)
            db.commit()
    finally:
        db.close()


def create_demo_data():
    db = next(get_db())
    try:
        if db.query(models.Tour).count() == 0:
            db.add_all([
                models.Tour(name="Круиз по Средиземному морю", type="cruise", description="Италия, Испания, Франция", price=1200, start_date=date(2026, 7, 10), end_date=date(2026, 7, 20)),
                models.Tour(name="Курортный отдых в Турции", type="resort", description="Отель 5 звезд, все включено", price=850, start_date=date(2026, 8, 1), end_date=date(2026, 8, 8)),
                models.Tour(name="Туристический тур по Праге", type="tourist", description="Экскурсии, музеи, старый город", price=520, start_date=date(2026, 9, 5), end_date=date(2026, 9, 10)),
                models.Tour(name="Бизнес-поездка в Берлин", type="business", description="Трансфер, отель, конференция", price=980, start_date=date(2026, 10, 2), end_date=date(2026, 10, 5)),
                models.Tour(name="Эксклюзивный тур на Мальдивы", type="exclusive", description="Вилла, индивидуальный трансфер", price=3500, start_date=date(2026, 11, 15), end_date=date(2026, 11, 25)),
            ])
            db.commit()
        if db.query(models.Hotel).count() == 0:
            db.add_all([
                models.Hotel(name="Sea Palace Resort", country="Турция", city="Анталья", stars=5, address="Beach street, 1"),
                models.Hotel(name="Prague Center Hotel", country="Чехия", city="Прага", stars=4, address="Old Town, 12"),
            ])
            db.commit()
        if db.query(models.Carrier).count() == 0:
            db.add_all([
                models.Carrier(name="Turkish Airlines", transport_type="plane", phone="+90 000 000"),
                models.Carrier(name="Mediterranean Cruises", transport_type="ship", phone="+39 000 000"),
            ])
            db.commit()
    finally:
        db.close()


create_default_admin()
create_demo_data()


@app.get("/")
def root():
    return {"message": "Travel Agency API работает. Документация: /docs"}


@app.post("/auth/register")
def register_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.login == data.login).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    if data.role not in ["admin", "client"]:
        raise HTTPException(status_code=400, detail="Role must be admin or client")
    user = models.User(login=data.login, password_hash=hash_password(data.password), role=data.role)
    db.add(user)
    db.commit()
    return {"message": "registered", "login": user.login, "role": user.role}


@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.login == data.login).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    return {"message": "login successful", "role": user.role, "user_id": user.id, "client_id": user.client_id}


@app.post("/auth/register-client", response_model=schemas.TokenResponse)
def register_client(data: schemas.ClientRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.login == data.login).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    client = models.Client(full_name=data.full_name, phone=data.phone, email=data.email, passport_number=data.passport_number)
    db.add(client)
    db.commit()
    db.refresh(client)
    user = models.User(login=data.login, password_hash=hash_password(data.password), role="client", client_id=client.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "client registered", "role": user.role, "user_id": user.id, "client_id": client.id}


@app.post("/clients", response_model=schemas.ClientRead)
def create_client(data: schemas.ClientCreate, db: Session = Depends(get_db)):
    client = models.Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@app.get("/clients", response_model=list[schemas.ClientRead])
def search_clients(name: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Client)
    if name:
        query = query.filter(models.Client.full_name.ilike(f"%{name}%"))
    return query.order_by(models.Client.id.desc()).all()


@app.put("/clients/{client_id}", response_model=schemas.ClientRead)
def update_client(client_id: int, data: schemas.ClientCreate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, value in data.model_dump().items():
        setattr(client, key, value)
    db.commit()
    db.refresh(client)
    return client


@app.delete("/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": "deleted"}


def get_tour_repo(mode: str, db: Session):
    if mode == "sql":
        return TourRepositorySql(db)
    return TourRepositoryOrm(db)


@app.post("/tours", response_model=schemas.TourRead)
def create_tour(data: schemas.TourCreate, mode: str = Query("orm", pattern="^(orm|sql)$"), db: Session = Depends(get_db)):
    if data.type not in TOUR_TYPES:
        raise HTTPException(status_code=400, detail="Invalid tour type")
    repo = get_tour_repo(mode, db)
    return repo.add(data)


@app.get("/tours")
def search_tours(
    name: str | None = None,
    type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    mode: str = Query("orm", pattern="^(orm|sql)$"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Tour)

    if name:
        query = query.filter(models.Tour.name.ilike(f"%{name}%"))

    if type:
        query = query.filter(models.Tour.type == type)

    if min_price is not None:
        query = query.filter(models.Tour.price >= min_price)

    if max_price is not None:
        query = query.filter(models.Tour.price <= max_price)

    return query.order_by(models.Tour.id.desc()).all()


@app.put("/tours/{tour_id}")
def update_tour(tour_id: int, data: schemas.TourCreate, mode: str = Query("orm", pattern="^(orm|sql)$"), db: Session = Depends(get_db)):
    repo = get_tour_repo(mode, db)
    tour = repo.update(tour_id, data)
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    return tour


@app.delete("/tours/{tour_id}")
def delete_tour(tour_id: int, mode: str = Query("orm", pattern="^(orm|sql)$"), db: Session = Depends(get_db)):
    repo = get_tour_repo(mode, db)
    if not repo.delete(tour_id):
        raise HTTPException(status_code=404, detail="Tour not found")
    return {"message": "deleted"}


@app.post("/bookings", response_model=schemas.BookingRead)
def create_booking(data: schemas.BookingCreate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == data.client_id).first()
    tour = db.query(models.Tour).filter(models.Tour.id == data.tour_id).first()
    if not client or not tour:
        raise HTTPException(status_code=404, detail="Client or tour not found")
    booking = models.Booking(client_id=data.client_id, tour_id=data.tour_id, status=data.status, total_price=Decimal(tour.price))
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@app.get("/bookings")
def list_bookings(status: str | None = None, db: Session = Depends(get_db)):
    query = (
        db.query(models.Booking, models.Client, models.Tour)
        .join(models.Client, models.Booking.client_id == models.Client.id)
        .join(models.Tour, models.Booking.tour_id == models.Tour.id)
    )

    if status:
        query = query.filter(models.Booking.status == status)

    rows = query.order_by(models.Booking.id.desc()).all()

    return [
        {
            "id": booking.id,
            "client_full_name": client.full_name,
            "client_phone": client.phone,
            "tour_name": tour.name,
            "booking_date": booking.booking_date.strftime("%d.%m.%Y %H:%M:%S"),
            "status": booking.status,
            "total_price": booking.total_price,
        }
        for booking, client, tour in rows
    ]


@app.put("/bookings/{booking_id}", response_model=schemas.BookingRead)
def update_booking(booking_id: int, data: schemas.BookingUpdate, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = data.status
    db.commit()
    db.refresh(booking)
    return booking


@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    db.delete(booking)
    db.commit()
    return {"message": "deleted"}


@app.get("/bookings/client/{client_id}")
def list_client_bookings(client_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(models.Booking, models.Tour)
        .join(models.Tour, models.Booking.tour_id == models.Tour.id)
        .filter(models.Booking.client_id == client_id)
        .order_by(models.Booking.id.desc())
        .all()
    )

    return [
        {
            "id": booking.id,
            "tour_name": tour.name,
            "booking_date": booking.booking_date.strftime("%d.%m.%Y %H:%M:%S"),
            "status": booking.status,
            "total_price": booking.total_price,
        }
        for booking, tour in rows
    ]


@app.post("/reviews", response_model=schemas.ReviewRead)
def create_review(data: schemas.ReviewCreate, db: Session = Depends(get_db)):
    review = models.Review(**data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@app.get("/reviews", response_model=list[schemas.ReviewRead])
def list_reviews(tour_id: int | None = None, client_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Review)
    if tour_id:
        query = query.filter(models.Review.tour_id == tour_id)
    if client_id:
        query = query.filter(models.Review.client_id == client_id)
    return query.order_by(models.Review.id.desc()).all()


@app.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"message": "deleted"}


# Универсальные CRUD-разделы для сущностей задания: маршруты, отели, перевозчики, договоры.
def crud_list(db, model, filters: dict):
    query = db.query(model)
    for field, value in filters.items():
        if value is not None:
            column = getattr(model, field)
            query = query.filter(column == value)
    return query.order_by(model.id.desc()).all()


def crud_create(db, model, data):
    item = model(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def crud_update(db, model, item_id, data):
    item = db.query(model).filter(model.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def crud_delete(db, model, item_id):
    item = db.query(model).filter(model.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "deleted"}


@app.get("/routes", response_model=list[schemas.RouteRead])
def list_routes(tour_id: int | None = None, db: Session = Depends(get_db)):
    return crud_list(db, models.Route, {"tour_id": tour_id})


@app.post("/routes", response_model=schemas.RouteRead)
def create_route(data: schemas.RouteCreate, db: Session = Depends(get_db)):
    return crud_create(db, models.Route, data)


@app.put("/routes/{item_id}", response_model=schemas.RouteRead)
def update_route(item_id: int, data: schemas.RouteCreate, db: Session = Depends(get_db)):
    return crud_update(db, models.Route, item_id, data)


@app.delete("/routes/{item_id}")
def delete_route(item_id: int, db: Session = Depends(get_db)):
    return crud_delete(db, models.Route, item_id)


@app.get("/hotels", response_model=list[schemas.HotelRead])
def list_hotels(city: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Hotel)
    if city:
        query = query.filter(models.Hotel.city.ilike(f"%{city}%"))
    return query.order_by(models.Hotel.id.desc()).all()


@app.post("/hotels", response_model=schemas.HotelRead)
def create_hotel(data: schemas.HotelCreate, db: Session = Depends(get_db)):
    return crud_create(db, models.Hotel, data)


@app.put("/hotels/{item_id}", response_model=schemas.HotelRead)
def update_hotel(item_id: int, data: schemas.HotelCreate, db: Session = Depends(get_db)):
    return crud_update(db, models.Hotel, item_id, data)


@app.delete("/hotels/{item_id}")
def delete_hotel(item_id: int, db: Session = Depends(get_db)):
    return crud_delete(db, models.Hotel, item_id)


@app.get("/carriers", response_model=list[schemas.CarrierRead])
def list_carriers(transport_type: str | None = None, db: Session = Depends(get_db)):
    return crud_list(db, models.Carrier, {"transport_type": transport_type})


@app.post("/carriers", response_model=schemas.CarrierRead)
def create_carrier(data: schemas.CarrierCreate, db: Session = Depends(get_db)):
    return crud_create(db, models.Carrier, data)


@app.put("/carriers/{item_id}", response_model=schemas.CarrierRead)
def update_carrier(item_id: int, data: schemas.CarrierCreate, db: Session = Depends(get_db)):
    return crud_update(db, models.Carrier, item_id, data)


@app.delete("/carriers/{item_id}")
def delete_carrier(item_id: int, db: Session = Depends(get_db)):
    return crud_delete(db, models.Carrier, item_id)


@app.get("/hotel-contracts", response_model=list[schemas.HotelContractRead])
def list_hotel_contracts(hotel_id: int | None = None, db: Session = Depends(get_db)):
    return crud_list(db, models.HotelContract, {"hotel_id": hotel_id})


@app.post("/hotel-contracts", response_model=schemas.HotelContractRead)
def create_hotel_contract(data: schemas.HotelContractCreate, db: Session = Depends(get_db)):
    return crud_create(db, models.HotelContract, data)


@app.put("/hotel-contracts/{item_id}", response_model=schemas.HotelContractRead)
def update_hotel_contract(item_id: int, data: schemas.HotelContractCreate, db: Session = Depends(get_db)):
    return crud_update(db, models.HotelContract, item_id, data)


@app.delete("/hotel-contracts/{item_id}")
def delete_hotel_contract(item_id: int, db: Session = Depends(get_db)):
    return crud_delete(db, models.HotelContract, item_id)


@app.get("/carrier-contracts", response_model=list[schemas.CarrierContractRead])
def list_carrier_contracts(carrier_id: int | None = None, db: Session = Depends(get_db)):
    return crud_list(db, models.CarrierContract, {"carrier_id": carrier_id})


@app.post("/carrier-contracts", response_model=schemas.CarrierContractRead)
def create_carrier_contract(data: schemas.CarrierContractCreate, db: Session = Depends(get_db)):
    return crud_create(db, models.CarrierContract, data)


@app.put("/carrier-contracts/{item_id}", response_model=schemas.CarrierContractRead)
def update_carrier_contract(item_id: int, data: schemas.CarrierContractCreate, db: Session = Depends(get_db)):
    return crud_update(db, models.CarrierContract, item_id, data)


@app.delete("/carrier-contracts/{item_id}")
def delete_carrier_contract(item_id: int, db: Session = Depends(get_db)):
    return crud_delete(db, models.CarrierContract, item_id)


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    popular = (
        db.query(models.Tour.name, func.count(models.Booking.id).label("count"))
        .join(models.Booking, models.Booking.tour_id == models.Tour.id, isouter=True)
        .group_by(models.Tour.id)
        .order_by(func.count(models.Booking.id).desc())
        .first()
    )
    return {
        "clients": db.query(models.Client).count(),
        "tours": db.query(models.Tour).count(),
        "bookings": db.query(models.Booking).count(),
        "reviews": db.query(models.Review).count(),
        "hotels": db.query(models.Hotel).count(),
        "carriers": db.query(models.Carrier).count(),
        "popular_tour": popular[0] if popular else "нет данных",
        "popular_tour_bookings": popular[1] if popular else 0,
    }

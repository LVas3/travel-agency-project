from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="client", nullable=False)  # admin или client
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)

    client = relationship("Client", back_populates="user")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    passport_number = Column(String, nullable=False)

    user = relationship("User", back_populates="client", uselist=False)
    bookings = relationship("Booking", back_populates="client")
    reviews = relationship("Review", back_populates="client")


class Tour(Base):
    __tablename__ = "tours"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, default="")
    price = Column(Numeric(10, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    routes = relationship("Route", back_populates="tour", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="tour")
    reviews = relationship("Review", back_populates="tour")


class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    visit_order = Column(Integer, nullable=False)
    description = Column(Text, default="")

    tour = relationship("Tour", back_populates="routes")


class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    stars = Column(Integer, nullable=False)
    address = Column(String, nullable=False)

    contracts = relationship("HotelContract", back_populates="hotel")


class Carrier(Base):
    __tablename__ = "carriers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    transport_type = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    contracts = relationship("CarrierContract", back_populates="carrier")


class HotelContract(Base):
    __tablename__ = "hotel_contracts"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    contract_number = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    terms = Column(Text, default="")

    hotel = relationship("Hotel", back_populates="contracts")


class CarrierContract(Base):
    __tablename__ = "carrier_contracts"
    id = Column(Integer, primary_key=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carriers.id"), nullable=False)
    contract_number = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    terms = Column(Text, default="")

    carrier = relationship("Carrier", back_populates="contracts")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    booking_date = Column(DateTime, default=utc_now)
    status = Column(String, default="created")
    total_price = Column(Numeric(10, 2), nullable=False)

    client = relationship("Client", back_populates="bookings")
    tour = relationship("Tour", back_populates="bookings")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(Text, default="")
    created_at = Column(DateTime, default=utc_now)

    client = relationship("Client", back_populates="reviews")
    tour = relationship("Tour", back_populates="reviews")

from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    login: str
    password: str
    role: str = "client"


class ClientRegister(BaseModel):
    login: str
    password: str
    full_name: str
    phone: str
    email: str
    passport_number: str


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    message: str
    role: str
    user_id: int
    client_id: int | None = None


class ClientBase(BaseModel):
    full_name: str
    phone: str
    email: str
    passport_number: str


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TourBase(BaseModel):
    name: str
    type: str = Field(description="cruise, resort, tourist, business, exclusive")
    description: str = ""
    price: Decimal = Field(gt=0)
    start_date: date
    end_date: date


class TourCreate(TourBase):
    pass


class TourRead(TourBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class BookingCreate(BaseModel):
    client_id: int
    tour_id: int
    status: str = "created"


class BookingUpdate(BaseModel):
    status: str = "created"


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    tour_id: int
    booking_date: datetime
    status: str
    total_price: Decimal


class ReviewCreate(BaseModel):
    client_id: int
    tour_id: int
    rating: int = Field(ge=1, le=5)
    text: str = ""


class ReviewRead(ReviewCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class RouteCreate(BaseModel):
    tour_id: int
    country: str
    city: str
    visit_order: int
    description: str = ""


class RouteRead(RouteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class HotelCreate(BaseModel):
    name: str
    country: str
    city: str
    stars: int = Field(ge=1, le=5)
    address: str


class HotelRead(HotelCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CarrierCreate(BaseModel):
    name: str
    transport_type: str
    phone: str


class CarrierRead(CarrierCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class HotelContractCreate(BaseModel):
    hotel_id: int
    contract_number: str
    start_date: date
    end_date: date
    terms: str = ""


class HotelContractRead(HotelContractCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CarrierContractCreate(BaseModel):
    carrier_id: int
    contract_number: str
    start_date: date
    end_date: date
    terms: str = ""


class CarrierContractRead(CarrierContractCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

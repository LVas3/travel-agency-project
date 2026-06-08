from datetime import date, datetime
from decimal import Decimal
import re 
from pydantic import BaseModel, ConfigDict, Field, field_validator

LOGIN_RE = re.compile(r"^[a-zA-Z0-9_]{4,20}$")
EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
PHONE_RE = re.compile(r"^\+?\d{10,15}$")
PASSPORT_RE = re.compile(r"^\d{10}$")


def validate_login_value(value: str) -> str:
    value = value.strip()

    if not LOGIN_RE.match(value):
        raise ValueError(
            "Логин должен быть от 4 до 20 символов: латиница, цифры или _"
        )

    return value


def validate_password_value(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Пароль должен быть не короче 8 символов")

    if " " in value:
        raise ValueError("Пароль не должен содержать пробелы")

    if not re.search(r"[A-Za-z]", value):
        raise ValueError("Пароль должен содержать хотя бы одну букву")

    if not re.search(r"\d", value):
        raise ValueError("Пароль должен содержать хотя бы одну цифру")

    return value


def validate_email_value(value: str) -> str:
    value = value.strip()

    if not EMAIL_RE.match(value):
        raise ValueError("Введите корректный email")

    return value


def validate_phone_value(value: str) -> str:
    value = value.strip().replace(" ", "").replace("-", "")

    if not PHONE_RE.match(value):
        raise ValueError("Телефон должен содержать 10-15 цифр")

    return value


def validate_passport_value(value: str) -> str:
    value = value.strip().replace(" ", "")

    if not PASSPORT_RE.match(value):
        raise ValueError("Паспорт должен содержать 10 цифр")

    return value
class UserCreate(BaseModel):
    login: str
    password: str
    role: str = "client"

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        return validate_login_value(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_value(value)

class ClientRegister(BaseModel):
    login: str
    password: str
    full_name: str
    phone: str
    email: str
    passport_number: str

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        return validate_login_value(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_value(value)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 3:
            raise ValueError("ФИО должно быть не короче 3 символов")

        return value
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return validate_phone_value(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email_value(value)

    @field_validator("passport_number")
    @classmethod
    def validate_passport(cls, value: str) -> str:
        return validate_passport_value(value)



class LoginRequest(BaseModel):
    login: str
    password: str

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Введите логин")
        return value.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value:
            raise ValueError("Введите пароль")
        return value

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

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 3:
            raise ValueError("ФИО должно быть не короче 3 символов")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return validate_phone_value(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email_value(value)

    @field_validator("passport_number")
    @classmethod
    def validate_passport(cls, value: str) -> str:
        return validate_passport_value(value)


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

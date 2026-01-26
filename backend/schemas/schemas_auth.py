from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional
import re
from datetime import date

APPROVED_CARD_TYPES = {"visa", "mastercard", "amex", "discover"}

class FinanceInfo(BaseModel):
    bank: Optional[str] = None
    credit_card_number: Optional[str] = Field(None, min_length=16, max_length=16)
    cvv: Optional[str] = Field(None, min_length=3, max_length=3)
    pin: Optional[str] = Field(None, min_length=4, max_length=4)
    account_type: Optional[str] = None  # maps to AccountTypeEnum
    card_type: Optional[str] = None

    @field_validator("credit_card_number")
    def cc_digits(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"\d{16}", v):
            raise ValueError("Credit card must be 16 digits with no spaces")
        return v

    @field_validator("cvv")
    def cvv_digits(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"\d{3}", v):
            raise ValueError("CVV must be exactly 3 digits")
        return v

    @field_validator("card_type")
    def card_type_allowed(cls, v):
        if v is None:
            return v
        if v.lower() not in APPROVED_CARD_TYPES:
            raise ValueError("Card type must be approved")
        return v

class ShippingInfo(BaseModel):
    postal_code: Optional[str] = None
    street_line_1: Optional[str] = None
    street_line_2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    country: Optional[str] = None

    @field_validator("postal_code")
    def ca_postal(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"[A-Z]\d[A-Z] \d[A-Z]\d", v):
            raise ValueError("Postal code must follow Canadian format: A2A 2A2")
        return v

class UserRegisterRequest(BaseModel):
    full_name: str
    dob: date
    email: EmailStr
    phone_number: str
    password: str
    confirm_password: str
    profile_image: Optional[str] = None
    finance: Optional[FinanceInfo] = None
    shipping: Optional[ShippingInfo] = None

    @field_validator("dob")
    def dob_not_future(cls, v):
        if v > date.today():
            raise ValueError("Date of Birth cannot be in the future")
        return v

    @field_validator("phone_number")
    def phone_format(cls, v):
        if not re.fullmatch(r"\d{3}-\d{3}-\d{4}", v):
            raise ValueError("Phone number must be 555-555-5555 format")
        return v

    @field_validator("password")
    def password_complexity(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must include an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must include a lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must include a number")
        if not re.fullmatch(r"[A-Za-z0-9!\-_,*]+", v):
            raise ValueError("Password has invalid characters")
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        if self.confirm_password != self.password:
            raise ValueError("Passwords do not match")
        return self

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[date] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    profile_image: Optional[str] = None
    account_status: Optional[str] = None
    finance: Optional[FinanceInfo] = None
    shipping: Optional[ShippingInfo] = None

class SellerUpgradeRequest(BaseModel):
    store_name: str
    contact_email: EmailStr
    finance: Optional[FinanceInfo] = None
    shipping: Optional[ShippingInfo] = None

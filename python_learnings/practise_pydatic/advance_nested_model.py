from pydantic import BaseModel


class Country(BaseModel):
    name: str
    code: str


class State(BaseModel):
    name: str
    country: Country


class City(BaseModel):
    name: str
    state: State


class Address(BaseModel):
    street: str
    city: City
    post_code: str


class Organization(BaseModel):
    name: str
    head_quarter: Address

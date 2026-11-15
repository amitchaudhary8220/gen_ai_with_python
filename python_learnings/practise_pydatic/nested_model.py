from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    postal_code: str


class User(BaseModel):
    id: int
    name: str
    address: Address


address = Address(street="123", city="Lucknow", postal_code="10001")
user = User(id=1, name="Amit Chaudhary", address=address)
print(user)

user_data = {
    "id": 2,
    "name": "Ankit Chaudhary",
    "address": {"street": "E block", "city": "Lucknow", "postal_code": "202060"},
}

user2 = User(**user_data)
print(f"user2 is ---->>> {user2}")

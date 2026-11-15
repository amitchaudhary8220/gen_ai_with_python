from multiprocessing import Value

from pydantic import BaseModel, Field, field_validator, model_validator


class Employee(BaseModel):
    id: int
    name: str = Field(
        ...,
       min_length=3,
       max_length=50,
       description="Employee Name",
       examples=["Amit Chaudhary"])
    department: str = 'General'
    slaray: float = Field(
        ...,
        ge=10000
    )

class User(BaseModel):
    username: str 



    @field_validator('username')
    def username_length(cls,v):
        if len(v) < 4:
            raise ValueError("Usenme must be atleast 4 characters")
        return v

class SignupDate(BaseModel):
    password: str
    confirm_password:str

    @model_validator(mode="after")
    def password_match(cls,values):
         if values.password != values.confirm_password:
           raise ValueError("Password do not match")
         return values
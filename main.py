from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from geopy.distance import geodesic

# Database connection
SQLALCHEMY_DATABASE_URL = "mysql://username:password@localhost/our_databasename"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class AddressBook(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String(255), index=True)  
    city = Column(String(100), index=True)    
    state = Column(String(100), index=True)   
    country = Column(String(100), index=True) 
    latitude = Column(Float)
    longitude = Column(Float)

# Create tables
Base.metadata.create_all(bind=engine) 

# Pydantic models
class AddressCreate(BaseModel):
    street: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float

class AddressUpdate(BaseModel):
    street: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float

class AddressOut(BaseModel):
    id: int
    street: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float

# FastAPI app
app = FastAPI()

# CRUD operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/addresses/", response_model=AddressOut)
def create_address(address: AddressCreate, db: SessionLocal = Depends(get_db)):
    db_address = AddressBook(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

@app.put("/addresses/{address_id}", response_model=AddressOut)
def update_address(address_id: int, address: AddressUpdate, db: SessionLocal = Depends(get_db)):
    db_address = db.query(AddressBook).filter(AddressBook.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    for key, value in address.dict().items():
        setattr(db_address, key, value)
    db.commit()
    db.refresh(db_address)
    return db_address

@app.delete("/addresses/{address_id}", response_model=AddressOut)
def delete_address(address_id: int, db: SessionLocal = Depends(get_db)):
    db_address = db.query(AddressBook).filter(AddressBook.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(db_address)
    db.commit()
    return db_address

@app.get("/addresses/", response_model=List[AddressOut])
def get_addresses(db: SessionLocal = Depends(get_db)):
    return db.query(AddressBook).all()

@app.get("/addresses/find/")
def search_addresses(latitude: float, longitude: float, distance: float = Query(...), db: SessionLocal = Depends(get_db)):
    addresses = db.query(AddressBook).all()
    filtered_addresses = []
    user_location = (latitude, longitude)
    for address in addresses:
        address_location = (address.latitude, address.longitude)
        if geodesic(user_location, address_location).km <= distance:
            filtered_addresses.append(address)
    return filtered_addresses





if __name__=="__main__":
    uvicorn.run("main:app")
























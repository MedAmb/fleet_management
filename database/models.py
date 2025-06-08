from sqlalchemy import Column, Integer, String, Boolean, Float
from database.schema import Base

class Vehicle(Base):
    __tablename__ = "vehicle"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, nullable=False)
    vehicle_type = Column(String)
    default_destination = Column(String)
    odometer_functional = Column(Boolean, default=True)
    fuel_conversion_constant = Column(Float)

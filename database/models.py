from datetime import date, time

from sqlalchemy import (Boolean, Column, Date, Float, ForeignKey, Integer,
                        String, Time)

from database.schema import Base


class Vehicle(Base):
    __tablename__ = "vehicle"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, nullable=False)
    vehicle_type = Column(String)
    default_destination = Column(String)
    odometer_functional = Column(Boolean, default=True)
    fuel_conversion_constant = Column(Float)


class TripLog(Base):
    __tablename__ = "trip_log"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id"), nullable=False)

    trip_date = Column(Date, default=date.today, nullable=False)
    trip_time = Column(Time, default=lambda: time(0, 0), nullable=False)

    odometer_start = Column(Float, nullable=True)
    odometer_end = Column(Float, nullable=True)
    fuel_used = Column(Float, nullable=False)

    actual_destination = Column(String, nullable=True)
    rerouted = Column(Boolean, default=False)
    refueled = Column(Boolean, default=False)
    refuel_amount = Column(Float, nullable=True)

    distance_travelled = Column(Float, nullable=False)

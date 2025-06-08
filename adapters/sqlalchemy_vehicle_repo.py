from sqlalchemy.orm import Session
from database.models import Vehicle
from repositories.vehicle_repository import AbstractVehicleRepository


class SQLAlchemyVehicleRepository(AbstractVehicleRepository):
    def __init__(self, session: Session):
        self.session = session

    # CRUD
    def add(self, vehicle: Vehicle) -> None:
        self.session.add(vehicle)
        self.session.commit()

    def get_by_plate(self, plate: str):
        return (
            self.session
            .query(Vehicle)
            .filter_by(plate_number=plate)
            .first()
        )

    def get_all(self):
        return self.session.query(Vehicle).all()

    def update(self, plate: str, **kwargs):
        v = self.get_by_plate(plate)
        if not v:
            raise ValueError("Vehicle not found")
        for k, val in kwargs.items():
            if hasattr(v, k):
                setattr(v, k, val)
        self.session.commit()

    def delete(self, plate: str):
        v = self.get_by_plate(plate)
        if not v:
            raise ValueError("Vehicle not found")
        self.session.delete(v)
        self.session.commit()

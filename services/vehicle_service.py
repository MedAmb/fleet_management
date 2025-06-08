from database.models import Vehicle
from repositories.vehicle_repository import AbstractVehicleRepository


class VehicleService:
    def __init__(self, repo: AbstractVehicleRepository):
        self.repo = repo

    # Use-cases
    def create_vehicle(self, plate: str, **attrs) -> None:
        if self.repo.get_by_plate(plate):
            raise ValueError("Vehicle already exists")
        vehicle = Vehicle(plate_number=plate, **attrs)
        self.repo.add(vehicle)

    def list_vehicles(self):
        return self.repo.get_all()

    def edit_vehicle(self, plate: str, **changes):
        self.repo.update(plate, **changes)

    def remove_vehicle(self, plate: str):
        self.repo.delete(plate)

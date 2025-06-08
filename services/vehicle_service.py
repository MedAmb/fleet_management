from database.models import Vehicle
from repositories.vehicle_repository import AbstractVehicleRepository


class VehicleService:
    def __init__(self, repo: AbstractVehicleRepository):
        self.repo = repo

    # Use-cases
    def create_vehicle(self, plate: str, **attrs) -> None:
        if self.repo.get_by_plate(plate):
            raise ValueError("Ce véhicule existe déjà")
        vehicle = Vehicle(plate_number=plate, **attrs)
        self.repo.add(vehicle)

    def list_vehicles(self):
        return self.repo.get_all()

    def edit_vehicle(self, plate: str, **changes):
        self.repo.update(plate, **changes)

    def remove_vehicle(self, plate: str):
        self.repo.delete(plate)

    def list_vehicle_types(self) -> list[str]:
        return sorted({v.vehicle_type for v in self.list_vehicles() if v.vehicle_type})

    def list_destinations(self) -> list[str]:
        return sorted(
            {
                v.default_destination
                for v in self.list_vehicles()
                if v.default_destination
            }
        )

    def get_by_plate(self, plate: str):
        return self.repo.get_by_plate(plate)  # type: ignore[attr-defined]

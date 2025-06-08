import pytest

from database.models import Vehicle
from repositories.vehicle_repository import AbstractVehicleRepository
from services.vehicle_service import VehicleService


class InMemoryRepo(AbstractVehicleRepository):
    def __init__(self):
        self._data = {}

    def add(self, vehicle: Vehicle):
        self._data[vehicle.plate_number] = vehicle

    def get_by_plate(self, plate):
        return self._data.get(plate)

    def get_all(self):
        return list(self._data.values())

    def update(self, plate, **kwargs):
        v = self.get_by_plate(plate)
        if not v:
            raise ValueError
        for k, v_ in kwargs.items():
            setattr(v, k, v_)

    def delete(self, plate):
        self._data.pop(plate, None)


def test_create_and_list_vehicle():
    repo = InMemoryRepo()
    service = VehicleService(repo)

    service.create_vehicle("ABC-123", vehicle_type="Truck")

    vehicles = service.list_vehicles()
    assert len(vehicles) == 1
    assert vehicles[0].plate_number == "ABC-123"

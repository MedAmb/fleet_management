from datetime import date, time

from database.models import TripLog, Vehicle
from repositories.triplog_repository import AbstractTripLogRepository
from repositories.vehicle_repository import AbstractVehicleRepository
from services.triplog_service import TripLogService


class InMemVehicleRepo(AbstractVehicleRepository):
    def __init__(self):
        self.data = {}

    def add(self, v):
        self.data[v.plate_number] = v

    def get_by_plate(self, p):
        return self.data.get(p)

    def get_all(self):
        return list(self.data.values())

    def update(self, p, **k):
        pass

    def delete(self, p):
        pass


class InMemTripRepo(AbstractTripLogRepository):
    def __init__(self):
        self.store = []

    def add(self, t):
        self.store.append(t)

    def get(self, i):
        return next((t for t in self.store if t.id == i), None)

    def list_for_vehicle(self, vid, s, e):
        return [t for t in self.store if t.vehicle_id == vid]


def test_record_trip_with_working_odometer():
    vrepo = InMemVehicleRepo()
    trepo = InMemTripRepo()
    vrepo.add(Vehicle(id=1, plate_number="ABC-123", odometer_functional=True))
    svc = TripLogService(vrepo, trepo)

    svc.record_trip(
        plate_number="ABC-123",
        trip_date=date.today(),
        trip_time=time(8, 0),
        fuel_used=50,
        odometer_start=1000,
        odometer_end=1200,
    )

    assert len(trepo.store) == 1
    trip: TripLog = trepo.store[0]
    assert trip.distance_travelled == 200

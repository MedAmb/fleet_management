# tests/unit/test_report_service.py
from datetime import date
from typing import List, Optional

from database.models import TripLog, Vehicle
from repositories.triplog_repository import AbstractTripLogRepository
from repositories.vehicle_repository import AbstractVehicleRepository
from services.report_service import ReportService


# ─────────────────────────────── in-memory mock repos ──
class InMemVehicleRepo(AbstractVehicleRepository):
    def __init__(self) -> None:
        self._data = {}

    # CRUD
    def add(self, vehicle: Vehicle) -> None:
        self._data[vehicle.plate_number] = vehicle

    def get_by_plate(self, plate: str) -> Optional[Vehicle]:
        return self._data.get(plate)

    def get_all(self) -> List[Vehicle]:
        return list(self._data.values())

    def update(self, plate: str, **kwargs) -> None: ...
    def delete(self, plate: str) -> None: ...


class InMemTripRepo(AbstractTripLogRepository):
    def __init__(self) -> None:
        self._store: List[TripLog] = []

    def add(self, trip: TripLog) -> None:
        self._store.append(trip)

    def get(self, trip_id: int): ...  # not needed for these tests

    def list_for_vehicle(self, vehicle_id, start: date, end: date) -> List[TripLog]:
        return [
            t
            for t in self._store
            if t.vehicle_id == vehicle_id and start <= t.trip_date <= end
        ]


# ─────────────────────────────────────────── tests ──
def _setup() -> ReportService:
    vrepo = InMemVehicleRepo()
    trepo = InMemTripRepo()

    car = Vehicle(id=1, plate_number="ABC-123", odometer_functional=True)
    vrepo.add(car)

    trepo.add(
        TripLog(
            vehicle_id=1,
            trip_date=date(2025, 6, 1),
            fuel_used=50,
            distance_travelled=600,
        )
    )
    trepo.add(
        TripLog(
            vehicle_id=1,
            trip_date=date(2025, 6, 2),
            fuel_used=40,
            distance_travelled=480,
        )
    )

    return ReportService(vrepo, trepo)


def test_vehicle_summary():
    svc = _setup()
    summary = svc.vehicle_summary("ABC-123", date(2025, 6, 1), date(2025, 6, 30))

    assert summary["trip_count"] == 2
    assert summary["total_distance"] == 1080
    assert summary["total_fuel"] == 90
    assert abs(summary["avg_eff"] - 12.0) < 0.01

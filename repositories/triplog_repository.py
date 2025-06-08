from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from database.models import TripLog


class AbstractTripLogRepository(ABC):
    @abstractmethod
    def add(self, trip: TripLog) -> None: ...
    @abstractmethod
    def get(self, trip_id: int) -> Optional[TripLog]: ...
    @abstractmethod
    def list_for_vehicle(
        self, vehicle_id: int, start: date, end: date
    ) -> List[TripLog]: ...

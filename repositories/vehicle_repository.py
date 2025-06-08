from abc import ABC, abstractmethod
from typing import List, Optional

from database.models import Vehicle


class AbstractVehicleRepository(ABC):
    @abstractmethod
    def add(self, vehicle: Vehicle) -> None: ...
    @abstractmethod
    def get_by_plate(self, plate: str) -> Optional[Vehicle]: ...
    @abstractmethod
    def get_all(self) -> List[Vehicle]: ...
    @abstractmethod
    def update(self, plate: str, **kwargs) -> None: ...
    @abstractmethod
    def delete(self, plate: str) -> None: ...

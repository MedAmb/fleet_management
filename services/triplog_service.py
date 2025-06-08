from datetime import date, time
from typing import Optional

from database.models import TripLog
from repositories.triplog_repository import AbstractTripLogRepository
from repositories.vehicle_repository import AbstractVehicleRepository


class TripLogService:
    def __init__(
        self, vehicles: AbstractVehicleRepository, trips: AbstractTripLogRepository
    ):
        self.vehicles = vehicles
        self.trips = trips

    def record_trip(
        self,
        plate_number: str,
        trip_date: date,
        trip_time: time,
        fuel_used: float,
        odometer_start: Optional[float] = None,
        odometer_end: Optional[float] = None,
        actual_destination: Optional[str] = None,
        rerouted: bool = False,
        refueled: bool = False,
        refuel_amount: Optional[float] = None,
    ) -> None:
        vehicle = self.vehicles.get_by_plate(plate_number)
        if not vehicle:
            raise ValueError("Véhicule non enregistré")

        # compute distance
        if vehicle.odometer_functional:
            if odometer_start is None or odometer_end is None:
                raise ValueError("Les deux relevés d'odomètre sont requis")
            if odometer_end < odometer_start:
                raise ValueError(
                    "La fin de l'odomètre ne peut pas être inférieure au début"
                )
            distance = odometer_end - odometer_start
        else:
            if vehicle.fuel_conversion_constant is None:
                raise ValueError("Constante de conversion carburant→distance manquante")
            distance = fuel_used * vehicle.fuel_conversion_constant
            if distance <= 0:
                raise ValueError("La distance calculée doit être positive")

        trip = TripLog(
            vehicle_id=vehicle.id,
            trip_date=trip_date,
            trip_time=trip_time,
            odometer_start=odometer_start,
            odometer_end=odometer_end,
            fuel_used=fuel_used,
            actual_destination=actual_destination,
            rerouted=rerouted,
            refueled=refueled,
            refuel_amount=refuel_amount,
            distance_travelled=distance,
        )
        self.trips.add(trip)

    def last_trips(self, limit: int = 100) -> list[TripLog]:
        """
        Retourne les `limit` trajets les plus récents, toutes plaques
        confondues, triés par date+heure décroissantes.
        """
        all_trips: list[TripLog] = []
        for v in self.vehicles.get_all():  # type: ignore[attr-defined]
            all_trips.extend(
                self.trips.list_for_vehicle(  # type: ignore[attr-defined]
                    v.id, date(2000, 1, 1), date.today()
                )
            )
        all_trips.sort(key=lambda t: (t.trip_date, t.trip_time), reverse=True)
        return all_trips[:limit]

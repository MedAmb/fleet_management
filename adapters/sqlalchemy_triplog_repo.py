from datetime import date

from sqlalchemy.orm import Session

from database.models import TripLog
from repositories.triplog_repository import AbstractTripLogRepository


class SQLAlchemyTripLogRepository(AbstractTripLogRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, trip: TripLog) -> None:
        self.session.add(trip)
        self.session.commit()

    def get(self, trip_id: int):
        return self.session.query(TripLog).get(trip_id)

    def list_for_vehicle(self, vehicle_id: int, start: date, end: date):
        return (
            self.session.query(TripLog)
            .filter(
                TripLog.vehicle_id == vehicle_id,
                TripLog.trip_date.between(start, end),
            )
            .all()
        )

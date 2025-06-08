from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List

from database.models import TripLog, Vehicle
from repositories.triplog_repository import AbstractTripLogRepository
from repositories.vehicle_repository import AbstractVehicleRepository


class ReportService:
    """
    Couche métier d'agrégation (aucun appel SQLAlchemy direct).
    """

    def __init__(
        self,
        vehicle_repo: AbstractVehicleRepository,
        trip_repo: AbstractTripLogRepository,
    ) -> None:
        self._vehicles = vehicle_repo
        self._trips = trip_repo

    # ─────────────────────────────────────────── helpers ──
    @staticmethod
    def _aggregate(trips: List[TripLog]) -> Dict[str, float]:
        total_km = sum(t.distance_travelled for t in trips)
        total_fuel = sum(t.fuel_used for t in trips)
        return {
            "trip_count": len(trips),
            "total_distance": total_km,
            "total_fuel": total_fuel,
            "avg_eff": total_km / total_fuel if total_fuel else 0,
        }

    # ─────────────────────────────────────────── public ──
    def vehicle_summary(self, plate: str, start: date, end: date) -> Dict:
        vehicle: Vehicle | None = self._vehicles.get_by_plate(plate)
        if not vehicle:
            raise ValueError("Plaque inconnue")

        trips = self._trips.list_for_vehicle(vehicle.id, start, end)
        agg = self._aggregate(trips)
        return {**agg, "vehicle": vehicle, "trips": trips, "start": start, "end": end}

    def fleet_summary(self, start: date, end: date) -> Dict:
        vehicles = self._vehicles.get_all()
        trips: List[TripLog] = []
        for v in vehicles:
            trips.extend(self._trips.list_for_vehicle(v.id, start, end))

        agg = self._aggregate(trips)
        return {
            **agg,
            "vehicle_count": len(vehicles),
            "trips": trips,
            "start": start,
            "end": end,
        }

    # ─────────────────────────────── PDF export facultatif ──
    @staticmethod
    def export_pdf(summary: Dict, pdf_path: Path) -> Path:
        """
        Écrit un rapport PDF basique via ReportLab.
        Nécessite `reportlab` dans requirements.txt.
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen.canvas import Canvas

        c = Canvas(str(pdf_path), pagesize=A4)
        w, h = A4
        y = h - 40
        c.setFont("Helvetica-Bold", 16)

        titre = (
            f"Rapport – {summary['vehicle'].plate_number}"
            if "vehicle" in summary
            else "Rapport – Flotte complète"
        )
        c.drawString(40, y, titre)
        y -= 30

        c.setFont("Helvetica", 10)
        c.drawString(
            40,
            y,
            f"Période : {summary['start']} → {summary['end']}",
        )
        y -= 20
        c.drawString(40, y, f"Trajets : {summary['trip_count']}")
        y -= 20
        c.drawString(
            40,
            y,
            f"Distance : {summary['total_distance']:.1f} km   "
            f"Carburant : {summary['total_fuel']:.1f} L",
        )
        y -= 20
        c.drawString(
            40,
            y,
            f"Efficacité moyenne : {summary['avg_eff']:.2f} km/L",
        )
        c.save()
        return pdf_path

from datetime import date

from PyQt5.QtCore import QDate, QTime, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from services.triplog_service import TripLogService
from services.vehicle_service import VehicleService


class TripLogTab(QWidget):
    """Daily trip entry + quick table"""

    tripAdded = pyqtSignal()

    def __init__(
        self,
        vehicle_service: VehicleService,
        trip_service: TripLogService,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._vehicles = vehicle_service
        self._trips = trip_service

        layout = QVBoxLayout(self)

        # ── form row ───────────────────────────────────────────────
        row = QHBoxLayout()
        self.cb_plate = QComboBox()
        self._populate_plate()
        self.dt_date = QDateEdit(QDate.currentDate())
        self.dt_date.setCalendarPopup(True)
        self.tm_time = QTimeEdit(QTime.currentTime())
        self.in_start = QLineEdit()
        self.in_start.setPlaceholderText("Odo début")
        self.in_end = QLineEdit()
        self.in_end.setPlaceholderText("Odo fin")
        self.in_fuel = QLineEdit()
        self.in_fuel.setPlaceholderText("Carburant *")

        btn_add = QPushButton("Ajouter trajet")
        btn_add.clicked.connect(self._on_add)

        for w in (
            self.cb_plate,
            self.dt_date,
            self.tm_time,
            self.in_start,
            self.in_end,
            self.in_fuel,
            btn_add,
        ):
            row.addWidget(w)
        layout.addLayout(row)

        # ── table ─────────────────────────────────────────────────
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self._refresh()

    # ──────────────────────────────────────────────────────────────
    def _populate_plate(self) -> None:
        self.cb_plate.clear()
        for v in self._vehicles.list_vehicles():
            self.cb_plate.addItem(v.plate_number)

    def _on_add(self) -> None:
        plate = self.cb_plate.currentText()
        try:
            self._trips.record_trip(
                plate_number=plate,
                trip_date=self.dt_date.date().toPyDate(),
                trip_time=self.tm_time.time().toPyTime(),
                fuel_used=float(self.in_fuel.text()),
                odometer_start=(
                    float(self.in_start.text()) if self.in_start.text() else None
                ),
                odometer_end=float(self.in_end.text()) if self.in_end.text() else None,
            )
            self._refresh()

            # vider le formulaire
            self.in_start.clear()
            self.in_end.clear()
            self.in_fuel.clear()

            self.tripAdded.emit()

        except Exception as exc:
            QMessageBox.critical(self, "Erreur", str(exc))

    def _refresh(self) -> None:
        trips = self._trips.last_trips(100)  # ← simple & clean
        self.table.setRowCount(len(trips))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Carburant (L)", "Km", "Plaque"])

        plates = {v.id: v.plate_number for v in self._vehicles.list_vehicles()}
        for r, t in enumerate(trips):
            self.table.setItem(r, 0, QTableWidgetItem(str(t.trip_date)))
            self.table.setItem(r, 1, QTableWidgetItem(f"{t.fuel_used:.1f}"))
            self.table.setItem(r, 2, QTableWidgetItem(f"{t.distance_travelled:.1f}"))
            self.table.setItem(r, 3, QTableWidgetItem(plates.get(t.vehicle_id, "—")))

    def refresh_plate_list(self) -> None:
        self._populate_plate()

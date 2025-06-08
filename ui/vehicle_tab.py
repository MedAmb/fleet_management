from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from services.vehicle_service import VehicleService


class VehicleTab(QWidget):
    """
    Tab for adding, listing, and updating vehicles.
    Emits `vehicleAdded` whenever a new vehicle is successfully saved.
    """

    vehicleAdded = pyqtSignal()

    # ------------------------------------------------------------------
    def __init__(self, vehicle_service: VehicleService, parent=None) -> None:
        super().__init__(parent)
        self._service = vehicle_service
        layout = QVBoxLayout(self)

        # ── form row ───────────────────────────────────────────────
        form = QHBoxLayout()

        self.in_plate = QLineEdit()
        self.in_plate.setPlaceholderText("Plaque *")

        # Editable combo boxes for type & destination
        self.cb_type = QComboBox()
        self.cb_type.setEditable(True)
        self.cb_type.addItems(self._service.list_vehicle_types())
        self.cb_type.setPlaceholderText("Type")

        self.cb_dest = QComboBox()
        self.cb_dest.setEditable(True)
        self.cb_dest.addItems(self._service.list_destinations())
        self.cb_dest.setPlaceholderText("Destination")

        self.cb_odo_ok = QCheckBox("Odomètre OK")
        self.cb_odo_ok.setChecked(True)

        self.in_const = QLineEdit()
        self.in_const.setPlaceholderText("Const. carburant→km")
        self.in_const.setEnabled(False)
        self.cb_odo_ok.stateChanged.connect(
            lambda _: self.in_const.setEnabled(not self.cb_odo_ok.isChecked())
        )

        btn_save = QPushButton("Ajouter / Mettre à jour")
        btn_save.clicked.connect(self._on_save)

        for w in (
            self.in_plate,
            self.cb_type,
            self.cb_dest,
            self.cb_odo_ok,
            self.in_const,
            btn_save,
        ):
            form.addWidget(w)

        layout.addLayout(form)

        # ── table ─────────────────────────────────────────────────
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self._refresh()

    # ------------------------------------------------------------------
    # Slots & helpers
    # ------------------------------------------------------------------
    def _on_save(self) -> None:
        plate = self.in_plate.text().strip()
        try:
            existing = self._service.get_by_plate(plate)
            data = dict(
                vehicle_type=self.cb_type.currentText().strip() or None,
                default_destination=self.cb_dest.currentText().strip() or None,
                odometer_functional=self.cb_odo_ok.isChecked(),
                fuel_conversion_constant=(
                    float(self.in_const.text()) if self.in_const.text() else None
                ),
            )

            if existing:
                # ── update path ─────────────────────────────────────
                self._service.edit_vehicle(plate, **data)
            else:
                # ── create path ────────────────────────────────────
                self._service.create_vehicle(plate=plate, **data)

            self._refresh()
            self.vehicleAdded.emit()

        except Exception as exc:
            QMessageBox.critical(self, "Erreur", str(exc))

    def _refresh(self) -> None:
        """Reload vehicle list into the table."""
        vehicles = self._service.list_vehicles()
        self.table.setRowCount(len(vehicles))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Plaque", "Type", "Destination", "Odo OK", "Const."]
        )

        for r, v in enumerate(vehicles):
            self.table.setItem(r, 0, QTableWidgetItem(v.plate_number))
            self.table.setItem(r, 1, QTableWidgetItem(v.vehicle_type or ""))
            self.table.setItem(r, 2, QTableWidgetItem(v.default_destination or ""))
            self.table.setItem(
                r, 3, QTableWidgetItem("✓" if v.odometer_functional else "✗")
            )
            self.table.setItem(
                r, 4, QTableWidgetItem(str(v.fuel_conversion_constant or ""))
            )

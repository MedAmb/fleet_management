# ui/report_tab.py
from datetime import date
from pathlib import Path

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.report_service import ReportService
from services.vehicle_service import VehicleService


class ReportTab(QWidget):
    """Tab that displays trip summaries and lets the user export a PDF."""

    def __init__(
        self,
        vehicle_service: VehicleService,
        report_service: ReportService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._vehicles = vehicle_service
        self._reports = report_service
        self._summary = None  # filled after Generate

        layout = QVBoxLayout(self)

        # ── top control row ────────────────────────────────────────────
        ctrl = QHBoxLayout()
        self.cb_plate = QComboBox()
        self.cb_plate.addItem("<Tous les véhicules>")
        for v in self._vehicles.list_vehicles():
            self.cb_plate.addItem(v.plate_number)

        self.dt_start = QDateEdit(QDate.currentDate().addMonths(-1))
        self.dt_start.setCalendarPopup(True)
        self.dt_end = QDateEdit(QDate.currentDate())
        self.dt_end.setCalendarPopup(True)

        btn_gen = QPushButton("Generate")
        btn_pdf = QPushButton("Export PDF")
        btn_gen.setText("Générer")
        btn_pdf.setText("Exporter PDF")

        btn_gen.clicked.connect(self._on_generate)
        btn_pdf.clicked.connect(self._on_export_pdf)

        for w in (self.cb_plate, self.dt_start, self.dt_end, btn_gen, btn_pdf):
            ctrl.addWidget(w)
        layout.addLayout(ctrl)

        # ── results table ─────────────────────────────────────────────
        self.table = QTableWidget()
        layout.addWidget(self.table)

    # ── slots ─────────────────────────────────────────────────────────
    def _on_generate(self) -> None:
        plate = self.cb_plate.currentText()
        start = self.dt_start.date().toPyDate()
        end = self.dt_end.date().toPyDate()

        try:
            if plate == "<Tous les véhicules>":
                self._summary = self._reports.fleet_summary(start, end)
            else:
                self._summary = self._reports.vehicle_summary(plate, start, end)
        except Exception as exc:
            QMessageBox.critical(self, "Erreur de rapport", str(exc))
            return

        trips = self._summary["trips"]
        self.table.setRowCount(len(trips))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Date", "Plaque", "Carburant (L)", "Km", "Km / L"]
        )

        # cache plates for all-vehicles view
        plates = {v.id: v.plate_number for v in self._vehicles.list_vehicles()}

        for r, t in enumerate(trips):
            eff = t.distance_travelled / t.fuel_used if t.fuel_used else 0
            self.table.setItem(r, 0, QTableWidgetItem(str(t.trip_date)))
            self.table.setItem(
                r,
                1,
                QTableWidgetItem(
                    plate
                    if plate != "<Tous les véhicules>"
                    else plates.get(t.vehicle_id, "—")
                ),
            )
            self.table.setItem(r, 2, QTableWidgetItem(f"{t.fuel_used:.1f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{t.distance_travelled:.1f}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{eff:.2f}"))

    def refresh_plate_list(self) -> None:
        current = self.cb_plate.currentText()
        self.cb_plate.blockSignals(True)  # avoid accidental Generate
        self.cb_plate.clear()
        self.cb_plate.addItem("<Tous les véhicules>")
        for v in self._vehicles.list_vehicles():
            self.cb_plate.addItem(v.plate_number)
        # Restore previous selection if possible
        idx = self.cb_plate.findText(current)
        if idx != -1:
            self.cb_plate.setCurrentIndex(idx)
        self.cb_plate.blockSignals(False)

    def _on_export_pdf(self) -> None:
        if not self._summary:
            QMessageBox.information(
                self, "Pas de données", "Générez d'abord un rapport."
            )
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer PDF",
            str(Path.home() / "rapport.pdf"),
            "Fichiers PDF (*.pdf)",
        )
        if not path:
            return
        try:
            ReportService.export_pdf(self._summary, Path(path))
        except Exception as exc:
            QMessageBox.critical(self, "Erreur d'export", str(exc))
            return
        QMessageBox.information(self, "Enregistré", "PDF exporté avec succès.")

    def refresh_after_trip(self) -> None:
        if self._summary:  # seulement si un rapport est déjà affiché
            self._on_generate()

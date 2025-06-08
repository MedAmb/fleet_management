from PyQt5.QtWidgets import QMainWindow, QTabWidget

from adapters.sqlalchemy_triplog_repo import SQLAlchemyTripLogRepository
from adapters.sqlalchemy_vehicle_repo import SQLAlchemyVehicleRepository
from database.session_provider import get_session
from services.report_service import ReportService
from services.triplog_service import TripLogService
from services.vehicle_service import VehicleService
from ui.report_tab import ReportTab
from ui.triplog_tab import TripLogTab
from ui.vehicle_tab import VehicleTab


class MainWindow(QMainWindow):
    """Wires repositories → services → tabs."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Gestion de flotte")
        self.resize(1000, 600)

        # ── DB session + repos ──────────────────────────────────────
        self._sess_ctx = get_session()
        self._session = self._sess_ctx.__enter__()

        v_repo = SQLAlchemyVehicleRepository(self._session)
        t_repo = SQLAlchemyTripLogRepository(self._session)

        # ── services ────────────────────────────────────────────────
        self.vehicle_service = VehicleService(v_repo)
        self.trip_service = TripLogService(v_repo, t_repo)
        self.report_service = ReportService(v_repo, t_repo)

        # ── tabs (exposed as attrs) ─────────────────────────────────
        self.vehicle_tab = VehicleTab(self.vehicle_service)
        self.trip_tab = TripLogTab(self.vehicle_service, self.trip_service)
        self.report_tab = ReportTab(self.vehicle_service, self.report_service)

        tabs = QTabWidget()
        tabs.addTab(self.vehicle_tab, "Véhicules")
        tabs.addTab(self.trip_tab, "Trajets")
        tabs.addTab(self.report_tab, "Rapports")
        self.setCentralWidget(tabs)

        # refresh Trip tab’s plate list whenever a vehicle is added
        self.vehicle_tab.vehicleAdded.connect(self.trip_tab.refresh_plate_list)
        self.vehicle_tab.vehicleAdded.connect(self.report_tab.refresh_plate_list)
        self.trip_tab.tripAdded.connect(self.report_tab.refresh_after_trip)

    # ------------------------------------------------------------------
    def closeEvent(self, event):  # type: ignore[override]
        """Ensure SQLAlchemy session closes cleanly on app exit."""
        self._sess_ctx.__exit__(None, None, None)
        super().closeEvent(event)

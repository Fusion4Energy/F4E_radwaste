import sys

import pyvista as pv
from pyvistaqt import MainWindow, QtInteractor
from qtpy import QtWidgets

from f4e_radwaste.gui.gui_processing import (
    gui_standard_process,
    gui_filtered_process,
    gui_by_component_process,
)
from f4e_radwaste.gui.widgets.overlaid_box_widget import OverlaidBoxWidget
from f4e_radwaste.gui.widgets.results_widget import ResultsWidget

STATUS_BAR_MESSAGE_WELCOME = "Welcome to F4E Radwaste"
WINDOW_TITLE = "F4E Radwaste"
COLOR_BLACK = "black"
COLOR_WHITE = "white"


class MainWindowGUI(MainWindow):
    overlaid_box_widget: OverlaidBoxWidget
    results_widget: ResultsWidget

    def __init__(self, manager):
        self._app = QtWidgets.QApplication(sys.argv)
        super().__init__()

        # Create the widgets
        self.overlaid_box_widget = OverlaidBoxWidget(parent=self, manager=manager)
        self.plotter = self._build_plotter()
        self.results_widget = ResultsWidget(parent=self, manager=manager)

        # Add widgets to the horizontal layout
        self._build_horizontal_layout(
            self.overlaid_box_widget, self.plotter, self.results_widget
        )
        self._add_menu_bar(manager=manager)

    def start(self):
        self.show()
        sys.exit(self._app.exec_())

    def _build_horizontal_layout(self, *widgets):
        # create the window
        self.setWindowTitle(WINDOW_TITLE)
        self.statusBar().showMessage(STATUS_BAR_MESSAGE_WELCOME)
        # create the frame
        frame = QtWidgets.QFrame(None)
        main_horizontal_layout = QtWidgets.QHBoxLayout()
        # set the layout in the frame and set the frame in the window
        frame.setLayout(main_horizontal_layout)
        self.setCentralWidget(frame)
        # populate the main layout with all the widgets
        for widget in widgets:
            # noinspection PyArgumentList
            main_horizontal_layout.addWidget(widget)

    def _build_plotter(self):
        plotter = QtInteractor()
        self.signal_close.connect(plotter.close)
        plotter.set_background(COLOR_WHITE)
        pv.global_theme.font.color = COLOR_BLACK
        return plotter

    def _add_menu_bar(self, manager):
        main_menu: QtWidgets.QMenuBar = self.menuBar()

        # Post-processing menu
        post_process_menu = main_menu.addMenu("Processing")
        post_process_menu.addAction("Standard processing", gui_standard_process)
        post_process_menu.addAction("Cell-filtered processing", gui_filtered_process)
        post_process_menu.addAction("By component processing", gui_by_component_process)

        # Visualization menu
        file_menu = main_menu.addMenu("Visualization")
        file_menu.addAction(
            "Load data tables folder",
            manager.functions.menu_action_load_data_tables_folder,
        )

        # Exit
        # noinspection PyTypeChecker
        exit_button = main_menu.addAction("Exit", self.close)
        exit_button.setShortcut("q")

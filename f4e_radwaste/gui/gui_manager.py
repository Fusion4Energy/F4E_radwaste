from pathlib import Path
from typing import Optional
import pyvista as pv

from f4e_radwaste.gui.gui_functions import GUIFunctions
from f4e_radwaste.gui.gui_processor import GUIProcessor
from f4e_radwaste.gui.main_window import MainWindowGUI


class GUIManager:
    def __init__(self):
        self.processor: Optional[GUIProcessor] = None

        self.grid: pv.StructuredGrid = pv.StructuredGrid()
        self.geo_meshes: dict[str, pv.DataSet] = {}

        self.functions: GUIFunctions = GUIFunctions(manager=self)
        self.main_window: MainWindowGUI = MainWindowGUI(manager=self)

    def start(self):
        self.functions.active = True
        self.main_window.start()

    def load_new_data_processor(self, data_tables_folder_path: Path):
        self.processor = GUIProcessor(data_tables_folder_path)


if __name__ == "__main__":
    _manager = GUIManager()
    _manager.start()

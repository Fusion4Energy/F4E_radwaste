from dataclasses import dataclass
from pathlib import Path


@dataclass
class FolderPaths:
    input_files: Path
    data_tables: Path
    csv_results: Path
    vtk_results: Path

from dataclasses import dataclass

from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.meshgrids import create_grid
from f4e_radwaste.post_processing.folder_paths import FolderPaths


@dataclass
class MeshOutput:
    name: str
    data_mesh_info: DataMeshInfo
    data_mesh_activity: DataMeshActivity

    def save(self, folder_paths: FolderPaths):
        self.save_csv_tables(folder_paths)
        self.save_as_vtk_file(folder_paths)
        print(f"{self.name} processed!")

    def save_csv_tables(self, folder_paths: FolderPaths):
        self.data_mesh_activity.to_csv(folder_paths.csv_results, self.name)

    def save_as_vtk_file(self, folder_paths: FolderPaths):
        grid = create_grid(self.data_mesh_info, self.data_mesh_activity)
        grid.save(f"{folder_paths.vtk_results}/{self.name}.vts")

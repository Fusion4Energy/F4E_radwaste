from dataclasses import dataclass

from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.post_processing.folder_paths import FolderPaths


@dataclass
class ComponentOutput:
    name: str
    data_mesh_activity: DataMeshActivity

    def save(self, folder_paths: FolderPaths):
        self.data_mesh_activity.to_csv(folder_paths.csv_results, self.name)
        print(f"{self.name} processed!")

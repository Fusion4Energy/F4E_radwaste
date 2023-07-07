from f4e_radwaste.post_processing.folder_paths import FolderPaths
from f4e_radwaste.post_processing.input_data import InputData


def process_input_data_by_material(input_data: InputData, folder_paths: FolderPaths):
    decay_times = input_data.data_absolute_activity.decay_times
    materials = input_data.data_mesh_info.data_mass.materials

    for decay_time in decay_times:
        for material in materials:
            output_data = input_data.get_mesh_output_by_time_and_materials(
                decay_time=decay_time, materials=[material]
            )

            if output_data is None:
                continue

            output_data.save(folder_paths)

        output_data = input_data.get_mesh_output_by_time_and_materials(decay_time)
        output_data.save(folder_paths)
import re
from typing import TextIO, List, Tuple

import numpy as np
import pandas as pd

from f4e_radwaste.constants import (
    CoordinateType,
    KEY_VOXEL,
    KEY_MASS_GRAMS,
    KEY_MATERIAL,
    KEY_CELL,
)
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo


def read_file(file_path) -> DataMeshInfo:
    with open(file_path, "r", encoding="utf-8") as infile:
        for line in infile:
            if "Mesh tally number:" in line:
                data_mesh_info = _read_individual_mesh(infile)

                # Only the first DataMeshInfo is returned
                return data_mesh_info

    raise ValueError("No mesh found in the file...")


def _read_individual_mesh(infile: TextIO):
    # Skip 3 lines without relevant info
    [next(infile) for _ in range(3)]

    # Read the header
    line = infile.readline()
    if line.split()[0] == "origin":
        # The mesh is cylindrical
        data_mesh_info = _read_header_cyl(line, infile)
    else:
        data_mesh_info = _read_header_cart(line, infile)

    # Read the voxel data and assign it to the object
    data_mesh_info.data_mass = _read_voxels(data_mesh_info, infile)
    return data_mesh_info


def _read_header_cyl(line: str, infile: TextIO):
    # One line for origin, axis and vec
    words = line.split()
    origin = [float(x) for x in words[2:5]]
    axis = [float(x) for x in words[7:10]]
    vec = [float(x) for x in words[13:16]]

    # One line for each vector
    vector_i = _read_vector(infile.readline())
    vector_j = _read_vector(infile.readline())
    # This line is buggy, it says revolutions but the units are in
    # radians, the two numbers may be merged ex: 0.000000006.28318531
    line = infile.readline()
    vector_k = re.findall(r"\d\.\d{8}", line)
    vector_k = [float(x) / (2 * np.pi) for x in vector_k]

    mesh_info = DataMeshInfo(
        coordinates=CoordinateType.CYLINDRICAL,
        vector_i=np.array(vector_i),
        vector_j=np.array(vector_j),
        vector_k=np.array(vector_k),
        data_mass=None,
        origin=np.array(origin),
        axis=np.array(axis),
        vec=np.array(vec),
    )
    return mesh_info


def _read_header_cart(line: str, infile: TextIO) -> DataMeshInfo:
    # One line for each vector
    vector_i = _read_vector(line)
    vector_j = _read_vector(infile.readline())
    vector_k = _read_vector(infile.readline())

    mesh_info = DataMeshInfo(
        coordinates=CoordinateType.CARTESIAN,
        vector_i=np.array(vector_i),
        vector_j=np.array(vector_j),
        vector_k=np.array(vector_k),
        data_mass=None,
    )
    return mesh_info


def _read_vector(line: str) -> List[float]:
    return [float(x) for x in line.split()[2:]]


def _read_voxels(data_mesh_info: DataMeshInfo, infile: TextIO) -> DataMass:
    data = {
        KEY_VOXEL: [],
        KEY_CELL: [],
        KEY_MATERIAL: [],
        KEY_MASS_GRAMS: [],
    }

    number_of_voxels = (
        (len(data_mesh_info.vector_i) - 1)
        * (len(data_mesh_info.vector_j) - 1)
        * (len(data_mesh_info.vector_k) - 1)
    )

    for _ in range(number_of_voxels):
        voxel_id, volume, number_of_cells_inside = infile.readline().split()
        voxel_id, number_of_cells_inside = int(voxel_id), int(number_of_cells_inside)
        volume = float(volume)

        for _ in range(number_of_cells_inside):
            cell_id, material_id, cell_mass = _read_cell_part(volume, infile)

            data[KEY_VOXEL].append(voxel_id)
            data[KEY_CELL].append(cell_id)
            data[KEY_MATERIAL].append(material_id)
            data[KEY_MASS_GRAMS].append(cell_mass)

    if data_mesh_info.coordinates == CoordinateType.CYLINDRICAL:
        # WARNING: we divide the volume by 2 pi due to a bug in the D1S
        # generation of the meshinfo file for cyl coordinates.
        # It provides a volume calculated as if the theta coordinate units
        # were revolutions, but it is actually in radians.
        data[KEY_MASS_GRAMS] = np.array(data[KEY_MASS_GRAMS]) / (2 * np.pi)

    # Convert the data dictionary to a DataFrame
    mass_dataframe = pd.DataFrame(data).set_index([KEY_VOXEL, KEY_MATERIAL, KEY_CELL])

    return DataMass(mass_dataframe)


def _read_cell_part(volume: float, infile: TextIO) -> Tuple[int, float, float]:
    cell_id, density, material_id, volume_proportion = infile.readline().split()
    cell_id, material_id = int(cell_id), int(material_id)
    density, volume_proportion = float(density), float(volume_proportion)

    cell_volume_inside_voxel = volume * volume_proportion
    cell_mass = cell_volume_inside_voxel * density

    return cell_id, material_id, cell_mass

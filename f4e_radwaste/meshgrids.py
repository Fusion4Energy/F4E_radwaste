from typing import Optional

import numpy as np
import pyvista as pv

from f4e_radwaste.constants import CoordinateType
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo


def create_grid(
    data_mesh_info: DataMeshInfo, data_mesh_activity: Optional[DataMeshActivity] = None
) -> pv.StructuredGrid:
    if data_mesh_info.coordinates is CoordinateType.CARTESIAN:
        grid = create_cartesian_grid(
            vector_i=data_mesh_info.vector_i,
            vector_j=data_mesh_info.vector_j,
            vector_k=data_mesh_info.vector_k,
        )
    else:
        grid = create_cylindrical_grid(
            vector_i=data_mesh_info.vector_i,
            vector_j=data_mesh_info.vector_j,
            vector_k_revolutions=data_mesh_info.vector_k,
            origin=data_mesh_info.origin,
            axis=data_mesh_info.axis,
        )

    if data_mesh_activity is not None:
        insert_data_to_grid(data_mesh_activity, data_mesh_info, grid)

    return grid


def insert_data_to_grid(
    data_mesh_activity: DataMeshActivity,
    data_mesh_info: DataMeshInfo,
    grid: pv.StructuredGrid,
):
    dataframe = data_mesh_activity.get_filtered_dataframe()

    # Order the dataframe so the indices of it match the grid cell indices
    ints_vector_i = len(data_mesh_info.vector_i) - 1
    ints_vector_j = len(data_mesh_info.vector_j) - 1
    ints_vector_k = len(data_mesh_info.vector_k) - 1
    len_index = ints_vector_i * ints_vector_j * ints_vector_k

    indices = np.arange(len_index).reshape(
        (ints_vector_i, ints_vector_j, ints_vector_k)
    )
    indices += 1
    indices = indices.swapaxes(0, 2)
    if data_mesh_info.coordinates == CoordinateType.CYLINDRICAL:
        # If the grid was extended in the thetas the values should be repeated
        extended = grid.n_cells // len_index
        if extended > 1:
            indices = np.repeat(indices, extended, axis=0)

        # For cylindrical the order is Z-THETA-R
        indices = indices.swapaxes(0, 1)

    indices = indices.ravel()
    dataframe = dataframe.reindex(indices, fill_value=0)

    for column_name, column in dataframe.items():
        grid[str(column_name)] = column


def create_cartesian_grid(vector_i, vector_j, vector_k) -> pv.StructuredGrid:
    # meshgrid should receive float arrays to avoid a warning
    vector_i = np.asarray(vector_i, "float32")
    vector_j = np.asarray(vector_j, "float32")
    vector_k = np.asarray(vector_k, "float32")

    x_coordinates, y_coordinates, z_coordinates = np.meshgrid(
        vector_i, vector_j, vector_k, indexing="ij"
    )
    grid = pv.StructuredGrid(x_coordinates, y_coordinates, z_coordinates)
    return grid


def create_cylindrical_grid(
    vector_i, vector_j, vector_k_revolutions, origin=None, axis=None
) -> pv.StructuredGrid:
    vector_k_revolutions = correct_theta_vector(vector_k_revolutions)

    # Extend the theta vector if less than 3 intervals
    if len(vector_k_revolutions) <= 3:
        vector_k_revolutions = extend_theta_intervals(vector_k_revolutions)

    # Create the grid on the Z axis
    grid = create_cylindrical_grid_z_axis(vector_i, vector_j, vector_k_revolutions)

    # Roto translate the cylinder
    if axis is not None:
        rotate_to_axis(grid, axis)
    if origin is not None:
        grid.translate(origin, inplace=True)

    return grid


def create_cylindrical_grid_z_axis(vector_i, vector_j, vector_k_revolutions):
    vector_k_radians = np.array(vector_k_revolutions) * 2 * np.pi

    radii, thetas, z = np.array(
        np.meshgrid(vector_i, vector_k_radians, vector_j, indexing="ij")
    )
    x = np.cos(thetas) * radii
    y = np.sin(thetas) * radii
    points = np.c_[x.ravel(order="f"), y.ravel(order="f"), z.ravel(order="f")]

    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = len(vector_i), len(vector_k_revolutions), len(vector_j)

    return grid


def rotate_to_axis(cylinder: pv.StructuredGrid, axis):
    original_axis = np.array([0.0, 0.0, 1.0])
    normal_to_rotation = np.cross(original_axis, axis)

    # Calculate the angle to rotate
    angle = angle_between(original_axis, axis)

    # Apply the rotation
    cylinder.rotate_vector(vector=normal_to_rotation, angle=angle, inplace=True)


def correct_theta_vector(vector_k_revolutions):
    # If the cylinder starts at exactly 0 revolutions
    if np.isclose(vector_k_revolutions[0], 0.0):
        vector_k_revolutions[0] = 0.0

    # If the cylinder ends at exactly 1 revolution
    if np.isclose(vector_k_revolutions[-1], 1.0):
        vector_k_revolutions[-1] = 1.0

    return vector_k_revolutions


def extend_theta_intervals(vector_k, new_theta_ints=20):
    if len(vector_k) == 2:
        extended_vector_k = np.linspace(vector_k[0], vector_k[1], new_theta_ints + 1)

    elif len(vector_k) == 3:
        new_theta_ints = new_theta_ints // 2
        vector_k_0 = np.linspace(vector_k[0], vector_k[1], new_theta_ints + 1)
        vector_k_1 = np.linspace(vector_k[1], vector_k[2], new_theta_ints + 1)[1:]
        extended_vector_k = np.concatenate((vector_k_0, vector_k_1))

    else:
        raise ValueError("Only 1 or 2 theta defined intervals can be extended...")

    return extended_vector_k


def normalize_vector(vector: np.ndarray):
    """Returns the unit vector of the vector."""
    return vector / np.linalg.norm(vector)


def angle_between(vec_1, vec_2):
    """Returns the angle in degrees between vectors 'v1' and 'v2'"""
    v1_normalized = normalize_vector(vec_1)
    v2_normalized = normalize_vector(vec_2)
    radians = np.arccos(np.clip(np.dot(v1_normalized, v2_normalized), -1.0, 1.0))
    return np.rad2deg(radians)


# def _add_cell_center_labels_to_plotter(plotter: pv.Plotter, grid: pv.StructuredGrid):
#     # Add text annotations for each cell
#     centers = grid.cell_centers()
#     centers["Labels"] = np.arange(grid.n_cells)
#     plotter.add_point_labels(centers, "Labels", point_size=20, font_size=36)

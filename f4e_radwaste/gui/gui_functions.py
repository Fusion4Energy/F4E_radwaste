# pylint: disable=E1101
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.post_processing.classify_waste import classify_waste


if TYPE_CHECKING:
    from f4e_radwaste.gui.gui_manager import GUIManager

import pyvista as pv

from f4e_radwaste.gui.gui_helpers import (
    KEY_ALL_MATERIALS,
    KEY_CUSTOM_MATERIAL,
    DATA_MESH_PLOTTER_NAME,
    COLOR_MAP,
    SCALAR_BAR_ARGS,
    NUMBER_OF_COLORS,
    OVERLAID_BOX_MESH_PLOTTER_NAME,
    KEY_R2S_INDICES,
    select_stl_through_dialog,
    select_folder_through_dialog,
)

from f4e_radwaste.meshgrids import create_grid


class GUIFunctions:
    def __init__(self, manager):
        self.manager: GUIManager = manager
        # to stop the execution of some functions, when updating several ComboBox at
        # the same time we want to recalculate only once
        self.active = False

    def menu_action_load_data_tables_folder(self):
        folder_path = select_folder_through_dialog()

        self.manager.load_new_data_processor(folder_path)

        self.load_geometry_meshes(folder_path)

        self.update_results_widget_with_new_dataset()
        self.start_plot()

    def load_geometry_meshes(self, folder_path):
        geo_path = folder_path / "geometry"
        if not geo_path.is_dir():
            return
        for file in geo_path.iterdir():
            if not file.is_file():
                continue
            if file.suffix not in [".stl", ".ply"]:
                continue
            self.manager.geo_meshes[file.stem] = pv.read(file)

    def update_results_widget_with_new_dataset(self):
        # Stop the automatic execution of functions until the end of this function
        self.active = False

        # Update the time and material ComboBox
        results_widget = self.manager.main_window.results_widget
        input_data = self.manager.processor.input_data

        decay_times = input_data.data_absolute_activity.decay_times
        results_widget.update_time_combo_box(decay_times)

        material_ids = input_data.data_mesh_info.data_mass.materials
        material_ids = list(material_ids)
        material_ids.sort()
        material_ids.append(KEY_ALL_MATERIALS)
        material_ids.append(KEY_CUSTOM_MATERIAL)
        results_widget.update_material_combo_box(material_ids)

        # select and create the grid for a combination of time and material, necessary
        # to get the array names
        self.update_grid_with_time_material_combination()

        self.active = True

    def update_grid_with_time_material_combination(self):
        self.active = False

        # Get the time and material from the combo boxes
        results_widget = self.manager.main_window.results_widget
        decay_time = results_widget.get_decay_time()
        materials = results_widget.get_materials()

        # Calculate the DataMeshActivity for the time and material
        input_data = self.manager.processor.input_data
        try:
            mesh_activity = input_data.get_mesh_activity_by_time_and_materials(
                decay_time=decay_time,
                materials=materials,
            )
        except ValueError:
            # Create a dummy empty grid if no data for the mesh
            self.manager.grid = pv.StructuredGrid()
            self.active = True
            return

        mesh_activity = classify_waste(mesh_activity, input_data.isotope_criteria)

        dataframe = mesh_activity.get_filtered_dataframe()
        dataframe[KEY_R2S_INDICES] = dataframe.index.values
        mesh_activity = DataMeshActivity(dataframe)

        self.manager.grid = create_grid(
            data_mesh_info=input_data.data_mesh_info, data_mesh_activity=mesh_activity
        )

        # Update the array name ComboBox
        results_widget.update_array_name_combo_box(self.manager.grid.array_names)

        self.active = True

    def start_plot(self):
        self.active = False
        plotter = self.manager.main_window.plotter
        plotter.clear()
        results_widget = self.manager.main_window.results_widget
        plotting_options = results_widget.get_plotting_options_summary()
        if plotting_options.show_geometry:
            if plotting_options.sample_mesh_data_over_geometry:
                self.add_sampled_geo_mesh()
            else:
                self.add_geo_mesh()
        if plotting_options.show_overlaid_box:
            self.update_box_in_plotter()
        if plotting_options.show_data_mesh:
            self.add_data_mesh()
        self.active = True

    def replot(self):
        if not self.active:
            return
        self.start_plot()
        print("replot")

    def add_data_mesh(self):
        results_widget = self.manager.main_window.results_widget
        plotting_options = results_widget.get_plotting_options_summary()
        plotter = self.manager.main_window.plotter
        array_name = results_widget.get_array_name()
        if self.manager.grid.n_cells == 0:
            return
        # apply a threshold to the grid to show only the voxels with data
        threshold_grid = self.manager.grid.threshold(value=1e-90, scalars=array_name)
        if len(threshold_grid[array_name]) == 0:
            return
        plotter.add_mesh(
            threshold_grid,
            scalars=array_name,
            name=DATA_MESH_PLOTTER_NAME,
            log_scale=plotting_options.log_scale,
            cmap=COLOR_MAP,
            scalar_bar_args=SCALAR_BAR_ARGS,
            n_colors=NUMBER_OF_COLORS,
        )
        min_val = np.min(threshold_grid[array_name])
        max_val = np.max(threshold_grid[array_name])
        results_widget.set_color_range(min_val, max_val)
        plotter.update_scalar_bar_range(clim=[min_val, max_val])

    def add_geo_mesh(self):
        results_widget = self.manager.main_window.results_widget
        material_key = results_widget.get_material_string()
        geo_meshes = self.manager.geo_meshes
        if material_key not in geo_meshes.keys():
            return
        plotter = self.manager.main_window.plotter
        plotter.add_mesh(
            geo_meshes[material_key],
            color="grey",
            show_edges=True,
        )

    def add_sampled_geo_mesh(self):
        results_widget = self.manager.main_window.results_widget
        material_key = results_widget.get_material_string()
        geo_meshes = self.manager.geo_meshes
        if material_key not in geo_meshes.keys():
            return
        geo_meshes[material_key] = geo_meshes[material_key].sample(self.manager.grid)
        plotting_options = results_widget.get_plotting_options_summary()
        plotter = self.manager.main_window.plotter
        plotter.add_mesh(
            geo_meshes[material_key],
            scalars=results_widget.get_array_name(),
            name=DATA_MESH_PLOTTER_NAME,
            log_scale=plotting_options.log_scale,
            cmap=COLOR_MAP,
            scalar_bar_args=SCALAR_BAR_ARGS,
            n_colors=NUMBER_OF_COLORS,
        )

    def button_pressed_generate_box(self):
        self.active = False
        overlaid_box_widget = self.manager.main_window.overlaid_box_widget
        overlaid_box_widget.show_box_generated_widget()
        overlaid_box_widget.set_box_parameters_to_fit_mesh(self.manager.grid)
        overlaid_box_widget.generate_box_according_to_box_input_lines()
        self.update_box_in_plotter()
        self.active = True

    def button_pressed_load_stl_box(self):
        self.active = False
        overlaid_box_widget = self.manager.main_window.overlaid_box_widget
        stl_file_path = select_stl_through_dialog()
        overlaid_box_widget.load_stl_as_box(stl_file_path)
        overlaid_box_widget.show_custom_box_loaded_widget()
        self.update_box_in_plotter()
        self.active = True

    def button_pressed_calculate_radwaste(self) -> DataMeshActivity | None:
        grid = self.manager.grid

        if grid.n_cells == 0:
            return

        box = self.manager.main_window.overlaid_box_widget.box_grid

        if box.n_cells == 0:
            return

        # Get the time and material from the combo boxes
        results_widget = self.manager.main_window.results_widget
        decay_time = results_widget.get_decay_time()
        materials = results_widget.get_materials()

        mask_cells_inside = self.get_mask_vtk_cells_inside_box(box, grid)

        voxels_inside = grid[KEY_R2S_INDICES][mask_cells_inside]

        input_data = self.manager.processor.input_data
        package_activity = input_data.get_collapsed_activity(
            decay_time=decay_time, materials=materials, voxels=voxels_inside
        )
        pacakge_activity = classify_waste(package_activity, input_data.isotope_criteria)

        self.manager.main_window.results_widget.update_radwaste_display(
            pacakge_activity, input_data.isotope_criteria
        )

        return pacakge_activity

    @staticmethod
    def get_mask_vtk_cells_inside_box(box, value_grid):
        centers = value_grid.cell_centers()
        mask_points_inside = centers.select_enclosed_points(box)["SelectedPoints"]
        return mask_points_inside.astype(bool)

    def button_pressed_print_radwaste_info(self):
        """
        clicking print radwaste info button will start as if first we clicked calculate
         radwaste button, and then it will write the info to a file
        """
        pass
        # package_activity = self.button_pressed_calculate_radwaste()
        # package_activity.to_csv(path=PROJECT_PATHS.path_to_data_tables, name="PACKAGE")

    def button_pressed_delete_box(self):
        self.active = False
        overlaid_box_widget = self.manager.main_window.overlaid_box_widget
        overlaid_box_widget.show_no_box_loaded_widget()
        overlaid_box_widget.box_grid = pv.StructuredGrid()
        self.manager.main_window.plotter.remove_actor(OVERLAID_BOX_MESH_PLOTTER_NAME)
        self.active = True

    def button_pressed_custom_material_mixer(self):
        self.manager.main_window.results_widget.custom_material_mixer.show()

    def button_pressed_display_options(self):
        self.manager.main_window.results_widget.show_hide_display_options()

    def box_parameters_changed(self):
        if not self.active:
            return
        overlaid_box_widget = self.manager.main_window.overlaid_box_widget
        overlaid_box_widget.generate_box_according_to_box_input_lines()
        self.update_box_in_plotter()

    def update_box_in_plotter(self):
        results_widget = self.manager.main_window.results_widget
        plotting_options = results_widget.get_plotting_options_summary()
        if not plotting_options.show_overlaid_box:
            return
        box_grid = self.manager.main_window.overlaid_box_widget.box_grid
        if box_grid.n_cells == 0:
            return
        self.manager.main_window.plotter.add_mesh(
            box_grid,
            name=OVERLAID_BOX_MESH_PLOTTER_NAME,
            opacity=0.5,
            show_edges=True,
            line_width=3,
        )

    def decay_time_changed(self):
        if not self.active:
            return
        self.update_grid_with_time_material_combination()
        self.start_plot()
        print("decay time changed")

    def material_changed(self):
        if not self.active:
            return
        self.update_grid_with_time_material_combination()
        self.start_plot()
        print("material changed")

    def array_name_changed(self):
        if not self.active:
            return
        self.start_plot()

    def scalar_range_changed(self):
        if not self.active:
            return
        plotter = self.manager.main_window.plotter
        results_widget = self.manager.main_window.results_widget
        plotting_options = results_widget.get_plotting_options_summary()
        # we modify the actor directly instead of using plotter.update_scalar_bar_range
        # because the "name" parameter does not work, if we add another mesh to the
        # plotter like the overlaid box, the plotter can't find the scalar bar that way
        if DATA_MESH_PLOTTER_NAME in plotter.actors:
            clim = [plotting_options.min_scalar_val, plotting_options.max_scalar_val]
            plotter.actors[DATA_MESH_PLOTTER_NAME].mapper.scalar_range = clim

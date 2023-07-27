# pylint: disable=E1101
import dataclasses

from qtpy import QtWidgets, QtCore

from f4e_radwaste.constants import KEY_TOTAL_SPECIFIC_ACTIVITY, TYPE_B_STR
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity

from f4e_radwaste.gui.gui_helpers import (
    add_combo_box,
    add_check_push_button,
    add_check_box,
    KEY_ALL_MATERIALS,
    KEY_CUSTOM_MATERIAL,
    add_input_float_scientific_spinner,
)
from f4e_radwaste.gui.widgets.custom_material_mixer_widget import (
    CustomMaterialMixer,
)
from f4e_radwaste.post_processing.collapsed_data import CollapsedData


class MeshSelection:
    def __init__(self, layout, manager):
        self.time_combo_box = add_combo_box(
            layout=layout,
            message="Time",
            function=manager.functions.decay_time_changed,
        )
        self.material_combo_box = add_combo_box(
            layout=layout,
            message="Material",
            function=manager.functions.material_changed,
        )
        self.array_name_combo_box = add_combo_box(
            layout=layout,
            message="Data Array",
            function=manager.functions.array_name_changed,
        )
        add_check_push_button(
            layout=layout,
            message="Custom material mixer",
            function=manager.functions.button_pressed_custom_material_mixer,
        )


@dataclasses.dataclass
class PlottingOptionsSummary:
    show_data_mesh: bool
    show_overlaid_box: bool
    show_geometry: bool
    sample_mesh_data_over_geometry: bool
    log_scale: bool
    min_scalar_val: float
    max_scalar_val: bool


class PlottingOptions:
    def __init__(self, layout, manager):
        add_check_push_button(
            layout=layout,
            message="Show display options",
            function=manager.functions.button_pressed_display_options,
        )
        self.check_show_mesh = add_check_box(
            layout=layout,
            message="Show data mesh",
            function=manager.functions.replot,
        )
        self.check_show_overlaid_box = add_check_box(
            layout=layout,
            message="Show overlaid box",
            function=manager.functions.replot,
        )
        self.check_show_geom = add_check_box(
            layout=layout,
            message="Show geometry",
            function=manager.functions.replot,
        )
        self.check_sample_data_over_geo = add_check_box(
            layout=layout,
            message="Sample mesh data over geometry",
            function=manager.functions.replot,
        )
        self.check_log_scale = add_check_box(
            layout=layout,
            message="Log scale",
            function=manager.functions.replot,
        )
        self.min_scalar_val = add_input_float_scientific_spinner(
            layout=layout,
            message="Range min value",
            function=manager.functions.scalar_range_changed,
        )
        self.max_scalar_val = add_input_float_scientific_spinner(
            layout=layout,
            message="Range max value",
            function=manager.functions.scalar_range_changed,
        )
        # initial plotting configuration
        self.check_show_mesh.setChecked(True)
        self.check_show_overlaid_box.setChecked(True)
        self.check_log_scale.setChecked(True)


class RadwasteDisplay(QtWidgets.QWidget):
    def __init__(self, layout):
        super().__init__(parent=None)
        self.radwaste_type = QtWidgets.QLabel("")
        self.mass = QtWidgets.QLabel("")
        self.iras = QtWidgets.QLabel("")
        self.lma_isotopes = QtWidgets.QListWidget(parent=None)
        self.lma_isotopes.setMaximumHeight(100)
        self.relevant_activity = QtWidgets.QLabel("")
        self.total_activity = QtWidgets.QLabel("")
        self.dose_1_m = QtWidgets.QLabel("")
        self.contact_dose_rate = QtWidgets.QLabel("")
        self._build_widget(layout)

    # noinspection PyArgumentList
    def _build_widget(self, layout):
        scrollable_area = QtWidgets.QWidget(parent=None)
        scrollable_layout = QtWidgets.QVBoxLayout()
        scrollable_layout.addWidget(QtWidgets.QLabel("Radwaste classification:"))
        scrollable_layout.addWidget(self.radwaste_type)
        scrollable_layout.addWidget(QtWidgets.QLabel("Mass [kg]:"))
        scrollable_layout.addWidget(self.mass)
        scrollable_layout.addWidget(QtWidgets.QLabel("IRAS:"))
        scrollable_layout.addWidget(self.iras)
        scrollable_layout.addWidget(QtWidgets.QLabel("LMA exceeded isotopes:"))
        scrollable_layout.addWidget(self.lma_isotopes)
        scrollable_layout.addWidget(QtWidgets.QLabel("Relevant activity [Bq/g]:"))
        scrollable_layout.addWidget(self.relevant_activity)
        scrollable_layout.addWidget(QtWidgets.QLabel("Total activity [Bq/g]:"))
        scrollable_layout.addWidget(self.total_activity)
        scrollable_layout.addWidget(QtWidgets.QLabel("Dose at 1 meter [Sv/h/g]:"))
        scrollable_layout.addWidget(self.dose_1_m)
        scrollable_layout.addWidget(QtWidgets.QLabel("Contact dose rate [Sv/h]:"))
        scrollable_layout.addWidget(self.contact_dose_rate)

        spacer = QtWidgets.QSpacerItem(
            1,
            1,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        scrollable_layout.addItem(spacer)
        scrollable_area.setLayout(scrollable_layout)
        general_layout = QtWidgets.QVBoxLayout()
        scroll = QtWidgets.QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrollable_area)
        general_layout.addWidget(scroll)

        self.setLayout(general_layout)
        layout.addRow(self)


class ResultsWidget(QtWidgets.QWidget):
    def __init__(self, parent, manager):
        super().__init__(parent=parent)
        # QForm layout
        layout = QtWidgets.QFormLayout(parent=None)
        self.setMaximumWidth(210)
        self.setLayout(layout)
        self.mesh_selection = MeshSelection(layout, manager)
        self.plotting_options = PlottingOptions(layout, manager)
        self.radwaste_display = RadwasteDisplay(layout)
        self.custom_material_mixer = CustomMaterialMixer([])

    def get_decay_time(self):
        return self.mesh_selection.time_combo_box.currentText()

    def get_materials(self) -> list[int]:
        material_str = self.mesh_selection.material_combo_box.currentText()
        # all the material keys are convertible to int except KEY_ALL_MATERIALS and
        # KEY_CUSTOM_MATERIAL which will remain a str
        if material_str == KEY_ALL_MATERIALS:
            material_key = None  # this will select all the materials
        elif material_str == KEY_CUSTOM_MATERIAL:
            # return list of materials
            material_key = self.custom_material_mixer.get_custom_material_list()
        else:
            material_key = [int(material_str)]
        return material_key

    def get_material_string(self) -> str:
        material_str = self.mesh_selection.material_combo_box.currentText()
        return material_str

    def get_array_name(self):
        return self.mesh_selection.array_name_combo_box.currentText()

    def get_plotting_options_summary(self) -> PlottingOptionsSummary:
        options = self.plotting_options
        sample_mesh = options.check_sample_data_over_geo.checkState()
        # we have to perform the > 0 check because the checkbox returns a 0 if False
        # and a positive answer if True
        summary = PlottingOptionsSummary(
            show_data_mesh=options.check_show_mesh.checkState() > 0,
            show_overlaid_box=options.check_show_overlaid_box.checkState() > 0,
            show_geometry=options.check_show_geom.checkState() > 0,
            sample_mesh_data_over_geometry=sample_mesh > 0,
            log_scale=options.check_log_scale.checkState() > 0,
            min_scalar_val=options.min_scalar_val.value(),
            max_scalar_val=options.max_scalar_val.value(),
        )
        return summary

    def set_color_range(self, min_val, max_val):
        self.plotting_options.min_scalar_val.setValue(min_val)
        self.plotting_options.max_scalar_val.setValue(max_val)

    def update_time_combo_box(self, time_keys):
        time_keys = [str(value) for value in time_keys]
        self.mesh_selection.time_combo_box.clear()
        self.mesh_selection.time_combo_box.addItems(time_keys)

    def update_material_combo_box(self, material_keys):
        material_keys = [str(value) for value in material_keys]
        self.mesh_selection.material_combo_box.clear()
        self.mesh_selection.material_combo_box.addItems(material_keys)
        # don't start with the first material id which could be material 0 (void)
        self.mesh_selection.material_combo_box.setCurrentIndex(len(material_keys) - 2)
        # update the custom material mixer with the new materials, don't take the last
        # two materials as they correspond to KEY_ALL_MATERIALS and KEY_CUSTOM_MATERIAL
        self.custom_material_mixer.update_list_of_materials(material_keys[:-2])

    def update_array_name_combo_box(self, array_name_keys):
        # try to keep the previous data array if it exists
        previous_array_name = self.get_array_name()
        self.mesh_selection.array_name_combo_box.clear()
        self.mesh_selection.array_name_combo_box.addItems(array_name_keys)
        # start with an interesting data array
        if previous_array_name in array_name_keys:
            start_index = array_name_keys.index(previous_array_name)
        else:
            start_index = array_name_keys.index(KEY_TOTAL_SPECIFIC_ACTIVITY)
        self.mesh_selection.array_name_combo_box.setCurrentIndex(start_index)

    def show_hide_display_options(self):
        checked = not self.plotting_options.check_show_mesh.isVisible()
        self.plotting_options.check_show_mesh.setVisible(checked)
        self.plotting_options.check_show_overlaid_box.setVisible(checked)
        self.plotting_options.check_show_geom.setVisible(checked)
        self.plotting_options.check_sample_data_over_geo.setVisible(checked)
        self.plotting_options.check_log_scale.setVisible(checked)

    def update_radwaste_display(
        self, package_activity: DataMeshActivity, isotope_criteria: DataIsotopeCriteria
    ):
        collapsed_data = CollapsedData(package_activity)

        radwaste_class = collapsed_data.get_radwaste_class_str()
        self.radwaste_display.radwaste_type.setText(f"{radwaste_class}")

        mass_grams = collapsed_data.get_mass()
        self.radwaste_display.mass.setText(f"{mass_grams / 1000:.2f}")

        iras = collapsed_data.get_iras()
        self.radwaste_display.iras.setText(f"{iras:.2f}")

        self.radwaste_display.lma_isotopes.clear()
        if radwaste_class == TYPE_B_STR:
            lma_exceeded_isotopes = collapsed_data.get_isotopes_exceeding_lma(
                isotope_criteria
            )
            self.radwaste_display.lma_isotopes.addItems(lma_exceeded_isotopes)

        relevant_activity = collapsed_data.get_relevant_activity()
        self.radwaste_display.relevant_activity.setText(f"{relevant_activity:.2e}")

        total_activity = collapsed_data.get_total_activity()
        self.radwaste_display.total_activity.setText(f"{total_activity:.2e}")

        dose_1_m = collapsed_data.get_dose_1_m()
        self.radwaste_display.dose_1_m.setText(f"{dose_1_m:.2e}")

        contact_dose_rate = collapsed_data.get_contact_dose_rate()
        self.radwaste_display.contact_dose_rate.setText(f"{contact_dose_rate:.2e}")

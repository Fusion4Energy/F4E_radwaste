# pylint: disable=E1101
from pathlib import Path

from qtpy import QtWidgets, QtCore

from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.gui.widgets.scientific_float_spinner_widget import (
    QScientificFloatSpinner,
)

KEY_R2S_INDICES = "Voxel Indices"
KEY_ALL_MATERIALS = "all materials"
KEY_CUSTOM_MATERIAL = "custom material"
DATA_MESH_PLOTTER_NAME = "data_mesh"
OVERLAID_BOX_MESH_PLOTTER_NAME = "overlaid_box"
GEOMETRY_MESH_PLOTTER_NAME = "geometry_mesh"
COLOR_MAP = "jet"
NUMBER_OF_COLORS = 10
SCALAR_BAR_ARGS = dict(
    interactive=True,  # Log bar for plots
    title_font_size=18,
    label_font_size=18,
    shadow=True,
    n_labels=NUMBER_OF_COLORS + 1,  # Because n_colors of the plot is 10
    # to solve a weird bug where the scalar bar shows some colors repeated
    n_colors=100,
    italic=True,
    fmt="%.e",
    font_family="arial",
)


def add_push_button(message, layout, function):
    button = QtWidgets.QPushButton(message)
    # noinspection PyUnresolvedReferences
    button.pressed.connect(function)
    if isinstance(layout, QtWidgets.QFormLayout):
        layout.addRow(button)
    else:
        layout.addWidget(button)


def add_centered_text(layout, message):
    label = QtWidgets.QLabel(message)
    # noinspection PyUnresolvedReferences
    label.setAlignment(QtCore.Qt.AlignCenter)
    if isinstance(layout, QtWidgets.QFormLayout):
        layout.addRow(label)
    else:
        layout.addWidget(label)


def add_input_float_spinner(layout, message, function=None):
    widget = QtWidgets.QDoubleSpinBox(parent=None)
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
    )
    widget.setSizePolicy(size_policy)
    if function is not None:
        # noinspection PyUnresolvedReferences
        widget.valueChanged.connect(function)
    widget.setValue(0)
    widget.setRange(-100_000, 100_000)
    layout.addRow(message, widget)
    return widget


def add_input_float_scientific_spinner(layout, message, function=None):
    widget = QScientificFloatSpinner()
    size_policy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
    )
    widget.setSizePolicy(size_policy)
    if function is not None:
        # noinspection PyUnresolvedReferences
        widget.editingFinished.connect(function)
        # widget.valueChanged.connect(function)
    widget.setValue(1.0)
    widget.setFixedWidth(80)
    layout.addRow(message, widget)
    return widget


def add_combo_box(layout, message, function):
    widget = QtWidgets.QComboBox(parent=None)
    # noinspection PyUnresolvedReferences
    widget.currentIndexChanged.connect(function)
    # layout.addRow(message, widget)
    add_centered_text(layout, message)
    layout.addRow(widget)
    return widget


def add_check_push_button(layout, message, function):
    widget = QtWidgets.QPushButton(message)
    widget.setCheckable(True)
    widget.setChecked(False)
    # noinspection PyUnresolvedReferences
    widget.pressed.connect(function)
    layout.addRow(widget)
    return widget


def add_check_box(layout, message, function):
    widget = QtWidgets.QCheckBox(message)
    widget.setChecked(False)
    # noinspection PyUnresolvedReferences
    widget.stateChanged.connect(function)
    layout.addRow(widget)
    return widget


def add_voxel_indices_as_column(mesh_activity: DataMeshActivity):
    dataframe = mesh_activity.get_filtered_dataframe()
    dataframe[KEY_R2S_INDICES] = dataframe.index.values
    return dataframe


def select_folder_through_dialog() -> Path:
    dialog = QtWidgets.QFileDialog(None)
    path = dialog.getExistingDirectory(
        parent=None,
        caption="Select the data_tables folder",
        directory="",
    )
    path = Path(path)
    return path


def select_stl_through_dialog():
    dialog = QtWidgets.QFileDialog(None)
    path, _filter = dialog.getOpenFileName(
        parent=None, caption="Select the STL file", directory="", filter="*.stl"
    )
    path = Path(path)
    return path

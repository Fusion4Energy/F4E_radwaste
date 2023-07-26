# pylint: disable=E1101
from qtpy import QtWidgets

from f4e_radwaste.gui.gui_helpers import (
    add_centered_text,
    add_input_float_spinner,
    add_push_button,
)


class BoxGeneratedWidget(QtWidgets.QWidget):
    def __init__(self, manager):
        super().__init__(parent=None)
        # QForm layout
        layout = QtWidgets.QFormLayout(parent=None)
        self.setLayout(layout)
        add_centered_text(self.layout(), "Origin")
        function_box_changed = manager.functions.box_parameters_changed
        self.origin_x = add_input_float_spinner(layout, "x:", function_box_changed)
        self.origin_y = add_input_float_spinner(layout, "y:", function_box_changed)
        self.origin_z = add_input_float_spinner(layout, "z:", function_box_changed)
        add_centered_text(layout, "Size")
        self.size_x = add_input_float_spinner(layout, "x:", function_box_changed)
        self.size_y = add_input_float_spinner(layout, "y:", function_box_changed)
        self.size_z = add_input_float_spinner(layout, "z:", function_box_changed)
        self.size_x.setValue(1)
        self.size_y.setValue(1)
        self.size_z.setValue(1)
        add_centered_text(layout, "Rotation")
        self.rot_x = add_input_float_spinner(layout, "x:", function_box_changed)
        self.rot_y = add_input_float_spinner(layout, "y:", function_box_changed)
        self.rot_z = add_input_float_spinner(layout, "z:", function_box_changed)
        add_centered_text(self.layout(), "")
        generate_radwaste_package_buttons(layout=layout, manager=manager)
        self.setVisible(False)


def generate_radwaste_package_buttons(layout, manager):
    add_push_button(
        message="Calculate radwaste",
        layout=layout,
        function=manager.functions.button_pressed_calculate_radwaste,
    )
    add_push_button(
        message="Print radwaste info",
        layout=layout,
        function=manager.functions.button_pressed_print_radwaste_info,
    )
    add_push_button("Delete Box", layout, manager.functions.button_pressed_delete_box)

# pylint: disable=E1101
from qtpy import QtWidgets

from f4e_radwaste.gui.gui_helpers import add_push_button

MESSAGE_GENERATE_BOX_BUTTON = "Define package"
MESSAGE_LOAD_STL_BOX = "Load custom STL "


def no_box_loaded_widget(manager):
    widget = QtWidgets.QWidget(parent=None)
    # Vertical layout
    widget.setLayout(QtWidgets.QVBoxLayout())
    add_push_button(
        message=MESSAGE_GENERATE_BOX_BUTTON,
        layout=widget.layout(),
        function=manager.functions.button_pressed_generate_box,
    )
    add_push_button(
        message=MESSAGE_LOAD_STL_BOX,
        layout=widget.layout(),
        function=manager.functions.button_pressed_load_stl_box,
    )
    # noinspection PyUnresolvedReferences
    widget.layout().addStretch()  # so the buttons are stacked at the top
    widget.setVisible(False)
    return widget

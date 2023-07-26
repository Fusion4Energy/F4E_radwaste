# pylint: disable=E1101
from qtpy import QtWidgets

from f4e_radwaste.gui.widgets.box_generated_widget import (
    generate_radwaste_package_buttons,
)


class CustomBoxLoadedWidget(QtWidgets.QWidget):
    def __init__(self, manager):
        super().__init__(parent=None)
        # QForm layout
        layout = QtWidgets.QFormLayout(parent=None)
        self.setLayout(layout)
        generate_radwaste_package_buttons(layout=layout, manager=manager)
        self.setVisible(False)

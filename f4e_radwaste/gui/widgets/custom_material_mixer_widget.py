# Thanks to the writer of the tutorial this file is based on: John Lim
# Link to tutorial: https://www.pythonguis.com/tutorials/pyqt6-widget-search-bar/

from qtpy import QtWidgets, QtCore


class CustomMaterialMixer(QtWidgets.QWidget):
    def __init__(self, material_names):
        super().__init__(None)
        self.material_names = material_names
        # material list
        self.check_material_instances = []
        self.widget_materials = QtWidgets.QWidget()
        layout_materials = QtWidgets.QVBoxLayout()
        for material_name in self.material_names:
            widget = CheckMaterial(material_name)
            layout_materials.addWidget(widget)
            self.check_material_instances.append(widget)
        spacer = QtWidgets.QSpacerItem(
            1,
            1,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        layout_materials.addItem(spacer)
        self.widget_materials.setLayout(layout_materials)
        # Scroll Area Properties.
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget_materials)
        # Search bar
        self.searchbar = QtWidgets.QLineEdit()
        # noinspection PyUnresolvedReferences
        self.searchbar.textChanged.connect(self.searchbar_text_changed)
        # Adding Completer.
        self.completer = QtWidgets.QCompleter(self.material_names)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.searchbar.setCompleter(self.completer)
        # Show only On materials
        self.show_only_on = QtWidgets.QCheckBox("Show only On materials")
        # noinspection PyUnresolvedReferences
        self.show_only_on.stateChanged.connect(self.show_only_on_pressed)
        # Set the general layout
        layout_general = QtWidgets.QVBoxLayout()
        layout_general.addWidget(self.searchbar)
        layout_general.addWidget(self.show_only_on)
        layout_general.addWidget(self.scroll)
        self.setLayout(layout_general)
        self.setWindowTitle("Custom material mixer")
        return

    def searchbar_text_changed(self, text):
        self.update_display(text=text)

    def show_only_on_pressed(self, checked):
        self.update_display(show_only_on=checked)

    def update_display(self, text=None, show_only_on=None):
        if text is None:
            text = self.searchbar.text()
        if show_only_on is None:
            show_only_on = self.show_only_on.isChecked()
        for check_material in self.check_material_instances:
            check_material.hide()
            if text.lower() in check_material.name.lower():
                if show_only_on:
                    if check_material.is_on:
                        check_material.show()
                    else:
                        check_material.hide()
                else:
                    check_material.show()
        return

    def update_list_of_materials(self, new_material_names):
        # update completer
        self.completer.model().setStringList(new_material_names)
        # update CheckMaterials
        self.material_names = new_material_names
        self.check_material_instances = []
        layout = QtWidgets.QVBoxLayout()
        for material_name in self.material_names:
            widget = CheckMaterial(material_name)
            layout.addWidget(widget)
            self.check_material_instances.append(widget)
        spacer = QtWidgets.QSpacerItem(
            1,
            1,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        layout.addItem(spacer)
        self.widget_materials = QtWidgets.QWidget()
        self.widget_materials.setLayout(layout)
        self.scroll.setWidget(self.widget_materials)
        return

    def get_custom_material_list(self) -> list[int]:
        custom_material_list = []
        for check_material in self.check_material_instances:
            if check_material.is_on:
                custom_material_list.append(check_material.name)
        custom_material_list = [int(mat_str) for mat_str in custom_material_list]
        return custom_material_list


class CheckMaterial(QtWidgets.QWidget):
    def __init__(self, material_name):
        super().__init__(None)
        self.name = material_name
        self.is_on = False
        self.label = QtWidgets.QLabel(material_name)
        self.button_on = QtWidgets.QPushButton("On")
        # noinspection PyUnresolvedReferences
        self.button_on.clicked.connect(self.on)
        self.button_off = QtWidgets.QPushButton("Off")
        # noinspection PyUnresolvedReferences
        self.button_off.clicked.connect(self.off)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button_on)
        layout.addWidget(self.button_off)
        self.setLayout(layout)
        self.update_button_state()
        return

    def off(self):
        self.is_on = False
        self.update_button_state()

    def on(self):
        self.is_on = True
        self.update_button_state()

    def update_button_state(self):
        """
        Update the appearance of the control buttons (On/Off)
        depending on the current state.
        """
        if self.is_on:
            self.button_on.setStyleSheet("background-color: #4CAF50; color: #fff;")
            self.button_off.setStyleSheet("background-color: none; color: none;")
        else:
            self.button_on.setStyleSheet("background-color: none; color: none;")
            self.button_off.setStyleSheet("background-color: #D32F2F; color: #fff;")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    _widget = CustomMaterialMixer([])
    _widget.update_list_of_materials(["No", "brother", "sister"])
    _widget.show()
    sys.exit(app.exec_())

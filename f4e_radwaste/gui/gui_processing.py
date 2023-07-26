from f4e_radwaste.gui.gui_helpers import select_folder_through_dialog
from f4e_radwaste.main import standard_process, by_component_process, filtered_process


def gui_standard_process():
    folder_path = select_folder_through_dialog()
    standard_process(folder_path)


def gui_filtered_process():
    folder_path = select_folder_through_dialog()
    filtered_process(folder_path)


def gui_by_component_process():
    folder_path = select_folder_through_dialog()
    by_component_process(folder_path)

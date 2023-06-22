from f4e_radwaste.post_processing import (
    group_data_by_time_and_materials,
    classify_waste,
)
from f4e_radwaste.readers import dgs_file
from f4e_radwaste.readers import mesh_info_file
from f4e_radwaste.readers import isotope_criteria_file


def main():
    data_absolute_activity = dgs_file.read_file(
        r"D:\WORK\tryingSimple\tests\data\DGSdata_example_ivvs.dat"
    )
    data_mesh_info = mesh_info_file.read_file(
        r"D:\WORK\tryingSimple\tests\data\meshinfo_cart"
    )
    isotope_criteria = isotope_criteria_file.read_file(
        r"D:\WORK\tryingSimple\f4e_radwaste\resources\criteria.json"
    )

    for decay_time in data_absolute_activity.decay_times:
        for material in data_mesh_info.data_mass.materials:
            print(f"{material} for time {decay_time}")

            data_mesh_activity = group_data_by_time_and_materials(
                data_absolute_activity=data_absolute_activity,
                data_mass=data_mesh_info.data_mass,
                decay_time=decay_time,
                materials=[material],
            )

            if data_mesh_activity is None:
                print("empty")
                continue

            classify_waste(data_mesh_activity, isotope_criteria)


if __name__ == "__main__":
    main()

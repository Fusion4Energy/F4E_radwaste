from setuptools import setup, find_packages

setup(
    name="f4e_radwaste",
    version="1.0.0",
    description="Tool to analyze activation results and define radwaste packages",
    # long_description=long_description,
    # long_description_content_type='text/markdown',
    license=" EUPL, Version 1.2",
    # url='https://github.com/???',
    author="Alvaro Cubi",
    keywords="MCNP, radiation, activation, radwaste",
    packages=find_packages(),
    package_data={"": ["*.json", "*.csv"]},
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "numpy >= 1.24.2",
        "vtk >= 9.2.6",
        "pyvista >= 0.38.2",
        "pandas >= 1.5.3",
        "qtpy >= 2.3.0",
        "pyqt5",
        "pyvistaqt",
        "tables >= 3.8.0",
        "periodictable",
    ],
    extras_require={
        "test": ["unittest"],
    },
)

from pathlib import Path
from typing import Type

from f4e_radwaste.post_processing.post_processing import (
    StandardProcessor,
    ByComponentProcessor,
    FilteredProcessor,
)


def standard_process(input_path: Path) -> None:
    load_and_process_folder(input_path, StandardProcessor)


def filtered_process(input_path: Path) -> None:
    load_and_process_folder(input_path, FilteredProcessor)


def by_component_process(input_path: Path) -> None:
    load_and_process_folder(input_path, ByComponentProcessor)


def load_and_process_folder(
    input_path: Path, processor_type: Type[StandardProcessor]
) -> None:
    processor = processor_type(input_path)
    processor.process()


if __name__ == "__main__":
    standard_process(Path(r"D:\WORK\test_results"))
    # standard_process(Path(r"D:\WORK\tryingSimple\tests\old_data\ivvs_cart"))

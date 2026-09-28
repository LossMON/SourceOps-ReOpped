"""PythonVTFlib: utilities for VTF Source engine files."""

__version__ = "0.1.1"

from pathlib import Path
import os
import subprocess

from .enums import (
    IMAGE_FORMAT,
    VTF_FLAG,
    PLATFORM,
    FILE_FORMAT,
    RESIZE_FILTER,
    RESIZE_METHOD,
    COMPRESSION_METHOD,
    MODE,
    VERSION,
    VTFNormalMapOptions,
    VTFResizeOptions,
    VTFConvertOptions,
)

__all__ = [
    "__version__",
    "ops",
    "IMAGE_FORMAT",
    "VTF_FLAG",
    "PLATFORM",
    "FILE_FORMAT",
    "RESIZE_FILTER",
    "RESIZE_METHOD",
    "COMPRESSION_METHOD",
    "MODE",
    "VERSION",
    "VTFNormalMapOptions",
    "VTFResizeOptions",
    "VTFConvertOptions",
]


class ops:
    def __init__(self):

        self.platform = os.name
        self.bin_name = 'maretf'

        BASE_DIR = Path(__file__).resolve().parent
        self.bin_path = BASE_DIR / "bin"

        if self.platform == "nt":
            self.bin = self.bin_path / "win64" / f'{self.bin_name}.exe'
        elif self.platform == "posix":
            self.bin = self.bin_path / "linux64" / self.bin_name
        else:
            raise OSError(f"Unsupported platform: {self.platform}")

        if not self.bin.exists():
            raise FileNotFoundError(f"Binary not found: {self.bin}")

    def convert(self, options: VTFConvertOptions):
        cmd = str(self.bin)
        args = [cmd] + options.get_cmd()

        print(f"Running command: {' '.join(args)}")
        print(args)

        result = subprocess.run(args=args, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            print(f"Success: {result.stdout}")
        pass
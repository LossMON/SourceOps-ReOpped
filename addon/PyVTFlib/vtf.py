from pathlib import Path
import os
import subprocess

from typing import Optional, List, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from PyVTFLib.enums import (
    FORMAT,
    VTF_FLAG,
    PLATFORM,
    FILE_FORMAT,
    RESIZE_FILTER,
    RESIZE_METHOD,
    COMPRESSION_METHOD,
    VERSION
)

@dataclass
class NormalMapOptions:
    INVERT_GREEN: bool = False #Invert Green Channel needs to be set if the normalmap is in OpenGL format, ie Blender
    BUMPSCALE: float = 1 # Range 0 to 1

@dataclass
class ResizeOptions:
    WIDTH: int
    HEIGHT: int
    #Range 0 to 1
    quality: float = -1 #Default
    method: RESIZE_METHOD = None

@dataclass
class CreateVTFOptions:
    #Required
    input_path: str | Path
    output_path: str | Path
    #Optional
    format: FORMAT = None
    vtf_flags: list[VTF_FLAG] = None
    filter: RESIZE_FILTER = None
    resize: ResizeOptions = None
    normal: NormalMapOptions = None
    compression_level: float = None #Range 0 to 1, default -1 for default compression level
    compression_method: COMPRESSION_METHOD = None
    version: VERSION = None
    platform: PLATFORM = None
    disable_mips: bool = False

    def __post_init__(self):
        if isinstance(self.input_path, str):
            self.input_path = Path(self.input_path)
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)

        self.input_path = self.input_path.resolve()
        self.output_path = self.output_path.resolve() if self.output_path else None

        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_cmd(self):
        cmd = ['create']
        cmd.extend(['--input', str(self.input_path)])

        if self.output_path: cmd.extend(['--output', str(self.output_path)])
        if self.format:      cmd.extend(['--format', self.format.name])
        if self.platform:    cmd.extend(['--platform', self.platform.name])

        if self.vtf_flags:
            for flag in self.vtf_flags: cmd.extend(['--flag', flag.name])

        if self.resize:
            if self.resize.WIDTH:   cmd.extend(['--width', str(self.resize.WIDTH)])
            if self.resize.HEIGHT:  cmd.extend(['--height', str(self.resize.HEIGHT)])
            if self.resize.quality: cmd.extend(['--quality', str(self.resize.quality)])
            if self.resize.method:  cmd.extend(['--resize-method', self.resize.method.name])

        if self.normal:
            if VTF_FLAG.NORMAL not in self.vtf_flags: cmd.extend(['--flag', VTF_FLAG.NORMAL.name])
            if self.normal.INVERT_GREEN:              cmd.extend(['--invert-green'])
            if self.normal.BUMPSCALE:                 cmd.extend(['--bumpscale', str(self.normal.BUMPSCALE)])

        if self.compression_level:  cmd.extend(['--compression-level', str(self.compression_level)])
        if self.compression_method: cmd.extend(['--compression-method', self.compression_method.name])
        if self.version:            cmd.extend(['--version', self.version.value])
        if self.disable_mips:       cmd.extend(['disable_mips'])
        if self.filter:             cmd.extend(['--filter', self.filter.name])

        return cmd




@dataclass
class ExtractVTFOptions:
    #Required
    input_path: str | Path
    output_path: str | Path
    #Optional
    skip_image: bool = False
    file_format: FILE_FORMAT = FILE_FORMAT.DEFAULT    # Output file format ie PNG, WEBP etc
    image_format: FORMAT = FORMAT.DEFAULT    # The image format to convert the texture data to before extracting.
    extract_alpha_channel: bool = False
    extract_all_mips : bool = False
    extract_all_frames : bool = False
    extract_all_faces : bool = False
    extract_all_slices : bool = False
    extract_all_images : bool = False
    extract_all_resources: bool = False

    def __post_init__(self):
        if isinstance(self.input_path, str):
            self.input_path = Path(self.input_path)
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)

    def get_cmd(self):
        cmd = ['extract']
        cmd.extend(['--input', str(self.input_path)])

        if self.output_path:           cmd.extend(['--output', str(self.output_path)])
        if self.skip_image:            cmd.extend(['--extract-skip-image'])
        if self.file_format:           cmd.extend(['--extract-file-format', self.file_format])
        if self.image_format:          cmd.extend(['--extract-image-format', self.image_format])
        if self.extract_alpha_channel: cmd.extend(['--extract-alpha-channel'])
        if self.extract_all_mips:      cmd.extend(['--extract-all-mips'])
        if self.extract_all_frames:    cmd.extend(['--extract-all-frames'])
        if self.extract_all_faces:     cmd.extend(['--extract-all-faces'])
        if self.extract_all_slices:    cmd.extend(['--extract-all-slices'])
        if self.extract_all_images:    cmd.extend(['--extract-all-images'])
        if self.extract_all_resources: cmd.extend(['--extract-all-resources'])
        return cmd


    
class VTF:
    def __init__(self, bin_path: Optional[Path] = None):
        self.base_dir = Path(__file__).resolve().parent
        self.bin_path = bin_path or self.base_dir / "bin"
        self.bin_name = 'maretf'
        self.bin = self._get_binary()
    
    def _get_binary(self) -> Path:
        if os.name == "nt":
            bin_path = self.bin_path / "win64" / f'{self.bin_name}.exe'
        elif os.name == "posix":
            bin_path = self.bin_path / "linux64" / self.bin_name
        else:
            raise OSError(f"Unsupported OS: {os.name}")
        
        if not bin_path.exists():
            raise FileNotFoundError(f"Binary not found: {bin_path}")
        
        return bin_path.resolve()
    
    def _run(self, args) -> subprocess.CompletedProcess:
        cmd = [str(self.bin)] + args
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            raise Exception(result.stderr)
        else:
            print(f"Success: {result.stdout}")
        
        return result
    

vtf = VTF()
def create(options: CreateVTFOptions) -> subprocess.CompletedProcess:
    return vtf._run(args=options.get_cmd())

def extract(options: ExtractVTFOptions) -> subprocess.CompletedProcess:
    return vtf._run(args=options.get_cmd())
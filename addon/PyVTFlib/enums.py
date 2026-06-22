from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

#Enums
class IMAGE_FORMAT(Enum):
    UNCHANGED = auto()
    DEFAULT = auto()
    RGBA8888 = auto()
    ABGR8888 = auto()
    RGB888 = auto()
    BGR888 = auto()
    RGB565 = auto()
    I8 = auto()
    IA88 = auto()
    P8 = auto()
    A8 = auto()
    RGB888_BLUESCREEN = auto()
    BGR888_BLUESCREEN = auto()
    ARGB8888 = auto()
    BGRA8888 = auto()
    BGRA8888_HDR = auto()
    DXT1 = auto()
    DXT3 = auto()
    DXT5 = auto()
    BGRX8888 = auto()
    BGR565 = auto()
    BGRX5551 = auto()
    BGRA4444 = auto()
    DXT1_ONE_BIT_ALPHA = auto()
    BGRA5551 = auto()
    UV88 = auto()
    UVWQ8888 = auto()
    RGBA16161616F = auto()
    RGBA16161616 = auto()
    RGBA16161616_HDR = auto()
    UVLX8888 = auto()
    R32F = auto()
    RGB323232F = auto()
    RGBA32323232F = auto()
    RG1616F = auto()
    RG3232F = auto()
    RGBX8888 = auto()
    EMPTY = auto()
    ATI2N = auto()
    ATI1N = auto()
    RGBA1010102 = auto()
    BGRA1010102 = auto()
    R16F = auto()
    CONSOLE_BGRX8888_LINEAR = auto()
    CONSOLE_RGBA8888_LINEAR = auto()
    CONSOLE_ABGR8888_LINEAR = auto()
    CONSOLE_ARGB8888_LINEAR = auto()
    CONSOLE_BGRA8888_LINEAR = auto()
    CONSOLE_RGB888_LINEAR = auto()
    CONSOLE_BGR888_LINEAR = auto()
    CONSOLE_BGRX5551_LINEAR = auto()
    CONSOLE_I8_LINEAR = auto()
    CONSOLE_RGBA16161616_LINEAR = auto()
    CONSOLE_RGBA16161616_HDR = auto()
    CONSOLE_BGRX8888_LE = auto()
    CONSOLE_BGRA8888_LE = auto()
    TITANFALL_BC6H = auto()
    TITANFALL_BC7 = auto()
    R8 = auto()
    BC7 = auto()
    BC6H = auto()

class VTF_FLAG(Enum):
    POINT_SAMPLE = auto()
    TRILINEAR = auto()
    CLAMP_S = auto()
    CLAMP_T = auto()
    ANISOTROPIC = auto()
    NORMAL = auto() 
    NO_LOD = auto()
    LOAD_SMALL_MIPS = auto()
    PROCEDURAL = auto()
    ONE_BIT_ALPHA = auto()
    MULTI_BIT_ALPHA = auto()
    RENDERTARGET = auto()
    DEPTH_RENDERTARGET = auto()
    NO_DEBUG_OVERRIDE = auto()
    SINGLE_COPY = auto()
    NO_DEPTH_BUFFER = auto()
    CLAMP_U = auto()
    XBOX_CACHEABLE = auto()
    XBOX_UNFILTERABLE_OK = auto()
    LOAD_ALL_MIPS = auto()
    VERTEX_TEXTURE = auto()
    SSBUMP = auto()
    BORDER = auto()
    SRGB_V4 = auto()
    TF2_STAGING_MEMORY = auto()
    TF2_IMMEDIATE_CLEANUP = auto()
    TF2_IGNORE_PICMIP = auto()
    TF2_STREAMABLE_COARSE = auto()
    TF2_STREAMABLE_FINE = auto()
    PWL_CORRECTED = auto()
    SRGB_V5 = auto()
    DEFAULT_POOL = auto()
    LOAD_MOST_MIPS = auto()
    CSGO_COMBINED = auto()
    CSGO_ASYNC_DOWNLOAD = auto()
    CSGO_SKIP_INITIAL_DOWNLOAD = auto()
    CSGO_YCOCG = auto()
    CSGO_ASYNC_SKIP_INITIAL_LOW_RES = auto()
    IGNORE_PICMIP = auto()

# Idk what this does, hope it's not important
#class FLAG_EXTRA(Enum):
#    USING_PREMULTIPLIED_ALPHA_RESIZE = auto()

#class HDRI_MODE(Enum):
#    FLAT = auto()
#    CUBEMAP = auto()
#    SKYBOX = auto()

#class HOTSPOT_RECT_FLAGS(Enum):
#    RANDOM_ROTATION = auto()
#    RANDOM_REFLECTION = auto()
#    IS_ALTERNATE = auto()

class PLATFORM(Enum):
    PC = auto()
    XBOX = auto()
    X360 = auto()
    PS3_ORANGEBOX = auto()
    PS3_PORTAL2 = auto()

class FILE_FORMAT(Enum):
    DEFAULT = auto()
    PNG = auto()
    JPG = auto()
    JPEG = auto()
    BMP = auto()
    TGA = auto()
    WEBP = auto()
    QOI = auto()
    HDR = auto()
    EXR = auto()

class RESIZE_FILTER(Enum):
    DEFAULT = auto()
    BOX = auto()
    BILINEAR = auto()
    CUBIC_BSPLINE = auto()
    CATMULL_ROM = auto()
    MITCHELL = auto()
    POINT_SAMPLE = auto()
    KAISER = auto()
    NICE = auto()

#class RESIZE_EDGE(Enum):
#    CLAMP = auto()
#    REFLECT = auto()
#    WRAP = auto()
#    ZERO = auto()

class RESIZE_METHOD(Enum):
    NONE = auto()
    BIGGER = auto()
    SMALLER = auto()
    NEAREST = auto()

class COMPRESSION_METHOD(Enum):
    DEFLATE = auto()
    ZSTD = auto()
    CONSOLE_LZMA = auto()




#Flags
class MODE(Enum):
    CREATE = auto()
    EDIT = auto()
    EXTRACT = auto()
    INFO = auto()
    CONVERT = auto()  # Alias for CREATE (vtex2 compatibility)

class VERSION(Enum):
    DEFAULT = "7.4" #Default Version
    V7_2 = '7.2'
    V7_4 = "7.4" #Default Version
    V7_5 = "7.5"
    V7_6 = "7.6"


@dataclass
class VTFNormalMapOptions(Enum):
    INVERT_GREEN: bool = False #Invert Green Channel needs to be set if the normalmap is in OpenGL format, ie Blender
    BUMPSCALE : float = 1.0 # Range 0.0 to 1.0


@dataclass
class VTFResizeOptions:
    WIDTH: int = None
    HEIGHT: int = None
    #Range 0 to 1
    quality: float = -1 #Default
    method: RESIZE_METHOD = RESIZE_METHOD.NEAREST

@dataclass
class VTFConvertOptions:

    #Required
    input_path: str | Path
    output_path: str | Path
    MODE: MODE = MODE.CONVERT

    #Optional
    format: IMAGE_FORMAT = IMAGE_FORMAT.DEFAULT
    vtf_flags: list[VTF_FLAG] = None
    filter: RESIZE_FILTER = RESIZE_FILTER.DEFAULT
    resize: VTFResizeOptions = None
    normal: VTFNormalMapOptions = None
    compression_level: float = -1 #Range 0 to 1, default -1 for default compression level
    compression_method: COMPRESSION_METHOD = COMPRESSION_METHOD.ZSTD
    version: VERSION = VERSION.DEFAULT
    platform: PLATFORM = PLATFORM.PC

    disable_mips: bool = False

    def __post_init__(self):
        # Convert input_path and output_path to Path objects if they are strings
        if isinstance(self.input_path, str):
            self.input_path = Path(self.input_path)
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)

        self.input_path = self.input_path.resolve()

        # Validate that input_path exists
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        #Create output directory if it doesn't exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    

    def get_cmd(self):
        if self.MODE == MODE.CONVERT:


            cmd = [self.MODE.name.lower()] #Start with the mode as the first argument, e.g. "convert"

            cmd += ['--input', str(self.input_path)]
            cmd += ['--output', str(self.output_path)] if self.output_path is not None else []

            cmd += ['--format', self.format.name] if self.format != IMAGE_FORMAT.DEFAULT else []
            cmd += ['--platform', self.platform.name] if self.platform != PLATFORM.PC else []

            if self.vtf_flags is not None:
                for flag in self.vtf_flags:
                    cmd += ['--flag', flag.name]
            
            if self.resize is not None:
                cmd += ['--width', str(self.resize.WIDTH)]          if self.resize.WIDTH   is not None              else []
                cmd += ['--height', str(self.resize.HEIGHT)]        if self.resize.HEIGHT  is not None              else []
                cmd += ['--quality', str(self.resize.quality)]      if self.resize.quality != -1                    else []
                cmd += ['--resize-method', self.resize.method.name] if self.resize.method  != RESIZE_METHOD.NEAREST else []
            
            if self.normal is not None:
                cmd += ['--flag', VTF_FLAG.NORMAL.name] if VTF_FLAG.NORMAL not in self.vtf_flags else []
                cmd += ['--invert-green'] if self.normal.INVERT_GREEN else []
                cmd += ['--bumpscale', str(self.normal.BUMPSCALE)] if self.normal.BUMPSCALE != 1.0 else []
            
            cmd += ['--compression-level', str(self.compression_level)] if self.compression_level != -1 else []
            cmd += ['--compression-method', self.compression_method.name] if self.compression_method != COMPRESSION_METHOD.ZSTD else []
            cmd += ['--version', self.version.value] if self.version != VERSION.DEFAULT else []

            cmd += ['disable_mips'] if self.disable_mips else []
            cmd += ['--filter', self.filter.name] if self.filter != RESIZE_FILTER.DEFAULT else []



            return cmd
        else:
            raise NotImplementedError(f"Mode {self.MODE} not implemented yet")




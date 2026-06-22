import bpy

VTF_FORMATS =["RGBA8888", "ABGR8888", "RGB888", "BGR888", "RGB565", "I8", "IA88", "A8", "RGB888_BLUESCREEN", "BGR888_BLUESCREEN", "ARGB8888", "BGRA8888", "DXT1", "DXT3", "DXT5", "BGRX8888", "BGR565", "BGRX5551", "BGRA4444", "DXT1_ONEBITALPHA", "BGRA5551", "UV88", "UVWQ8888", "RGBA16161616F", "RGBA16161616", "UVLX8888"]
VTF_RESIZE_METHODS = ["NEAREST", "BIGGEST", "SMALLEST"]
VTF_RESIZE_FILTERS =["POINT", "BOX", "TRIANGLE", "QUADRATIC", "CUBIC", "CATROM", "MITCHEL", "GAUSSIAN", "SINC", "BESSEL", "HANNING", "HAMMING", "BLACKMAN", "KAISER"]
VTF_SHARPEN_FILTERS =["NONE", "NEGATIVE", "LIGHTER", "DARKER", "CONTRASTMORE", "CONTRASTLESS", "SMOOTHEN", "SHARPENSOFT", "SHARPENMEDIUM", "SHARPENSTRONG", "FINDEDGES", "CONTOUR", "EDGEDETECT", "EDGEDETECTSOFT", "EMBOSS", "MEANREMOVAL", "UNSHARP", "XSHARPEN", "WARPSHARP"]
VTF_NORMAL_KERNELS =["4X", "3X3", "5X5", "7X7", "9X9", "DUDV"]
VTF_NORMAL_HEIGHTS =["ALPHA", "AVERAGERGB", "BIASEDRGB", "RED", "GREEN", "BLUE", "MAXRGB", "COLORSPACE"]
VTF_NORMAL_ALPHAS =["NOCHANGE", "HEIGHT", "BLACK", "WHITE"]

class SOURCEOPS_MaterialProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Material Name', default='example')
    
    vtf_format: bpy.props.EnumProperty(name="Format", items=[(x, x, "") for x in VTF_FORMATS], default="DXT5")
    vtf_alphaformat: bpy.props.EnumProperty(name="Alpha Format", items=[(x, x, "") for x in VTF_FORMATS], default="DXT5")
    vtf_flag_POINTSAMPLE: bpy.props.BoolProperty(name="POINTSAMPLE")
    vtf_flag_TRILINEAR: bpy.props.BoolProperty(name="TRILINEAR")
    vtf_flag_CLAMPS: bpy.props.BoolProperty(name="CLAMPS")
    vtf_flag_CLAMPT: bpy.props.BoolProperty(name="CLAMPT")
    vtf_flag_ANISOTROPIC: bpy.props.BoolProperty(name="ANISOTROPIC")
    vtf_flag_HINT_DXT5: bpy.props.BoolProperty(name="HINT_DXT5")
    vtf_flag_NORMAL: bpy.props.BoolProperty(name="NORMAL")
    vtf_flag_NOMIP: bpy.props.BoolProperty(name="NOMIP")
    vtf_flag_NOLOD: bpy.props.BoolProperty(name="NOLOD")
    vtf_flag_MINMIP: bpy.props.BoolProperty(name="MINMIP")
    vtf_flag_PROCEDURAL: bpy.props.BoolProperty(name="PROCEDURAL")
    vtf_flag_RENDERTARGET: bpy.props.BoolProperty(name="RENDERTARGET")
    vtf_flag_DEPTHRENDERTARGET: bpy.props.BoolProperty(name="DEPTHRENDERTARGET")
    vtf_flag_NODEBUGOVERRIDE: bpy.props.BoolProperty(name="NODEBUGOVERRIDE")
    vtf_flag_SINGLECOPY: bpy.props.BoolProperty(name="SINGLECOPY")
    vtf_flag_NODEPTHBUFFER: bpy.props.BoolProperty(name="NODEPTHBUFFER")
    vtf_flag_CLAMPU: bpy.props.BoolProperty(name="CLAMPU")
    vtf_flag_VERTEXTEXTURE: bpy.props.BoolProperty(name="VERTEXTEXTURE")
    vtf_flag_SSBUMP: bpy.props.BoolProperty(name="SSBUMP")
    vtf_flag_BORDER: bpy.props.BoolProperty(name="BORDER")

    vtf_resize: bpy.props.BoolProperty(name="Enable Resizing (-resize)", default=False)
    vtf_rmethod: bpy.props.EnumProperty(name="Method", items=[(x, x, "") for x in VTF_RESIZE_METHODS], default="NEAREST")
    vtf_rfilter: bpy.props.EnumProperty(name="Filter", items=[(x, x, "") for x in VTF_RESIZE_FILTERS], default="BOX")
    vtf_rsharpen: bpy.props.EnumProperty(name="Sharpen", items=[(x, x, "") for x in VTF_SHARPEN_FILTERS], default="NONE")
    vtf_rwidth: bpy.props.IntProperty(name="Force Width", default=0, min=0)
    vtf_rheight: bpy.props.IntProperty(name="Force Height", default=0, min=0)
    vtf_rclampwidth: bpy.props.IntProperty(name="Clamp Width (Max)", default=0, min=0)
    vtf_rclampheight: bpy.props.IntProperty(name="Clamp Height (Max)", default=0, min=0)

    vtf_nomipmaps: bpy.props.BoolProperty(name="Disable Mipmaps", default=False)
    vtf_mfilter: bpy.props.EnumProperty(name="Mip Filter", items=[(x, x, "") for x in VTF_RESIZE_FILTERS], default="KAISER")
    vtf_msharpen: bpy.props.EnumProperty(name="Mip Sharpen", items=[(x, x, "") for x in VTF_SHARPEN_FILTERS], default="SHARPENSOFT")

    vtf_normal_map: bpy.props.BoolProperty(name="Generate Normal Map", default=False)
    vtf_nkernel: bpy.props.EnumProperty(name="Kernel", items=[(x, x, "") for x in VTF_NORMAL_KERNELS], default="3X3")
    vtf_nheight: bpy.props.EnumProperty(name="Height Calc", items=[(x, x, "") for x in VTF_NORMAL_HEIGHTS], default="AVERAGERGB")
    vtf_nalpha: bpy.props.EnumProperty(name="Alpha Calc", items=[(x, x, "") for x in VTF_NORMAL_ALPHAS], default="NOCHANGE")
    vtf_nscale: bpy.props.FloatProperty(name="Scale", default=2.0, min=0.0)
    vtf_nwrap: bpy.props.BoolProperty(name="Wrap (Tiled Textures)", default=False)

    vtf_gamma: bpy.props.BoolProperty(name="Gamma Correct", default=False)
    vtf_gcorrection: bpy.props.FloatProperty(name="Gamma Value", default=2.2, min=0.0)
    vtf_nothumbnail: bpy.props.BoolProperty(name="No Thumbnail", default=False)
    vtf_noreflectivity: bpy.props.BoolProperty(name="No Reflectivity Calc", default=False)
    vtf_bumpscale: bpy.props.FloatProperty(name="Bump Scale", default=1.0, min=0.0)

    vmt_shader: bpy.props.EnumProperty(name="VMT Shader",items=[("VertexLitGeneric", "VertexLitGeneric", ""),("UnlitGeneric", "UnlitGeneric", ""),("LightmappedGeneric", "LightmappedGeneric", "")], default="VertexLitGeneric")
    vmt_translucent: bpy.props.BoolProperty(name="$translucent", default=False)
    vmt_alphatest: bpy.props.BoolProperty(name="$alphatest", default=False)
    vmt_nocull: bpy.props.BoolProperty(name="$nocull", default=False)
    vmt_envmap: bpy.props.BoolProperty(name="$envmap", description="Adds env_cubemap reflection properties", default=False)
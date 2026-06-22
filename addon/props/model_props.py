import bpy
from . material_folder_props import SOURCEOPS_MaterialFolderProps
from . model_folder_props import SOURCEOPS_ModelFolderProps
from . material_props import SOURCEOPS_MaterialProps
from . skin_props import SOURCEOPS_SkinProps
from . sequence_props import SOURCEOPS_SequenceProps
from . attachment_props import SOURCEOPS_AttachmentProps
from . particle_props import SOURCEOPS_ParticleProps
from . surface_props import SOURCEOPS_SurfaceProps

VTF_FORMATS =["RGBA8888", "ABGR8888", "RGB888", "BGR888", "RGB565", "I8", "IA88", "A8", "RGB888_BLUESCREEN", "BGR888_BLUESCREEN", "ARGB8888", "BGRA8888", "DXT1", "DXT3", "DXT5", "BGRX8888", "BGR565", "BGRX5551", "BGRA4444", "DXT1_ONEBITALPHA", "BGRA5551", "UV88", "UVWQ8888", "RGBA16161616F", "RGBA16161616", "UVLX8888"]
VTF_RESIZE_METHODS =["NEAREST", "BIGGEST", "SMALLEST"]
VTF_RESIZE_FILTERS =["POINT", "BOX", "TRIANGLE", "QUADRATIC", "CUBIC", "CATROM", "MITCHELL", "GAUSSIAN", "SINC", "BESSEL", "HANNING", "HAMMING", "BLACKMAN", "KAISER"]
VTF_SHARPEN_FILTERS =["NONE", "NEGATIVE", "LIGHTER", "DARKER", "CONTRASTMORE", "CONTRASTLESS", "SMOOTHEN", "SHARPENSOFT", "SHARPENMEDIUM", "SHARPENSTRONG", "FINDEDGES", "CONTOUR", "EDGEDETECT", "EDGEDETECTSOFT", "EMBOSS", "MEANREMOVAL", "UNSHARP", "XSHARPEN", "WARPSHARP"]
VTF_NORMAL_KERNELS =["4X", "3X3", "5X5", "7X7", "9X9", "DUDV"]
VTF_NORMAL_HEIGHTS =["ALPHA", "AVERAGERGB", "BIASEDRGB", "RED", "GREEN", "BLUE", "MAXRGB", "COLORSPACE"]
VTF_NORMAL_ALPHAS =["NOCHANGE", "HEIGHT", "BLACK", "WHITE"]


class SOURCEOPS_ModelProps(bpy.types.PropertyGroup):
    material_folder_items: bpy.props.CollectionProperty(type=SOURCEOPS_MaterialFolderProps)
    material_folder_index: bpy.props.IntProperty(default=0)
    
    model_folder_items: bpy.props.CollectionProperty(type=SOURCEOPS_ModelFolderProps)
    model_folder_index: bpy.props.IntProperty(default=0)
    
    material_items: bpy.props.CollectionProperty(type=SOURCEOPS_MaterialProps)
    material_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    skin_items: bpy.props.CollectionProperty(type=SOURCEOPS_SkinProps)
    skin_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')
    
    texturegroup_items: bpy.props.CollectionProperty(type=SOURCEOPS_MaterialFolderProps)
    texturegroup_index: bpy.props.IntProperty(default=0)

    sequence_items: bpy.props.CollectionProperty(type=SOURCEOPS_SequenceProps)
    sequence_index: bpy.props.IntProperty(default=0)

    attachment_items: bpy.props.CollectionProperty(type=SOURCEOPS_AttachmentProps)
    attachment_index: bpy.props.IntProperty(default=0)

    particle_items: bpy.props.CollectionProperty(type=SOURCEOPS_ParticleProps)
    particle_index: bpy.props.IntProperty(default=0)

    export_checked: bpy.props.BoolProperty(name='Export', default=True)
    name: bpy.props.StringProperty(name='Name', default='example/model')
    rename_material: bpy.props.StringProperty(name='Rename Material', default='')

    def poll_armature(self, object): return object.type == 'ARMATURE'
    armature: bpy.props.PointerProperty(name='Armature', type=bpy.types.Object, poll=poll_armature)

    def poll_reference(self, object): return object not in (self.collision, self.bodygroups, self.stacking, getattr(self, "lod_1_collection", None))
    reference: bpy.props.PointerProperty(name='Reference', type=bpy.types.Collection, poll=poll_reference)

    def poll_collision(self, object): return object not in (self.reference, self.bodygroups, self.stacking, getattr(self, "lod_1_collection", None))
    collision: bpy.props.PointerProperty(name='Collision', type=bpy.types.Collection, poll=poll_collision)

    def poll_lod_collection(self, object): return object not in (self.reference, self.collision, self.bodygroups, self.stacking)
    lod_1_collection: bpy.props.PointerProperty(name='LOD 1', type=bpy.types.Collection, poll=poll_lod_collection)
    lod_1_distance: bpy.props.IntProperty(name='LOD 1 Dist', default=10, min=0)
    lod_2_collection: bpy.props.PointerProperty(name='LOD 2', type=bpy.types.Collection, poll=poll_lod_collection)
    lod_2_distance: bpy.props.IntProperty(name='LOD 2 Dist', default=20, min=0)
    lod_3_collection: bpy.props.PointerProperty(name='LOD 3', type=bpy.types.Collection, poll=poll_lod_collection)
    lod_3_distance: bpy.props.IntProperty(name='LOD 3 Dist', default=30, min=0)
    lod_4_collection: bpy.props.PointerProperty(name='LOD 4', type=bpy.types.Collection, poll=poll_lod_collection)
    lod_4_distance: bpy.props.IntProperty(name='LOD 4 Dist', default=40, min=0)
    lod_5_collection: bpy.props.PointerProperty(name='LOD 5', type=bpy.types.Collection, poll=poll_lod_collection)
    lod_5_distance: bpy.props.IntProperty(name='LOD 5 Dist', default=50, min=0)
    lod_6_collection: bpy.props.PointerProperty(name='LOD 6', type=bpy.types.Collection, poll=poll_lod_collection)
    lod_6_distance: bpy.props.IntProperty(name='LOD 6 Dist', default=60, min=0)

    def poll_bodygroups(self, object): return object not in (self.reference, self.collision, self.stacking)
    bodygroups: bpy.props.PointerProperty(name='Bodygroups', type=bpy.types.Collection, poll=poll_bodygroups)

    def poll_stacking(self, object): return object not in (self.reference, self.collision, self.bodygroups)
    stacking: bpy.props.PointerProperty(name='Stacking', type=bpy.types.Collection, poll=poll_stacking)

    surface: bpy.props.EnumProperty(name='Surface Property', items=SOURCEOPS_SurfaceProps, default='default')
    glass: bpy.props.BoolProperty(name='Has Glass', default=False)
    static: bpy.props.BoolProperty(name='Static Prop', default=False)
    static_prop_combine: bpy.props.BoolProperty(name='Static Prop Combine', default=False)
    joints: bpy.props.BoolProperty(name='Collision Joints', default=False)
    mass: bpy.props.IntProperty(name='Model Mass', default=0, min=0)
    prepend_armature: bpy.props.BoolProperty(name='Prepend Armature', default=False)
    ignore_transforms: bpy.props.BoolProperty(name='Ignore Transforms', default=False)
    origin_source: bpy.props.EnumProperty(name='Origin Source', items=[('MANUAL', 'Manual Input', ''), ('OBJECT', 'Object', '')])
    origin_object: bpy.props.PointerProperty(name='Origin Object', type=bpy.types.Object)
    origin_x: bpy.props.FloatProperty(name='Origin +X', default=0.0)
    origin_y: bpy.props.FloatProperty(name='Origin +Y', default=0.0)
    origin_z: bpy.props.FloatProperty(name='Origin Z', default=0.0)
    rotation: bpy.props.FloatProperty(name='Origin Rotation', default=0.0)
    scale: bpy.props.FloatProperty(name='Model Scale', default=1.0)

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

    vmt_shader: bpy.props.EnumProperty(name="VMT Shader", items=[("VertexLitGeneric", "VertexLitGeneric", ""), ("UnlitGeneric", "UnlitGeneric", ""), ("LightmappedGeneric", "LightmappedGeneric", "")], default="VertexLitGeneric")
    vmt_translucent: bpy.props.BoolProperty(name="$translucent", default=False)
    vmt_alphatest: bpy.props.BoolProperty(name="$alphatest", default=True) 
    vmt_nocull: bpy.props.BoolProperty(name="$nocull", default=False)
    vmt_envmap: bpy.props.BoolProperty(name="$envmap", description="Adds env_cubemap reflection properties", default=False)
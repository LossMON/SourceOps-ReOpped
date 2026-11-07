import bpy
from . model_props import SOURCEOPS_ModelProps
from . map_props import SOURCEOPS_MapProps
from . surface_props import SOURCEOPS_SurfaceProps

def update_view_model(self, context):
    if self.auto_view_model:
        self.auto_view_model_plusplus = False

def update_view_model_plusplus(self, context):
    if self.auto_view_model_plusplus:
        self.auto_view_model = False

class SOURCEOPS_GlobalProps(bpy.types.PropertyGroup):
    model_items: bpy.props.CollectionProperty(type=SOURCEOPS_ModelProps)
    model_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    map_items: bpy.props.CollectionProperty(type=SOURCEOPS_MapProps)
    map_index: bpy.props.IntProperty(default=0, name='Ctrl click to rename')

    simulation_input: bpy.props.PointerProperty(
        name='Simulation Input',
        description='The collection containing your rigid body objects',
        type=bpy.types.Collection,
    )

    simulation_output: bpy.props.PointerProperty(
        name='Simulation Output',
        description='The collection your rigged objects will go',
        type=bpy.types.Collection,
    )

    default_surface: bpy.props.EnumProperty(
        name='Batch Surface',
        description='Surface property applied to newly added models, or batch-applied via the button',
        items=SOURCEOPS_SurfaceProps,
        default='default',
    )

    # --- AUTO EXPORT SAVED SETTINGS ---
    auto_export_meshes: bpy.props.BoolProperty(name='Export Meshes', description='Export the meshes and animations as SMD/FBX', default=True)
    auto_generate_qc: bpy.props.BoolProperty(name='Generate QC', description='Generate the QC based on your settings', default=True)
    auto_compile_qc: bpy.props.BoolProperty(name='Compile QC', description='Compile the QC to an MDL', default=True)
    
    use_studiomdlplusplus: bpy.props.BoolProperty(name='Use StudioMDL++', description='Force the compiler to use studiomdlplusplus.exe instead of studiomdl.exe (Must exist in the bin folder)', default=False)
    
    auto_view_model: bpy.props.BoolProperty(name='View Model', description='Open the compiled models in HLMV', default=False, update=update_view_model)
    auto_view_model_plusplus: bpy.props.BoolProperty(name='View Model++', description='Open the compiled models in HLMV++', default=False, update=update_view_model_plusplus)
    
    auto_use_addon_folder: bpy.props.BoolProperty(name='Create Model Folder Name', description='Create a folder with the Model Name inside your Game Models path and sort files correctly', default=True)
    auto_create_material_folder: bpy.props.BoolProperty(name='Create Material Folder', description='Put exported textures inside a root "materials" folder. If unchecked, exports directly to your Models path alongside your meshes.', default=True)
    auto_create_folders_alone: bpy.props.BoolProperty(name='Create Model+Material Folder Alone No Model Name', description='Export directly into "models" and "materials" folders without creating a parent folder named after the model', default=False)
    auto_export_materials: bpy.props.BoolProperty(name='Export Materials (VTF/VMT)', description='Automatically extract, format, and generate VTF/VMT files using VTFcmd', default=True)
    auto_overwrite_vtf: bpy.props.BoolProperty(name='Overwrite VTF', description='If enabled, existing VTF files will be overwritten.', default=True)
    auto_overwrite_vmt: bpy.props.BoolProperty(name='Overwrite VMT', description='If enabled, existing VMT files will be overwritten.', default=True)

    # --- TEXTURE COMBINER PROPERTIES ---
    combiner_target_collection: bpy.props.PointerProperty(
        name='Target Collection',
        description='Select the collection containing the model meshes to combine',
        type=bpy.types.Collection,
    )
    combiner_atlas_size: bpy.props.EnumProperty(
        name='Atlas size',
        description='Select atlas size or mode',
        items=[
            ('2048', '2048 x 2048 (2K)', 'Standard 2048x2048 bake'),
            ('512', '512 x 512', 'Standard 512x512 bake'),
            ('1024', '1024 x 1024 (1K)', 'Standard 1024x1024 bake'),
            ('4096', '4096 x 4096 (4K)', 'Standard 4096x4096 bake'),
            ('QUAD', 'Quadratic', 'Square Power of 2 (Auto fit up to 4K)'),
            ('PO2', 'Power of 2', 'Power of 2 (Auto fit up to 4K)'),
            ('AUTO', 'Automatic', 'Minimal size fitting textures'),
            ('CUSTOM', 'Custom Size', 'Specify an exact custom resolution'),
        ],
        default='AUTO',
    )
    combiner_custom_width: bpy.props.IntProperty(
        name='Custom Width',
        description='Custom atlas width in pixels',
        default=1024, min=16, max=8192
    )
    combiner_custom_height: bpy.props.IntProperty(
        name='Custom Height',
        description='Custom atlas height in pixels',
        default=1024, min=16, max=8192
    )
    combiner_bake_margin: bpy.props.IntProperty(
        name='Margin (px)',
        description='Pixel margin around UV islands to prevent edge bleeding',
        default=12,
        min=0,
        max=64,
    )
    combiner_uv_margin: bpy.props.FloatProperty(
        name='UV Island Margin',
        description='Spacing between UV islands in the atlas unwrap',
        default=0.012,
        min=0.0,
        max=0.1,
        precision=3,
    )
    combiner_crop: bpy.props.BoolProperty(
        name='Crop outside images by UV',
        description='Align and crop images by UV if materials have UV coordinates outside bounds',
        default=True,
    )
    combiner_pixel_art: bpy.props.BoolProperty(
        name='Pixel Art / Small Textures',
        description='Avoids 1-pixel UV scaling for small textures',
        default=False,
    )
    combiner_diffuse_size: bpy.props.IntProperty(
        name='Size of materials without image',
        description='Select the size in pixels for materials that only consist of a color',
        min=8,
        max=256,
        default=32,
    )
    combiner_gaps: bpy.props.IntProperty(
        name='Size of gaps between images',
        description='Select size of gaps between images',
        min=0,
        max=32,
        default=0,
    )

    panel: bpy.props.EnumProperty(
            name='Panel',
            description='Which panel to display',
            items=[
                ('GAMES', 'Games', 'Display the games panel', 'PREFERENCES', 1),
                ('MODELS', 'Models', 'Display the models panel', 'MESH_CUBE', 2),
                ('MODEL_OPTIONS', 'Model Options', 'Display the model options panel', 'MODIFIER', 3),
                ('TEXTURES', 'Textures', 'Display the textures panel', 'TEXTURE', 4),
                ('SEQUENCES', 'Sequences', 'Display the sequences panel', 'SEQUENCE', 5),
                ('EVENTS', 'Events', 'Display the events panel', 'ACTION', 6),
                ('ATTACHMENTS', 'Attachments', 'Display the attachments panel', 'BONE_DATA', 7),
                ('PARTICLES', 'Particles', 'Display the particles panel', 'PARTICLES', 8),
                ('MAPS', 'Maps', 'Display the maps panel', 'MOD_BUILD', 9),
                ('SIMULATION', 'Simulation', 'Display the simulation panel', 'PHYSICS', 10),
                ('MISC', 'Misc', 'Display the misc panel', 'MONKEY', 11),
                ('TEXTURE_COMBINER', 'Texture Combiner', 'Display the texture combiner panel', 'IMAGE', 12),
            ],
        )
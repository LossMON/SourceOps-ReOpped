import bpy

class SOURCEOPS_ModelFolderProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Relative Path',
        description='$modelname, the folder inside of which to place the compiled model, relative to your game\'s models folder',
        default='weapons/example',
    )
    modelsrc_path: bpy.props.StringProperty(
        name='Modelsrc Relative Path',
        description='Folder inside modelsrc to export source files. If left empty, uses the relative path above',
        default='',
    )

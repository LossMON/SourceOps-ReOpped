import bpy

class SOURCEOPS_ModelFolderProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name='Relative Path',
        description='$modelname, the folder inside of which to place the compiled model, relative to your game\'s models folder',
        default='weapons/example',
    )
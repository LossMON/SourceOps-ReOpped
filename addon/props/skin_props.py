import bpy

class SOURCEOPS_SkinProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Material Name', default='')
    linked_materials: bpy.props.StringProperty(name='Linked Materials', default='')
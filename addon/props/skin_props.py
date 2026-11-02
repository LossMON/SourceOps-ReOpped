import bpy

def update_add_linked_skin(self, context):
    val = self.add_linked_skin.strip()
    if val:
        current = [m for m in self.linked_materials.split() if m]
        if val not in current:
            current.append(val)
            self.linked_materials = " ".join(current)
        self.add_linked_skin = ""

class SOURCEOPS_SkinProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Material Name', default='')
    linked_materials: bpy.props.StringProperty(name='Linked Skins', default='')
    add_linked_skin: bpy.props.StringProperty(name='Linked Skins', default='', update=update_add_linked_skin)
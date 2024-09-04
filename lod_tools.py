import bpy, math
from .panel_base import BlendTools_Panel

class LODSettings(bpy.types.PropertyGroup):
    int_LODCount: bpy.props.IntProperty(
        name="LOD Count",
        min=1,
        soft_max=6,
        default=4,
    )
    float_LODBias: bpy.props.FloatProperty(
        name="LOD Bias",
        min=0,
        max=1,
        default=1,

    )
    
class LODTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_parent_id = "BLENDTOOLS_PT_panel"
    bl_label = "LOD"
    
    @classmethod
    def poll(cls, context):
        return (bpy.context.active_object is not None)


    def draw(self, context):
        scene = context.scene
        settings = scene.lodSettings
        layout = self.layout
        layout.prop(settings, "int_LODCount", slider=True)
        layout.prop(settings, "float_LODBias", slider=True)
        layout.operator("object.lodify", text="LODify")

        if "WN_Decimate" in bpy.context.active_object.modifiers:
            updateBox = layout.box()
            updateBox.label(text="Update")
            updateBox.prop(bpy.context.active_object.modifiers["WN_Decimate"], "ratio", text="Ratio")
            updateBox.operator("object.updatelod", text="Update").id = int(bpy.context.active_object.users_collection[0].name[-1:])

class UpdateLODs_OT_Operator(bpy.types.Operator):
    bl_idname= "object.updatelod"
    bl_label="updatelod"
    bl_description="Update LODs"
    id : bpy.props.IntProperty()
    def execute(self, context):
        scene = context.scene
        settings = scene.lodSettings
        OBs = bpy.context.selected_objects
        active = bpy.context.active_object

        for ob in bpy.data.collections[f"LOD{self.id}"].objects:
            if "WN_Decimate" in ob.modifiers:
                ob.modifiers["WN_Decimate"].ratio = bpy.context.active_object.modifiers["WN_Decimate"].ratio

        return{'FINISHED'}

class LODify_OT_Operator(bpy.types.Operator):
    bl_idname= "object.lodify"
    bl_label="lodify"
    bl_description="Create LODs"
    id : bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        settings = scene.lodSettings
        OBs = bpy.context.selected_objects
        active = bpy.context.active_object

        bpy.ops.ed.undo_push()

        for i in range(0, settings.int_LODCount):
            if f"LOD{i}" not in bpy.data.collections:
                coll = bpy.data.collections.new(f"LOD{i}")
                bpy.context.scene.collection.children.link(coll)
                coll["decRatio"] = 1.0

        for ob in OBs:
            bpy.ops.object.select_all(action='DESELECT')
            if ob.parent == None or ob == active:
                bpy.context.view_layer.objects.active = ob
                for i in range(0, settings.int_LODCount):
                    bpy.ops.object.select_all(action='DESELECT')
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.object.select_grouped(extend=True, type="CHILDREN_RECURSIVE")
                    bpy.ops.object.duplicate()
                    lodObs = bpy.context.selected_objects
                    for lodOb in lodObs:
                        for other_col in lodOb.users_collection:
                            other_col.objects.unlink(lodOb)
                        bpy.data.collections[f"LOD{i}"].objects.link(lodOb)
                        lodOb.name = (lodOb.name[:-4] if lodOb.name[-4:-1] == ".00" else lodOb.name) + f"_LOD{i}"
                        decMod = lodOb.modifiers.new("WN_Decimate", 'DECIMATE')
                        if i > 0:
                            decMod.ratio = (1/(i+1)) * settings.float_LODBias
                            bpy.data.collections[f"LOD{i}"]["decRatio"] = (1/(i+1)) * settings.float_LODBias
                    
            break

        bpy.ops.ed.undo_push()


        return{'FINISHED'}
    

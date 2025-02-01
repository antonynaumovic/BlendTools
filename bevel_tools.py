import bpy, math
from pathlib import Path
from .panel_base import BlendTools_Panel

class BevelSettings(bpy.types.PropertyGroup):
    float_bevelAmount : bpy.props.FloatProperty(
        name="Bevel Amount",
        description="Bevel Weight Amount",
        default=0.001,
        min=0.0,
        max=30,
        unit='LENGTH',
    )
    float_sharpAngle : bpy.props.FloatProperty(
        name="Sharpness Angle",
        description="Sharp Weight Amount",
        default=0.523599,
        min=0,
        max=math.pi*2,
        unit='ROTATION',
        subtype='ANGLE'
    )
    float_smoothAngle : bpy.props.FloatProperty(
        name="Smooth Angle",
        description="Auto Smooth Angle",
        default=0.959931,
        min=0,
        max=math.pi*2,
        unit='ROTATION',
        subtype='ANGLE'
    )
    enum_bevelAction: bpy.props.EnumProperty(
        name="Bevel Preset",
        description="Action Selecting",
        items=[
        ("0", "Sub D", ""),
        ("1", "Default", ""),
        ]
    )
    bool_redoWeights: bpy.props.BoolProperty(
        name="Redo Weights",
        description="Reset Weights and add new",
        default=False
    )
    int_segAmounts: bpy.props.IntProperty(
        name="Segment Count",
        description="Bevel Segment Amount",
        default=1,
        min=1
    )


class BevelTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_parent_id = "BLENDTOOLS_PT_panel"
    bl_label = "Bevel"
    @classmethod
    def poll(cls, context):
        return (context.object is not None)


    def draw(self, context):
        scene = context.scene
        settings = scene.bevelSettings
        layout = self.layout
        
        layout.operator("object.bevelmod", text="Bevel")
        layout.operator("object.smoothmod", text="Smooth By Angle")
        layout.operator("object.weightedmod", text="Weighted Normal")
        layout.prop(settings, "enum_bevelAction")
        layout.prop(settings, "float_bevelAmount")
        layout.prop(settings, "float_sharpAngle")
        layout.prop(settings, "float_smoothAngle")
        layout.prop(settings, "int_segAmounts")
        layout.prop(settings, "bool_redoWeights")



class UpdateBevelTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_parent_id = "BLENDTOOLS_PT_panel"
    bl_label = "Update Bevel"
    @classmethod
    def poll(cls, context):
        return (None if context.object is None else 
        list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers)))


    def draw(self, context):
        scene = context.scene
        settings = scene.bevelSettings
        layout = self.layout
        bevelMods = list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers))
        row = layout.row()
        layout.prop(bevelMods[-1], "width", text="Width")
        layout.prop(bevelMods[-1], "segments", text="Segments")
        if len(list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers))) and len(bpy.context.selected_objects) > 1:
            layout.operator("object.updatebevelmod", text="Copy To Selected")

class UpdateBevel_OT_Operator(bpy.types.Operator):
    
    bl_idname= "object.updatebevelmod"
    bl_label="bevelmod"
    bl_description="Update Bevel"

    def execute(self, context):
        scene = context.scene
        context = bpy.context
        BevelSettings = scene.bevelSettings
        bevelList = list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers))
        smoothList = list(filter(lambda x: x.name.startswith("WN_Smooth"), bpy.context.object.modifiers))
        smoothAmount = len(smoothList)
        curBevel = bevelList[-1]
        properties = []
        targets = context.copy()
        for prop in curBevel.bl_rna.properties:
            if not prop.is_readonly:
                properties.append(prop.identifier)
        if len(targets["selected_objects"]) == 0:
            return{"FINISHED"}
        
        for i in targets["selected_objects"]:
            i.select_set(True)
        for target in targets["selected_objects"]:
            bpy.context.view_layer.objects.active = target
            if target.type == "MESH":
                bevelList = list(filter(lambda x: x.name.startswith("WN_Bevel_"), target.modifiers))
                if len(bevelList) > 0:
                    bevelToUpdate = bevelList[-1]
                else:
                    if smoothAmount == 0:
                        bpy.ops.object.shade_smooth()
                        smoothMod = bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
                        for mod in reversed(target.modifiers):
                            if mod.type == "NODES":
                                mod.name = f"WN_SMOOTH"
                                mod["Input_1"] = BevelSettings.float_smoothAngle
                                break
                    bevelToUpdate = bpy.ops.object.modifier_add(type='BEVEL')
                    for mod in reversed(target.modifiers):
                        if mod.type == "BEVEL":
                            mod.name = f"WN_Bevel_1"
                            break
                    bevelToUpdate = target.modifiers["WN_Bevel_1"]
                    target.data.use_auto_smooth = True
                for prop in properties:
                    setattr(bevelToUpdate, prop, getattr(curBevel, prop))
        bpy.context.view_layer.objects.active = targets['active_object']
        return{"FINISHED"}


class Smooth_OT_Operator(bpy.types.Operator):
    
    bl_idname= "object.smoothmod"
    bl_label="smoothmod"
    bl_description="Add Smooth Modifier"

    def execute(self, context):
        scene = context.scene
        C = bpy.context
        BevelSettings = scene.bevelSettings

        obs = bpy.context.selected_objects
        active = bpy.context.active_object
        try:
            for ob in obs:
                bpy.ops.object.select_all(action='DESELECT')
                #deselect all but just one object and make it active
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                if ob.type == "MESH":
                    smoothList = list(filter(lambda x: x.name.startswith("WN_Smooth"), ob.modifiers))
                    smoothAmount = len(smoothList)
                    if smoothAmount == 0:
                        bpy.ops.object.shade_smooth()
                        bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
                        for mod in reversed(ob.modifiers):
                            if mod.type == "NODES":
                                mod.name = f"WN_Smooth"
                                mod["Input_1"] = BevelSettings.float_smoothAngle
                                break
                        
                for ob in obs:
                    ob.select_set(state=True)
                bpy.context.view_layer.objects.active = active
        except Exception as e:
            self.report({"WARNING"}, str(e))
        
        return {"FINISHED"}

class Weighted_OT_Operator(bpy.types.Operator):
    
    bl_idname= "object.weightedmod"
    bl_label="weightedmod"
    bl_description="Add Weighted Normal Modifier"

    def execute(self, context):
        scene = context.scene
        C = bpy.context
        BevelSettings = scene.bevelSettings
        obs = bpy.context.selected_objects
        active = bpy.context.active_object
        try:
            for ob in obs:
                bpy.ops.object.select_all(action='DESELECT')
                #deselect all but just one object and make it active
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                if ob.type == "MESH":
                    smoothList = list(filter(lambda x: x.name.startswith("WN_Weighted Normal"), ob.modifiers))
                    smoothAmount = len(smoothList)
                    if smoothAmount == 0:
                        bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')
                        for mod in reversed(ob.modifiers):
                            if mod.type == "WEIGHTED_NORMAL":
                                mod.name = f"WN_Weighted Normal"
                                mod.weight = 100
                                break
                    else:
                        for i in smoothList:
                            i.weight = 100
                for ob in obs:
                    ob.select_set(state=True)
                bpy.context.view_layer.objects.active = active
        except Exception as e:
            self.report({"WARNING"}, str(e))
        
        return {"FINISHED"}


class Bevel_OT_Operator(bpy.types.Operator):
    
    bl_idname= "object.bevelmod"
    bl_label="bevelmod"
    bl_description="Add Bevel Modifier"

    def execute(self, context):
        scene = context.scene
        C = bpy.context
        BevelSettings = scene.bevelSettings

        obs = bpy.context.selected_objects
        active = bpy.context.active_object
        try:
            for ob in obs:
                #deselect all but just one object and make it active
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                if ob.type == "MESH":
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type="EDGE")
                    if BevelSettings.bool_redoWeights:
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.transform.edge_bevelweight(value=-1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.mesh.edges_select_sharp(sharpness=BevelSettings.float_sharpAngle)
                    bpy.ops.transform.edge_bevelweight(value=1)
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bevelList = list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers))
                    smoothList = list(filter(lambda x: x.name.startswith("WN_Smooth"), bpy.context.object.modifiers))
                    bevelAmount = len(bevelList)
                    smoothAmount = len(smoothList)
                    if bevelAmount == 0:
                        bpy.ops.object.modifier_add(type='BEVEL')
                        for mod in reversed(ob.modifiers):
                            if mod.type == "BEVEL":
                                mod.name = f"WN_Bevel_{bevelAmount+1}"
                                break
                        curBevel = bpy.context.object.modifiers[f"WN_Bevel_{bevelAmount+1}"]
                        curBevel.limit_method = 'WEIGHT'
                    else:
                        curBevel = bevelList[-1]

                    if smoothAmount == 0:
                            bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="", relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle")
                            for mod in reversed(ob.modifiers):
                                if mod.type == "NODES":
                                    mod.name = f"WN_Smooth"
                                    mod["Input_1"] = BevelSettings.float_smoothAngle  
                                    break
                                          
                    if BevelSettings.enum_bevelAction == "0":
                        curBevel.miter_outer = "MITER_ARC"
                        curBevel.use_clamp_overlap = False
                        curBevel.loop_slide = False
                    curBevel.width = BevelSettings.float_bevelAmount
                    curBevel.harden_normals = True
                    curBevel.segments = BevelSettings.int_segAmounts
                for ob in obs:
                    ob.select_set(state=True)
                bpy.context.view_layer.objects.active = active
        except Exception as e:
            self.report({"WARNING"}, str(e))
        
        return {"FINISHED"}
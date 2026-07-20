# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from .panel_base import BlendTools_Panel
from .mirror_tools import *
from .bevel_tools import *
from .lod_tools import *
from .extra_tools import *

bl_info = {
    "name": "BlendTools",
    "author": "Antony Naumovic",
    "description": "",
    "blender": (5, 0, 0),
    "version": (0, 0, 24),
    "location": "",
    "warning": "",
    "category": "Tools"
}


class BLENDTOOLS_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_idname = "BLENDTOOLS_PT_panel"
    bl_label = "BlendTools"

    def draw(self, context):
        layout = self.layout
        label = layout.label(text="Quick Tools:")
        row = layout.row(align=True)
        row.operator("object.bevelmod", text="Bevel", icon="MOD_BEVEL")
        row.operator("object.bevelmodonly", text="", icon="MODIFIER_DATA")
        row = layout.row(align=False)
        row.operator("object.smoothmod", text="Smooth By Angle", icon="MOD_SMOOTH")
        row.operator("object.weightedmod", text="Weighted Normal", icon="MOD_NORMALEDIT")
        row = layout.row(align=True)
        row.operator("object.triangulate", text="Triangulate", icon="MOD_TRIANGULATE")


class BLENDTOOLS_PT_Panel_tools(BlendTools_Panel, bpy.types.Panel):
    bl_idname = "BLENDTOOLS_PT_panel_tools"
    bl_label = "Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        pass


classes = (BevelSettings,
           MirrorSettings,
           LODSettings,
           BLENDTOOLS_PT_Panel,
           BLENDTOOLS_PT_Panel_mirror,
           BLENDTOOLS_PT_Panel_tools,
           BLENDTOOLS_PT_Panel_bevel,
           BLENDTOOLS_PT_Panel_updatebevel,
           BLENDTOOLS_PT_Panel_beveloptions,
           BLENDTOOLS_PT_Panel_extra,
           BLENDTOOLS_PT_Panel_lod,
           BLENDTOOLS_OT_Operator_bevel,
           BLENDTOOLS_OT_Operator_updatebevel,
           BLENDTOOLS_OT_Operator_addmirror,
           BLENDTOOLS_OT_Operator_triangulate,
           BLENDTOOLS_OT_Operator_addsuffix,
           BLENDTOOLS_OT_Operator_removesuffix,
           BLENDTOOLS_OT_Operator_updatemirror,
           BLENDTOOLS_OT_Operator_decustom,
           BLENDTOOLS_OT_Operator_showconcave,
           BLENDTOOLS_OT_Operator_togglecreases,
           BLENDTOOLS_OT_Operator_setcreasesweight,
           BLENDTOOLS_OT_Operator_lodify,
           BLENDTOOLS_OT_Operator_updatelod,
           BLENDTOOLS_OT_Operator_smooth,
           BLENDTOOLS_OT_Operator_weighted,
           BLENDTOOLS_OT_Operator_mergematerials,
           BLENDTOOLS_OT_Operator_bevelmodonly,
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bevelSettings = bpy.props.PointerProperty(
        type=BevelSettings)
    bpy.types.Scene.mirrorSettings = bpy.props.PointerProperty(
        type=MirrorSettings)
    bpy.types.Scene.lodSettings = bpy.props.PointerProperty(type=LODSettings)


def unregister():
    del bpy.types.Scene.lodSettings
    del bpy.types.Scene.mirrorSettings
    del bpy.types.Scene.bevelSettings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

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
    "name" : "BlendTools",
    "author" : "Antony Naumovic",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


class BlendTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_idname = "BLENDTOOLS_PT_panel"
    bl_label = "BlendTools"
    def draw(self, context):
        pass
        

classes = (BevelSettings,
           MirrorSettings,
           LODSettings,
           BlendTools_PT_Panel,
           BevelTools_PT_Panel,
           UpdateBevelTools_PT_Panel,
           Bevel_OT_Operator,
           UpdateBevel_OT_Operator,
           MirrorTools_PT_Panel,
           AddMirror_OT_Operator,
           ExtraTools_PT_Panel,
           Triangulate_OT_Operator,
           AddSuffix_OT_Operator,
           RemoveSuffix_OT_Operator,
           UpdateMirror_OT_Operator,
           DeCustom_OT_Operator,
           ShowConcave_OT_Operator,
           LODTools_PT_Panel,
           LODify_OT_Operator,
           UpdateLODs_OT_Operator
           )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bevelSettings = bpy.props.PointerProperty(type=BevelSettings)
    bpy.types.Scene.mirrorSettings = bpy.props.PointerProperty(type=MirrorSettings)
    bpy.types.Scene.lodSettings = bpy.props.PointerProperty(type=LODSettings)

def unregister():
    del bpy.types.Scene.bevelSettings
    del bpy.types.Scene.mirrorSettings
    del bpy.types.Scene.lodSettings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
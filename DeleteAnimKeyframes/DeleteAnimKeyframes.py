bl_info = {
    "name": "处理位移关键帧",
    "description": "此操作会删除X和Z的位移关键帧",
    "author": "大冰",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "category": "Animation"
}

import bpy
from bpy.types import Operator, Panel


class DeleteAnimKeyframesOperator(Operator):
    """Delete Anim Keyframes Operator"""
    bl_idname = "anim.delete_anim_keyframes"
    bl_label = "Delete Anim Keyframes"
    bl_description = "Delete translate Z and translate X keyframes from selected joints and their descendants."

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "ARMATURE"

    def clear_fcurve(self, fcurve):
        """删除fcurve上的所有keyframe"""
        if fcurve and fcurve.keyframe_points:
            for kf in reversed(fcurve.keyframe_points):  # 反向遍历，确保删除后索引不会错位
                fcurve.keyframe_points.remove(kf)

    def delete_joint_keyframes(self, obj, bone):
        """删除当前骨骼节点上的平移Z和平移X关键帧"""
        """XYZ对应Index 0 、 1 、 2"""
        for axis in ["location", "location"]:
            fcz = obj.animation_data.action.fcurves.find("pose.bones[\"%s\"].%s" % (bone.name, axis), index=2)
            self.clear_fcurve(fcz)
            if fcz and fcz.keyframe_points:
                print(f"Successfully deleted {axis} keyframes of {bone.name}.")
            else:
                print(f"No fcurve found on {bone.name} for {axis}.")
            fcx = obj.animation_data.action.fcurves.find("pose.bones[\"%s\"].%s" % (bone.name, axis), index=0)    
            self.clear_fcurve(fcx)
            if fcx and fcx.keyframe_points:
                print(f"Successfully deleted {axis} keyframes of {bone.name}.")
            else:
                print(f"No fcurve found on {bone.name} for {axis}.")    

    def delete_children_keyframes(self, obj, bone):
        """删除当前子节点上的平移Z和平移X关键帧"""
        children = [child for child in bone.children_recursive]
        if children:
            for child in children:
                fcz = obj.animation_data.action.fcurves.find("pose.bones[\"%s\"].location" % child.name, index=2)
                if fcz:
                    self.clear_fcurve(fcz)
                    if fcz.keyframe_points:
                        print(f"Successfully deleted location keyframes of {child.name}.")
                else:
                    print(f"No fcurve found on child node {child.name}.")
                fcx = obj.animation_data.action.fcurves.find("pose.bones[\"%s\"].location" % child.name, index=0)
                if fcx:
                    self.clear_fcurve(fcx)
                    if fcx.keyframe_points:
                        print(f"Successfully deleted location keyframes of {child.name}.")
                else:
                    print(f"No fcurve found on child node {child.name}.")    

    def execute(self, context):
        # 获取所选骨架
        obj = context.active_object
        selection = [bone for bone in obj.data.bones if bone.select]
        if not selection:
            self.report({"INFO"}, "Please select the joints.")
            return {"CANCELLED"}

        for bone in selection:
            print(f"Current bone: {bone.name}")
            have_keyframes = False

            fc = obj.animation_data.action.fcurves.find("pose.bones[\"%s\"].location" % bone.name, index=2)
            if fc:
                self.delete_joint_keyframes(obj, bone)
                have_keyframes = True
            else:
                print(f"No fcurve found on {bone.name}.")

            if not have_keyframes:
                print(f"No keyframes need to be deleted on {bone.name}.")

            self.delete_children_keyframes(obj, bone)

        self.report({"INFO"}, "All selected joints and their descendants have been processed.")
        return {"FINISHED"}


class DeleteAnimKeyframesPanel(Panel):
    """Delete Anim Keyframes Panel"""
    bl_idname = "OBJECT_PT_delete_anim_keyframes"
    bl_label = "处理位移关键帧"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Delete Anim Keyframes"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("anim.delete_anim_keyframes", text="选中骨架，切换到姿态模式，然后点我")


classes = [
    DeleteAnimKeyframesOperator,
    DeleteAnimKeyframesPanel
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

from typing import Any, Set
import bpy
from bpy.types import Context, UILayout

bl_info = {
    "name": "Simple Fade Manager",
    "author": "kanta",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "VSE(Sequencer) > Sidebar",
    "description": "BlenderのVSE(Video Sequence Editor)でフェード設定を簡単にするアドオン",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Sequencer",
}


class SIMPLE_FADE_MANAGER_OT_AddFade(bpy.types.Operator):
    bl_idname = "simple_fade_manager.add_fade"
    bl_label = "ストリップにフェードを追加"
    bl_description = "ストリップにフェードを追加します"
    bl_options = {"REGISTER"}

    fade_no: bpy.props.IntProperty(
        name="フェード番号", description="フェードリストのインデックス番号", default=0
    )

    @classmethod
    def poll(cls, context):
        return len(context.selected_sequences) > 0

    def execute(self, context: Context) -> Set[str] | Set[int]:
        scene = context.scene
        fade_list = scene.fade_list
        fade_info = fade_list[self.fade_no]
        bpy.ops.sequencer.fades_clear()
        if fade_info.fade_type in ["FadeIn", "FadeInAndOut"]:
            bpy.ops.sequencer.fades_add(
                duration_seconds=fade_info.fade_in_sec, type="IN"
            )
        if fade_info.fade_type in ["FadeOut", "FadeInAndOut"]:
            bpy.ops.sequencer.fades_add(
                duration_seconds=fade_info.fade_out_sec, type="OUT"
            )
        return {"FINISHED"}


class SIMPLE_FADE_MANAGER_OT_AppendInfoToFadeList(bpy.types.Operator):
    bl_idname = "simple_fade_manager.append_info_to_fade_list"
    bl_label = "追加"
    bl_description = "フェードリストに情報を追加"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> Set[str] | Set[int]:
        scene = context.scene
        fade_list = scene.fade_list
        info = fade_list.add()
        list_size = len(fade_list)
        info.name = f"フェード No.{list_size}"
        return {"FINISHED"}


class SIMPLE_FADE_MANAGER_OT_RemoveInfoFromFadeList(bpy.types.Operator):
    bl_idname = "simple_fade_manager.remove_info_from_fade_list"
    bl_label = "削除"
    bl_description = "フェードリストから情報を削除"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        fade_list = scene.fade_list
        return len(fade_list) > 0

    def execute(self, context: Context) -> Set[str] | Set[int]:
        scene = context.scene
        fade_list = scene.fade_list
        index = scene.fade_no
        fade_list.remove(index)
        list_size = len(fade_list)
        if list_size == 0:
            scene.fade_no = 0
        else:
            scene.fade_no = min(list_size - 1, index)
        return {"FINISHED"}


class SIMPLE_FADE_MANAGER_UL_FadeInfoList(bpy.types.UIList):
    bl_idname = "SIMPLE_FADE_MANAGER_UL_FadeInfoList"

    def draw_item(
        self,
        context: Context | None,
        layout: UILayout,
        data: Any | None,
        item: Any | None,
        icon: int | None,
        active_data: Any,
        active_property: str,
        index: Any | None = 0,
        flt_flag: Any | None = 0,
    ):
        layout.alignment = "LEFT"
        layout.label(text=f"{item.name}")


class SIMPLE_FADE_MANAGER_PT_ManageFadeList(bpy.types.Panel):
    bl_idname = "SIMPLE_FADE_MANAGER_PT_ManageFadeList"
    bl_label = "フェードの管理"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Fade Manager"

    @classmethod
    def poll(cls, context):
        return context.space_data.view_type == "SEQUENCER"

    def draw(self, context: Context):
        scene = context.scene
        layout = self.layout
        row = layout.row()
        row.template_list(
            SIMPLE_FADE_MANAGER_UL_FadeInfoList.bl_idname,
            "",
            scene,
            "fade_list",
            scene,
            "fade_no",
        )
        row = layout.row(align=True)
        row.operator(SIMPLE_FADE_MANAGER_OT_AppendInfoToFadeList.bl_idname, text="追加")
        row.operator(
            SIMPLE_FADE_MANAGER_OT_RemoveInfoFromFadeList.bl_idname, text="削除"
        )
        fade_list = scene.fade_list
        if len(fade_list) > 0:
            row = layout.row(align=True)
            fade_no = scene.fade_no
            item = fade_list[fade_no]
            row = layout.row(align=True)
            box = row.box()
            sp = box.split(factor=0.4, align=True)
            sp.alignment = "RIGHT"
            sp.label(text="名前")
            sp.prop(item, "name", text="")
            sp = box.split(factor=0.4, align=True)
            sp.alignment = "RIGHT"
            sp.label(text="種別")
            sp.prop(item, "fade_type", text="")
            if item.fade_type in ["FadeIn", "FadeInAndOut"]:
                sp = box.split(factor=0.4, align=True)
                sp.alignment = "RIGHT"
                sp.label(text="Fade In (sec)")
                sp.prop(item, "fade_in_sec", text="")
            if item.fade_type in ["FadeOut", "FadeInAndOut"]:
                sp = box.split(factor=0.4, align=True)
                sp.alignment = "RIGHT"
                sp.label(text="Fade Out (sec)")
                sp.prop(item, "fade_out_sec", text="")
            row = box.row(align=True)
            row.separator(factor=1)
            op = row.operator(SIMPLE_FADE_MANAGER_OT_AddFade.bl_idname)
            op.fade_no = scene.fade_no
        col = layout.column(align=True)
        col.separator()
        col.operator("sequencer.fades_clear", text="ストリップからフェードを削除")


class SIMPLE_FADE_MANAGER_FadeInfo(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="NEW FADE")
    fade_in_sec: bpy.props.FloatProperty(default=1.0)
    fade_out_sec: bpy.props.FloatProperty(default=1.0)
    fade_type: bpy.props.EnumProperty(
        items=[
            ("FadeIn", "フェードイン", "フェードイン"),
            ("FadeOut", "フェードアウト", "フェードアウト"),
            ("FadeInAndOut", "フェードイン/アウト", "フェードイン/アウト"),
        ],
        default="FadeInAndOut",
    )


classes = [
    SIMPLE_FADE_MANAGER_OT_AddFade,
    SIMPLE_FADE_MANAGER_OT_AppendInfoToFadeList,
    SIMPLE_FADE_MANAGER_OT_RemoveInfoFromFadeList,
    SIMPLE_FADE_MANAGER_UL_FadeInfoList,
    SIMPLE_FADE_MANAGER_PT_ManageFadeList,
    SIMPLE_FADE_MANAGER_FadeInfo,
]


def register_props():
    scene = bpy.types.Scene
    scene.fade_no = bpy.props.IntProperty(
        name="フェード番号", description="フェードリストのインデックス番号", default=0
    )
    scene.fade_list = bpy.props.CollectionProperty(type=SIMPLE_FADE_MANAGER_FadeInfo)


def unregister_props():
    scene = bpy.types.Scene
    del scene.fade_list
    del scene.fade_no


def register():
    for c in classes:
        bpy.utils.register_class(c)
    register_props()
    print(f"アドオン{bl_info['name']}が有効化されました")


def unregister():
    unregister_props()
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    print(f"アドオン{bl_info['name']}が無効化されました")


if __name__ == "__main__":
    register()

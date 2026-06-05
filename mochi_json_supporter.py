bl_info = {
    "name": "MochiFitter JSON補助ツール",
    "author": "amanoissui",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "category": "Object",
    "description": (
        "MochiFitter-BlenderAddon-kai (GPL v3) を使用して "
        "pose_basis / posediff JSON を生成する補助アドオン。"
        "本アドオンは GPL v3 の下で配布されます。"
    ),
    "license": "GPL-3.0",
    "doc_url": "https://github.com/Mega-Gorilla/MochiFitter-BlenderAddon-kai",
}

# --------------------------------------------------
# このアドオンは GNU General Public License v3.0 の下で配布されます。
# MochiFitter-BlenderAddon-kai (Copyright (C) Mega-Gorilla, GPL v3)
# https://github.com/Mega-Gorilla/MochiFitter-BlenderAddon-kai
# --------------------------------------------------

import bpy
import json
import os
import shutil
from mathutils import Matrix


# =========================================================
# ユーティリティ
# =========================================================

def find_mochifitter():
    """sys.modules から SaveAndApplyFieldAuto を探す"""
    import sys
    for mod_name, mod in sys.modules.items():
        if 'SaveAndApplyFieldAuto' in mod_name:
            return mod
    return None


def resolve_avatar_data_path(out_dir, avatar_name):
    """avatar_data_{名前}.json を出力フォルダから検索"""
    candidates = [
        os.path.join(out_dir, f"avatar_data_{avatar_name}.json"),
        os.path.join(out_dir, f"avatar_data_{avatar_name.lower()}.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def matrix_to_list(matrix):
    return [list(row) for row in matrix]


def call_mochi_save_pose(mochi, armature_obj, context,
                         filename, avatar_data_fname,
                         out_dir, blend_dir):
    """
    MochiFitter の save_armature_pose() を呼び出し、
    結果を out_dir へ移動する。
    """
    avatar_tmp = None
    try:
        if os.path.abspath(blend_dir) != os.path.abspath(out_dir):
            src_avatar = os.path.join(out_dir, avatar_data_fname)
            avatar_tmp = os.path.join(blend_dir, avatar_data_fname)
            shutil.copy2(src_avatar, avatar_tmp)

        prev_active = context.view_layer.objects.active
        context.view_layer.objects.active = armature_obj

        mochi.save_armature_pose(
            armature_obj,
            filename=filename,
            avatar_data_file=avatar_data_fname,
        )

        context.view_layer.objects.active = prev_active

        src_path = os.path.join(blend_dir, filename)
        dst_path = os.path.join(out_dir,   filename)
        if os.path.abspath(src_path) != os.path.abspath(dst_path):
            shutil.move(src_path, dst_path)

        return dst_path

    finally:
        if avatar_tmp and os.path.exists(avatar_tmp):
            os.remove(avatar_tmp)


def compute_posediff(template_pose, source_pose):
    """
    pose_basis_template.json と ソースの現在ポーズ の差分を計算。
    delta_matrix = template_delta.inverted() @ source_delta
    その他フィールドはソースの値をそのまま使用。
    """
    diff_data = {}
    common = set(template_pose.keys()) & set(source_pose.keys())
    for humanoid_name in sorted(common):
        tmpl       = template_pose[humanoid_name]
        src        = source_pose[humanoid_name]
        tmpl_delta = Matrix(tmpl['delta_matrix'])
        src_delta  = Matrix(src['delta_matrix'])
        diff_mat   = tmpl_delta.inverted_safe() @ src_delta
        diff_data[humanoid_name] = {
            'delta_matrix':           matrix_to_list(diff_mat),
            'location':               src['location'],
            'rotation':               src['rotation'],
            'scale':                  src['scale'],
            'head_world':             src['head_world'],
            'head_world_transformed': src['head_world_transformed'],
        }
    return diff_data


def resolve_dirs(props):
    """出力フォルダと blend_dir を解決"""
    out_dir = props.json_output_dir.strip()
    if not out_dir:
        if bpy.data.filepath:
            out_dir = os.path.dirname(bpy.path.abspath(bpy.data.filepath))
        else:
            return None, None
    else:
        out_dir = bpy.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    blend_dir = (
        os.path.dirname(bpy.path.abspath(bpy.data.filepath))
        if bpy.data.filepath else out_dir
    )
    return out_dir, blend_dir


# =========================================================
# Property Group
# =========================================================

class MochiJsonProps(bpy.types.PropertyGroup):

    target_avatar_name: bpy.props.StringProperty(
        name="ターゲットアバター名",
        description="出力ファイル名に使用（小文字化されます）",
        default=""
    )

    target_armature: bpy.props.PointerProperty(
        name="ターゲットArmature",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    source_avatar_name: bpy.props.StringProperty(
        name="ソースアバター名",
        description="posediff 生成用（avatar_data_{名前}.json を自動検索）",
        default=""
    )

    source_armature: bpy.props.PointerProperty(
        name="ソースArmature（ポーズ編集済み）",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    json_output_dir: bpy.props.StringProperty(
        name="出力フォルダ",
        description=(
            "JSONの保存先。"
            "avatar_data_{名前}.json と pose_basis_template.json もここから検索します"
        ),
        default="",
        subtype='DIR_PATH'
    )


# =========================================================
# Operator : pose_basis JSON生成
# =========================================================

class MOCHI_OT_generate_pose_basis(bpy.types.Operator):

    bl_idname  = "mochi_json.generate_pose_basis"
    bl_label   = "pose_basis を生成"
    bl_description = (
        "MochiFitter 経由でターゲットアーマチュアの "
        "pose_basis_{アバター名}.json を生成します"
    )
    bl_options = {'REGISTER'}

    def execute(self, context):
        props    = context.scene.mochi_json_props
        tgt_name = props.target_avatar_name.strip()

        if not tgt_name:
            self.report({'ERROR'}, "ターゲットアバター名を入力してください")
            return {'CANCELLED'}

        tgt_arm = props.target_armature
        if not tgt_arm:
            self.report({'ERROR'}, "ターゲットArmatureを指定してください")
            return {'CANCELLED'}

        mochi = find_mochifitter()
        if mochi is None:
            self.report(
                {'ERROR'},
                "MochiFitter が検出できません。"
                "MochiFitter-BlenderAddon-kai をインストール・有効化してください"
            )
            return {'CANCELLED'}

        out_dir, blend_dir = resolve_dirs(props)
        if out_dir is None:
            self.report({'ERROR'}, "出力フォルダが未指定で .blend が未保存です")
            return {'CANCELLED'}

        tgt_data_path = resolve_avatar_data_path(out_dir, tgt_name)
        if not tgt_data_path:
            self.report({'ERROR'}, f"avatar_data_{tgt_name}.json が見つかりません（フォルダ: {out_dir}）")
            return {'CANCELLED'}

        basis_filename    = f"pose_basis_{tgt_name.lower()}.json"
        avatar_data_fname = os.path.basename(tgt_data_path)

        try:
            call_mochi_save_pose(
                mochi, tgt_arm, context,
                basis_filename, avatar_data_fname,
                out_dir, blend_dir
            )
        except Exception as e:
            self.report({'ERROR'}, f"MochiFitter呼び出しエラー: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"生成完了 → {basis_filename}")
        return {'FINISHED'}


# =========================================================
# Operator : posediff JSON生成
# =========================================================

class MOCHI_OT_generate_posediff(bpy.types.Operator):

    bl_idname  = "mochi_json.generate_posediff"
    bl_label   = "posediff を生成"
    bl_description = (
        "pose_basis_template.json とソースの現在ポーズの差分から "
        "posediff_template_to_{アバター名}.json を生成します"
    )
    bl_options = {'REGISTER'}

    def execute(self, context):
        props    = context.scene.mochi_json_props
        tgt_name = props.target_avatar_name.strip()
        src_name = props.source_avatar_name.strip()

        if not tgt_name:
            self.report({'ERROR'}, "ターゲットアバター名を入力してください")
            return {'CANCELLED'}
        if not src_name:
            self.report({'ERROR'}, "ソースアバター名を入力してください")
            return {'CANCELLED'}

        src_arm = props.source_armature
        if not src_arm:
            self.report({'ERROR'}, "ソースArmatureを指定してください")
            return {'CANCELLED'}

        mochi = find_mochifitter()
        if mochi is None:
            self.report(
                {'ERROR'},
                "MochiFitter が検出できません。"
                "MochiFitter-BlenderAddon-kai をインストール・有効化してください"
            )
            return {'CANCELLED'}

        out_dir, blend_dir = resolve_dirs(props)
        if out_dir is None:
            self.report({'ERROR'}, "出力フォルダが未指定で .blend が未保存です")
            return {'CANCELLED'}

        # pose_basis_template.json を読み込む
        template_path = os.path.join(out_dir, "pose_basis_template.json")
        if not os.path.exists(template_path):
            self.report({'ERROR'}, f"pose_basis_template.json が見つかりません（フォルダ: {out_dir}）")
            return {'CANCELLED'}

        with open(template_path, 'r', encoding='utf-8') as f:
            template_pose = json.load(f)

        # ソースの avatar_data を検索
        src_data_path = resolve_avatar_data_path(out_dir, src_name)
        if not src_data_path:
            self.report({'ERROR'}, f"avatar_data_{src_name}.json が見つかりません")
            return {'CANCELLED'}

        avatar_data_fname = os.path.basename(src_data_path)

        # ソースの現在ポーズを MochiFitter 経由で取得
        try:
            tmp_fname = f"_vf_tmp_posediff_{src_name.lower()}.json"
            call_mochi_save_pose(
                mochi, src_arm, context,
                tmp_fname, avatar_data_fname,
                out_dir, blend_dir
            )
            tmp_path = os.path.join(out_dir, tmp_fname)
            with open(tmp_path, 'r', encoding='utf-8') as f:
                source_pose = json.load(f)
            os.remove(tmp_path)
        except Exception as e:
            self.report({'ERROR'}, f"ソースポーズ取得エラー: {e}")
            return {'CANCELLED'}

        # posediff 計算・保存
        diff_data  = compute_posediff(template_pose, source_pose)
        diff_fname = f"posediff_template_to_{tgt_name.lower()}.json"
        diff_path  = os.path.join(out_dir, diff_fname)
        with open(diff_path, 'w', encoding='utf-8') as f:
            json.dump(diff_data, f, indent=4, ensure_ascii=False)

        self.report(
            {'INFO'},
            f"生成完了 → {diff_fname}（pose_basis_template.json との差分）"
        )
        return {'FINISHED'}


# =========================================================
# Panel
# =========================================================

class VIEW3D_PT_mochi_json(bpy.types.Panel):

    bl_label       = "MochiFitter JSON補助ツール"
    bl_idname      = "VIEW3D_PT_mochi_json"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'MochiJSON'

    def draw(self, context):
        layout = self.layout
        props  = context.scene.mochi_json_props

        import sys
        mochi_found = any('SaveAndApplyFieldAuto' in k for k in sys.modules.keys())

        # MochiFitter 検出状態
        box_status = layout.box()
        if mochi_found:
            box_status.label(text="MochiFitter 検出済 ✓", icon='CHECKMARK')
        else:
            box_status.label(text="MochiFitter 未検出 → 全機能使用不可", icon='ERROR')
            box_status.label(
                text="MochiFitter-BlenderAddon-kai を有効化してください",
                icon='INFO'
            )

        # 共通設定
        box_common = layout.box()
        box_common.label(text="共通設定", icon='PREFERENCES')
        box_common.prop(props, "json_output_dir", text="出力フォルダ")

        out_dir     = props.json_output_dir.strip()
        out_dir_abs = bpy.path.abspath(out_dir) if out_dir else ""

        # pose_basis_template.json の存在確認
        if out_dir_abs:
            tmpl_path = os.path.join(out_dir_abs, "pose_basis_template.json")
            tmpl_exists = os.path.exists(tmpl_path)
            box_common.label(
                text="pose_basis_template.json ✓" if tmpl_exists
                     else "pose_basis_template.json が見つかりません",
                icon='CHECKMARK' if tmpl_exists else 'ERROR'
            )
        else:
            tmpl_exists = False

        box_common.prop(props, "target_avatar_name", text="ターゲット名")

        # ── pose_basis ──────────────────────────────────────
        box_pb = layout.box()
        box_pb.label(text="pose_basis 生成", icon='BONE_DATA')
        box_pb.prop(props, "target_armature", text="ターゲットArmature")

        if out_dir_abs and props.target_avatar_name.strip():
            found = resolve_avatar_data_path(out_dir_abs, props.target_avatar_name.strip())
            box_pb.label(
                text=f"{os.path.basename(found)} ✓" if found
                     else f"avatar_data_{props.target_avatar_name.strip()}.json が見つかりません",
                icon='CHECKMARK' if found else 'ERROR'
            )

        pb_ready = mochi_found and bool(
            props.target_avatar_name.strip()
            and props.target_armature
        )
        row = box_pb.row()
        row.scale_y = 1.3
        row.enabled = pb_ready
        row.operator("mochi_json.generate_pose_basis", icon='EXPORT')

        # ── posediff ────────────────────────────────────────
        box_pd = layout.box()
        box_pd.label(text="posediff 生成（pose_basis_template との差分）", icon='ARMATURE_DATA')
        box_pd.prop(props, "source_avatar_name", text="ソース名")
        box_pd.prop(props, "source_armature",    text="ソースArmature（ポーズ編集済み）")

        if out_dir_abs and props.source_avatar_name.strip():
            found_src = resolve_avatar_data_path(out_dir_abs, props.source_avatar_name.strip())
            box_pd.label(
                text=f"{os.path.basename(found_src)} ✓" if found_src
                     else f"avatar_data_{props.source_avatar_name.strip()}.json が見つかりません",
                icon='CHECKMARK' if found_src else 'ERROR'
            )

        pd_ready = mochi_found and tmpl_exists and bool(
            props.target_avatar_name.strip()
            and props.source_avatar_name.strip()
            and props.source_armature
        )
        row2 = box_pd.row()
        row2.scale_y = 1.3
        row2.enabled = pd_ready
        row2.operator("mochi_json.generate_posediff", icon='EXPORT')

        if mochi_found and not pd_ready:
            if not tmpl_exists:
                box_pd.label(text="pose_basis_template.json が必要です", icon='ERROR')
            else:
                box_pd.label(text="全項目を入力してください", icon='INFO')

        # ライセンス表記
        box_lic = layout.box()
        box_lic.label(text="License: GPL v3", icon='SCRIPT')
        box_lic.label(text="Uses MochiFitter-BlenderAddon-kai (GPL v3)")
        box_lic.label(text="Copyright (C) Mega-Gorilla")


# =========================================================
# Register
# =========================================================

classes = (
    MochiJsonProps,
    MOCHI_OT_generate_pose_basis,
    MOCHI_OT_generate_posediff,
    VIEW3D_PT_mochi_json,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mochi_json_props = (
        bpy.props.PointerProperty(type=MochiJsonProps)
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mochi_json_props


if __name__ == "__main__":
    register()

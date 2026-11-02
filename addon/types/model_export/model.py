import bpy
import time
import subprocess
import os
import threading
import concurrent.futures
import re
import shutil
from math import degrees
from shutil import move
from pathlib import Path
from traceback import print_exc

from ...utils import common
from .smd import SMD
from .fbx import export_fbx


class Model:
    def __init__(self, game, model):
        self.prefs = common.get_prefs(bpy.context)
        self.wine = Path(self.prefs.wine)
        
        sourceops = common.get_globals(bpy.context)
        if sourceops:
            self.use_addon_folder = getattr(sourceops, 'auto_use_addon_folder', True)
            self.create_material_folder = getattr(sourceops, 'auto_create_material_folder', True)
            self.create_folders_alone = getattr(sourceops, 'auto_create_folders_alone', False)
            self.overwrite_vtf = getattr(sourceops, 'auto_overwrite_vtf', True)
            self.overwrite_vmt = getattr(sourceops, 'auto_overwrite_vmt', True)
            self.max_threads = getattr(sourceops, 'auto_max_threads', 6)
            self.use_studiomdlplusplus = getattr(sourceops, 'use_studiomdlplusplus', False)
        else:
            self.use_addon_folder = False
            self.create_material_folder = True
            self.create_folders_alone = False
            self.overwrite_vtf = True
            self.overwrite_vmt = True
            self.max_threads = 6
            self.use_studiomdlplusplus = False
        
        self.model_props = model

        self.game = Path(game.game)
        self.bin = Path(game.bin)
        
        self.model_folder_items = getattr(model, 'model_folder_items', None)
        self.mod_raw = self.model_folder_items[0].name.replace('\\', '/').strip('/') if (self.model_folder_items and len(self.model_folder_items) > 0) else ''
        
        base_name = Path(model.name).with_suffix('').as_posix()
        self.stem = common.clean_filename(Path(base_name).stem)
        
        self.mod_qc_path = self.mod_raw
        while self.mod_qc_path.lower().startswith('materials/'):
            self.mod_qc_path = self.mod_qc_path[7:]
            
        if self.mod_qc_path:
            self.name = f"{self.mod_qc_path}/{base_name}"
        else:
            self.name = base_name

        if model.static and model.static_prop_combine:
            self.modelsrc = self.game.parent.parent.joinpath('content', self.game.name, 'models')
        else:
            self.modelsrc = Path(game.modelsrc)
            
        self.models = Path(game.models)
        self.mapsrc = Path(game.mapsrc)
        self.mesh_type = game.mesh_type

        directory = self.modelsrc.joinpath(self.stem)
        self.directory = common.verify_folder(directory)

        studiomdl = self.bin.joinpath('studiomdl.exe')
        quickmdl = self.bin.joinpath('quickmdl.exe')
        studiomdlplusplus = self.bin.joinpath('studiomdlplusplus.exe')
        
        if self.use_studiomdlplusplus:
            if studiomdlplusplus.is_file():
                self.studiomdl = studiomdlplusplus
            else:
                self.studiomdl = quickmdl if quickmdl.is_file() else studiomdl
        else:
            self.studiomdl = quickmdl if quickmdl.is_file() else studiomdl

        self.hlmv = self.bin.joinpath('hlmv.exe')
        self.hlmvplusplus_dir = Path(game.hlmvplusplus) if getattr(game, 'hlmvplusplus', '') else self.bin
        self.hlmvplusplus_exe = self.hlmvplusplus_dir.joinpath('hlmvplusplus.exe')

        self.material_folder_items = model.material_folder_items
        self.material_items = model.material_items
        self.skin_items = model.skin_items
        self.sequence_items = model.sequence_items
        self.attachment_items = model.attachment_items
        self.particle_items = model.particle_items

        self.armature = model.armature
        self.reference = model.reference
        self.collision = model.collision
        
        self.lod_1_collection = getattr(model, 'lod_1_collection', None)
        self.lod_1_distance = getattr(model, 'lod_1_distance', 10)
        self.lod_2_collection = getattr(model, 'lod_2_collection', None)
        self.lod_2_distance = getattr(model, 'lod_2_distance', 20)
        self.lod_3_collection = getattr(model, 'lod_3_collection', None)
        self.lod_3_distance = getattr(model, 'lod_3_distance', 30)
        self.lod_4_collection = getattr(model, 'lod_4_collection', None)
        self.lod_4_distance = getattr(model, 'lod_4_distance', 40)
        self.lod_5_collection = getattr(model, 'lod_5_collection', None)
        self.lod_5_distance = getattr(model, 'lod_5_distance', 50)
        self.lod_6_collection = getattr(model, 'lod_6_collection', None)
        self.lod_6_distance = getattr(model, 'lod_6_distance', 60)
        
        self.bodygroups = model.bodygroups
        self.stacking = model.stacking

        self.rename_material = model.rename_material
        self.surface = model.surface
        self.glass = model.glass
        self.static = model.static
        self.static_prop_combine = model.static_prop_combine
        self.joints = model.joints
        self.mass = model.mass

        self.prepend_armature = model.prepend_armature
        self.ignore_transforms = model.ignore_transforms

        self.origin_source = model.origin_source
        self.origin_object = model.origin_object

        self.origin_x = model.origin_x
        self.origin_y = model.origin_y
        self.origin_z = model.origin_z
        self.rotation = model.rotation
        self.scale = model.scale

    def _linear_to_srgb(self, c):
        if c < 0.0031308: 
            return c * 12.92
        else: 
            return 1.055 * (c ** (1.0 / 2.4)) - 0.055

    def _write_solid_tga(self, filepath, color, alpha_val):
        r = self._linear_to_srgb(color[0])
        g = self._linear_to_srgb(color[1])
        b = self._linear_to_srgb(color[2])
        
        r_b = max(0, min(255, int(round(r * 255))))
        g_b = max(0, min(255, int(round(g * 255))))
        b_b = max(0, min(255, int(round(b * 255))))
        a_b = max(0, min(255, int(round(alpha_val * 255))))

        width, height = 64, 64
        header = bytearray([0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, width & 255, (width >> 8) & 255, height & 255, (height >> 8) & 255, 32, 8])
        pixels = bytearray([b_b, g_b, r_b, a_b] * (width * height))
        
        try:
            with open(filepath, 'wb') as f:
                f.write(header)
                f.write(pixels)
            return True
        except Exception as e:
            print(f"[SourceOps ERROR] Failed to write binary TGA for solid color: {e}")
            return False

    def _get_material_texture_data(self, mat):
        if not mat or not mat.use_nodes: 
            return None, False, 1.0, 0.5, False
        
        alpha_val = 1.0
        roughness_val = 0.5
        is_alpha_linked = False
        
        principled = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)

        if principled:
            alpha_socket = principled.inputs.get('Alpha')
            if alpha_socket:
                if alpha_socket.is_linked:
                    is_alpha_linked = True
                else:
                    alpha_val = float(alpha_socket.default_value)
            
            base_col_socket = principled.inputs.get('Base Color')
            if base_col_socket and not base_col_socket.is_linked:
                if hasattr(base_col_socket, 'default_value') and len(base_col_socket.default_value) == 4:
                    alpha_val = min(alpha_val, float(base_col_socket.default_value[3]))

            rough_socket = principled.inputs.get('Roughness')
            if rough_socket and not rough_socket.is_linked:
                roughness_val = float(rough_socket.default_value)

        if hasattr(mat, 'blend_method') and mat.blend_method == 'OPAQUE':
            alpha_val = 1.0
            is_alpha_linked = False
                        
        img_node = next((n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None)
        if img_node:
            return img_node.image, False, alpha_val, roughness_val, is_alpha_linked
                
        if principled:
            base_col_socket = principled.inputs.get('Base Color')
            if base_col_socket:
                return base_col_socket.default_value, True, alpha_val, roughness_val, is_alpha_linked
                    
        return None, False, 1.0, 0.5, False

    def _get_nearest_power_of_two(self, n, max_size=4096):
        if n <= 0: return 1
        power = 1
        while power < n: power *= 2
        prev_power = power // 2
        if abs(n - prev_power) < abs(n - power): power = prev_power
        return min(power, max_size)

    def _prepare_image_for_export(self, image, max_size=4096, alpha_val=1.0):
        width, height = image.size
        new_width = self._get_nearest_power_of_two(width, max_size)
        new_height = self._get_nearest_power_of_two(height, max_size)
        
        needs_resize = (width != new_width or height != new_height)
        needs_alpha_bake = (alpha_val < 0.9995)
        
        if not needs_resize and not needs_alpha_bake:
            return image, False
            
        new_img = image.copy()
        
        if needs_resize:
            new_img.scale(new_width, new_height)
            
        if needs_alpha_bake:
            try:
                import numpy as np
                pixels = np.empty(new_width * new_height * 4, dtype=np.float32)
                new_img.pixels.foreach_get(pixels)
                pixels[3::4] *= alpha_val
                new_img.pixels.foreach_set(pixels)
            except ImportError:
                pixels = list(new_img.pixels)
                for i in range(3, len(pixels), 4):
                    pixels[i] *= alpha_val
                new_img.pixels = pixels
                
        new_img.update()
        return new_img, True

    def _save_temp_texture(self, image, output_dir, file_name):
        temp_path = os.path.join(output_dir, f"{file_name}.tga")
        scene = bpy.context.scene
        settings = scene.render.image_settings
        orig_fmt, orig_mode, orig_vt = settings.file_format, settings.color_mode, scene.view_settings.view_transform
        
        settings.file_format, settings.color_mode = 'TARGA', 'RGBA'
        scene.view_settings.view_transform = 'Standard'
        
        try: 
            image.save_render(temp_path)
        except Exception as e: 
            print(f"[SourceOps ERROR] Failed to save render texture {file_name}: {e}")
            return None
        finally:
            settings.file_format, settings.color_mode, scene.view_settings.view_transform = orig_fmt, orig_mode, orig_vt
        return temp_path
    
    def _generate_normal_map_image(self, image, scale=2.0, wrap=False):
        width, height = image.size
        try:
            import numpy as np
            pixels = np.empty(width * height * 4, dtype=np.float32)
            image.pixels.foreach_get(pixels)
            pixels = pixels.reshape((height, width, 4))
            lum = np.mean(pixels[:, :, :3], axis=2)
            
            if wrap:
                dx = np.roll(lum, -1, axis=1) - np.roll(lum, 1, axis=1)
                dy = np.roll(lum, -1, axis=0) - np.roll(lum, 1, axis=0)
            else:
                dx = np.zeros_like(lum)
                dy = np.zeros_like(lum)
                dx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
                dx[:, 0] = lum[:, 1] - lum[:, 0]
                dx[:, -1] = lum[:, -1] - lum[:, -2]
                
            dx *= scale * 0.5
            dy *= scale * 0.5
            nx = -dx
            ny = -dy
            nz = np.ones_like(lum)
            
            length = np.sqrt(nx**2 + ny**2 + nz**2)
            normal_pixels = np.empty((height, width, 4), dtype=np.float32)
            normal_pixels[:, :, 0] = nx / length * 0.5 + 0.5
            normal_pixels[:, :, 1] = ny / length * 0.5 + 0.5
            normal_pixels[:, :, 2] = nz / length * 0.5 + 0.5
            normal_pixels[:, :, 3] = 1.0
            
            flat_pixels = normal_pixels.flatten()
        except ImportError:
            flat_pixels = [0.5, 0.5, 1.0, 1.0] * (width * height)

        new_img = bpy.data.images.new(name=f"{image.name}_normal_temp", width=width, height=height, alpha=False)
        new_img.pixels.foreach_set(flat_pixels)
        new_img.update()
        return new_img

    def _process_assigned_normal(self, image, config):
        scale = getattr(config, "vtf_nscale", 2.0)
        wrap = getattr(config, "vtf_nwrap", False)
        width, height = image.size

        try:
            import numpy as np
            pixels = np.empty(width * height * 4, dtype=np.float32)
            image.pixels.foreach_get(pixels)
            pixels = pixels.reshape((height, width, 4))

            mean_r = np.mean(pixels[:, :, 0])
            mean_g = np.mean(pixels[:, :, 1])
            mean_b = np.mean(pixels[:, :, 2])
            is_tangent_normal = (mean_b > 0.55 and 0.25 < mean_r < 0.75 and 0.25 < mean_g < 0.75)

            if is_tangent_normal:
                if abs(scale - 1.0) > 0.001:
                    nx = (pixels[:, :, 0] * 2.0 - 1.0) * scale
                    ny = (pixels[:, :, 1] * 2.0 - 1.0) * scale
                    nz = (pixels[:, :, 2] * 2.0 - 1.0)
                    length = np.sqrt(nx**2 + ny**2 + nz**2)
                    length[length == 0] = 1.0
                    pixels[:, :, 0] = nx / length * 0.5 + 0.5
                    pixels[:, :, 1] = ny / length * 0.5 + 0.5
                    pixels[:, :, 2] = nz / length * 0.5 + 0.5

                flat_pixels = pixels.flatten()
                new_img = bpy.data.images.new(name=f"{image.name}_norm_proc", width=width, height=height, alpha=False)
                new_img.pixels.foreach_set(flat_pixels)
                new_img.update()
                return new_img, True
            else:
                return self._generate_normal_map_image(image, scale=scale, wrap=wrap), True
        except Exception:
            return image.copy(), True
        
    def _convert_to_vtf(self, tga_path, vtf_path, config, is_normal):
        try:
            from ...PyVTFlib import ops as pyvtf_ops, VTFConvertOptions, IMAGE_FORMAT, VTF_FLAG, VTFResizeOptions, RESIZE_METHOD, RESIZE_FILTER, MODE, VERSION
            
            fmt_str = getattr(config, "vtf_format", "DXT5")
            try: 
                fmt_enum = IMAGE_FORMAT[fmt_str]
            except KeyError: 
                fmt_enum = IMAGE_FORMAT.DXT5
                
            flag_mapping = {
                "POINTSAMPLE": "POINT_SAMPLE", "TRILINEAR": "TRILINEAR", "CLAMPS": "CLAMP_S",
                "CLAMPT": "CLAMP_T", "ANISOTROPIC": "ANISOTROPIC", "NORMAL": "NORMAL",
                "NOLOD": "NO_LOD", "MINMIP": "LOAD_SMALL_MIPS", "PROCEDURAL": "PROCEDURAL", "RENDERTARGET": "RENDERTARGET",
                "DEPTHRENDERTARGET": "DEPTH_RENDERTARGET", "NODEBUGOVERRIDE": "NO_DEBUG_OVERRIDE",
                "SINGLECOPY": "SINGLE_COPY", "NODEPTHBUFFER": "NO_DEPTH_BUFFER", "CLAMPU": "CLAMP_U",
                "VERTEXTEXTURE": "VERTEX_TEXTURE", "SSBUMP": "SSBUMP", "BORDER": "BORDER",
            }
            
            vtf_flags = []
            for f_prop, f_enum in flag_mapping.items():
                if f_enum and getattr(config, f"vtf_flag_{f_prop}", False):
                    vtf_flags.append(VTF_FLAG[f_enum])
            
            resize_options = None
            if getattr(config, "vtf_resize", False):
                try: 
                    r_method = RESIZE_METHOD[getattr(config, "vtf_rmethod", "NEAREST")]
                except KeyError: 
                    r_method = RESIZE_METHOD.NEAREST
                w = getattr(config, "vtf_rwidth", 0)
                h = getattr(config, "vtf_rheight", 0)
                resize_options = VTFResizeOptions(
                    WIDTH=w if w > 0 else None,
                    HEIGHT=h if h > 0 else None,
                    method=r_method
                )

            if is_normal and VTF_FLAG.NORMAL not in vtf_flags:
                vtf_flags.append(VTF_FLAG.NORMAL)
                    
            try: 
                filter_enum = RESIZE_FILTER[getattr(config, "vtf_mfilter", "DEFAULT")]
            except KeyError: 
                filter_enum = RESIZE_FILTER.DEFAULT
                
            disable_mips = getattr(config, "vtf_nomipmaps", False) or getattr(config, "vtf_flag_NOMIP", False)
            
            options = VTFConvertOptions(
                input_path=Path(tga_path),
                output_path=Path(vtf_path),
                MODE=MODE.CONVERT,
                format=fmt_enum,
                vtf_flags=vtf_flags,
                filter=filter_enum,
                resize=resize_options,
                normal=None,
                disable_mips=disable_mips,
                version=VERSION.V7_4
            )
            vtf_ops = pyvtf_ops()
            vtf_ops.convert(options)
            
            if os.path.exists(vtf_path):
                return True
            else:
                return False
                
        except Exception as e:
            print(f"[SourceOps ERROR] PyVTFlib MareTF execution failed exception: {e}")
            return False

    def _process_vtf_tasks(self, tga_path, vtf_path, tga_normal_path, vtf_normal_path, config, generate_normal, addon_dir, mat_clean):
        if tga_path:
            success_base = self._convert_to_vtf(tga_path, vtf_path, config, False)
            if success_base and addon_dir:
                try: 
                    shutil.copy2(vtf_path, os.path.join(addon_dir, f"{mat_clean}.vtf"))
                except Exception as e: 
                    pass
            try: 
                os.remove(tga_path)
            except: 
                pass
                
        if generate_normal and tga_normal_path:
            success_norm = self._convert_to_vtf(tga_normal_path, vtf_normal_path, config, True)
            if success_norm and addon_dir:
                try: 
                    shutil.copy2(vtf_normal_path, os.path.join(addon_dir, f"{mat_clean}_normalmap.vtf"))
                except Exception as e: 
                    pass
            try: 
                os.remove(tga_normal_path)
            except: 
                pass

    def _cleanup_image(self, image):
        try:
            if image and image.name in bpy.data.images: 
                bpy.data.images.remove(image)
        except: 
            pass

    def export_materials_func(self, use_addon_folder, global_processed_materials_clean=None):
        print(f"\n[SourceOps] ========================================")
        print(f"[SourceOps] STARTING MATERIAL EXPORT FOR: {self.name}")
        print(f"[SourceOps] ========================================")

        addon_name = self.stem
        mat_raw = self.material_folder_items[0].name.replace('\\', '/').strip('/') if self.material_folder_items else ''
        
        mat_qc_path = mat_raw
        while mat_qc_path.lower().startswith('materials/'):
            mat_qc_path = mat_qc_path[10:]
            
        if self.models.name.lower() == 'models':
            out_root = self.models.parent
        else:
            out_root = self.models
        
        if getattr(self, 'create_folders_alone', False):
            target_dir = out_root.joinpath('materials', mat_qc_path)
        elif self.create_material_folder:
            if use_addon_folder:
                target_dir = out_root.joinpath(addon_name, 'materials', mat_qc_path)
            else:
                target_dir = out_root.joinpath('materials', mat_qc_path)
        else:
            if use_addon_folder:
                target_dir = out_root.joinpath(addon_name, mat_raw)
            else:
                target_dir = out_root.joinpath(mat_raw)
                
        target_dir.mkdir(parents=True, exist_ok=True)
        addon_dir = None
        
        objects = set()
        if self.reference: 
            objects.update(self.get_all_objects(self.reference))
        
        if self.bodygroups:
            for bg in self.bodygroups.children:
                for col in bg.children: 
                    objects.update(self.get_all_objects(col))
        
        if global_processed_materials_clean is None:
            global_processed_materials_clean = set()

        print(f"[SourceOps] Found {len(objects)} valid mesh objects to scan for materials.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=getattr(self, 'max_threads', 6)) as executor:
            for obj in objects:
                if obj.type != 'MESH': 
                    continue
                for mat in obj.data.materials:
                    if not mat: 
                        continue
                    
                    mat_clean = re.sub(r'\.\d{3}$', '', mat.name).replace(" ", "_")
                    mat_clean = re.sub(r'[\\/*?:"<>|]', "", mat_clean)
                    
                    cache_key = (mat_clean, str(target_dir))
                    if cache_key in global_processed_materials_clean: 
                        continue
                    global_processed_materials_clean.add(cache_key)
                    
                    print(f"\n[SourceOps] Processing Material: '{mat.name}' -> Output Name: '{mat_clean}'")
                    
                    vmt_path = target_dir.joinpath(f"{mat_clean}.vmt")
                    vtf_path = target_dir.joinpath(f"{mat_clean}.vtf")
                    vtf_normal_path = target_dir.joinpath(f"{mat_clean}_normalmap.vtf")
                    
                    mat_config = next((m for m in self.material_items if m.name == mat_clean), None)
                    config = mat_config if mat_config else self.model_props
                    
                    assigned_norm = getattr(config, "normal_map", "").strip()
                    generate_normal = getattr(config, "vtf_normal_map", False)
                    has_normal = generate_normal or bool(assigned_norm)

                    used_global_text = False
                    existing_text = None
                    
                    if mat_config:
                        text_name = f"VMT_{mat_clean}.vmt"
                        existing_text = bpy.data.texts.get(text_name)
                    else:
                        global_text_name = f"VMT_GLOBAL_{self.stem}.vmt"
                        existing_text = bpy.data.texts.get(global_text_name)
                        if not existing_text:
                            existing_text = bpy.data.texts.get("VMT_GLOBAL_SETTINGS.vmt")
                        if existing_text:
                            used_global_text = True
                    
                    img_or_color, is_gen, alpha_val, roughness_val, is_alpha_linked = self._get_material_texture_data(mat)
                    
                    vmt_needs_update = self.overwrite_vmt or not vmt_path.is_file()
                    
                    if vmt_needs_update:
                        do_not_sort = getattr(config, "do_not_sort_vmts", False) or getattr(self.model_props, "do_not_sort_vmts", False)
                        basetexture_path = f"{mat_qc_path}/{mat_clean}" if mat_qc_path else mat_clean
                        surface_prop = self.surface if hasattr(self, 'surface') else getattr(self.model_props, 'surface', 'default')
                        shader = getattr(config, "vmt_shader", "VertexLitGeneric")
                        
                        # -------------------------------------------------------------
                        # 1. TRUE MANUAL OVERRIDE (DO NOT SORT VMTS)
                        # -------------------------------------------------------------
                        if do_not_sort:
                            raw_lines = []
                            if existing_text and len(existing_text.lines) > 0:
                                raw_lines = [line.body for line in existing_text.lines]
                            elif vmt_path.is_file():
                                try:
                                    with open(vmt_path, 'r') as f:
                                        lines = f.read().splitlines()
                                    is_disk_global = False
                                    for line in reversed(lines):
                                        if line.strip().startswith("// [SourceOps_State]"):
                                            state_str_old = line.split("// [SourceOps_State]")[1].strip()
                                            for pair in state_str_old.split("|"):
                                                if ":" in pair and pair.split(":")[0] == "is_global":
                                                    is_disk_global = (pair.split(":")[1] == "1")
                                            break
                                    if not used_global_text and is_disk_global:
                                        lines = []
                                    raw_lines = [l for l in lines if not l.strip().startswith("// [SourceOps_State]")]
                                except:
                                    pass
                                    
                            if not raw_lines:
                                raw_lines = [
                                    f'"{shader}"',
                                    '{',
                                    f'    "$basetexture" "{basetexture_path}"',
                                    f'    "$surfaceprop" "{surface_prop}"',
                                    '}'
                                ]
                            else:
                                if used_global_text:
                                    new_raw = []
                                    for l in raw_lines:
                                        if "DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY" in l:
                                            continue
                                        if "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)" in l:
                                            l = l.replace('"(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)"', f'"{basetexture_path}"')
                                            l = l.replace("(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)", basetexture_path)
                                        new_raw.append(l)
                                    raw_lines = new_raw
                                    
                            final_lines = raw_lines
                            raw_content = "\n".join(final_lines)
                            if not raw_content.endswith('\n'):
                                raw_content += '\n'
                                
                            try:
                                with open(vmt_path, 'w') as f:
                                    f.write(raw_content)
                            except Exception as e:
                                print(f"[SourceOps ERROR] Could not write VMT: {e}")

                        # -------------------------------------------------------------
                        # 2. NORMAL EXPORT (ALWAYS USES LIVE UI SETTINGS & COLORS)
                        # -------------------------------------------------------------
                        else:
                            lines_to_parse = []
                            if existing_text and len(existing_text.lines) > 0:
                                lines_to_parse = [line.body for line in existing_text.lines]
                            elif vmt_path.is_file():
                                try:
                                    with open(vmt_path, 'r') as f:
                                        lines_to_parse = f.read().splitlines()
                                except:
                                    pass
                                    
                            lines_to_parse = [l for l in lines_to_parse if not l.strip().startswith("// [SourceOps_State]")]
                            custom_lines = []
                            controlled_keys = [
                                "$basetexture", "$bumpmap", "$surfaceprop", "$model", "$translucent", "$alphatest", "$nocull",
                                "$envmap", "$envmaptint", "$envmapfresnel", "$normalmapalphaenvmapmask", "$basealphaenvmapmask",
                                "$phong", "$phongboost", "$phongexponent", "$phongtint", "$phongalbedotint",
                                "$phongfresnelranges", "$basemapalphaphongmask", "$reflectivity", "$envmapblur"
                            ]

                            if lines_to_parse:
                                for raw_line in lines_to_parse:
                                    stripped = raw_line.strip()
                                    if not stripped: continue
                                    if "DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY" in stripped: continue
                                    lower_line = stripped.lower().replace('"', '')
                                    if lower_line in ["vertexlitgeneric", "unlitgeneric", "lightmappedgeneric"]: continue
                                    if lower_line in ["vertexlitgeneric {", "unlitgeneric {", "lightmappedgeneric {"]: continue
                                    if stripped in ("{", "}"): continue

                                    is_controlled = any(stripped.lower().startswith(c_key) or stripped.lower().startswith(f'"{c_key}"') for c_key in controlled_keys)
                                    if not is_controlled:
                                        custom_lines.append(raw_line.rstrip('\n'))

                            vmt_lines = [f'"{shader}"', '{']
                            if used_global_text:
                                vmt_lines.append('    // (DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY, WILL BE REPLACED PER-MATERIAL ON EXPORT)')

                            vmt_lines.append(f'    "$basetexture" "{basetexture_path}"')
                            
                            bump_active = (has_normal or getattr(config, "vmt_phong", False))
                            if has_normal:
                                bump_val = f"{basetexture_path}_normalmap"
                            else:
                                bump_val = "dev/flat_normal"
                                
                            if bump_active:
                                vmt_lines.append(f'    "$bumpmap" "{bump_val}"')
                                
                            vmt_lines.append(f'    "$surfaceprop" "{surface_prop}"')
                            vmt_lines.append('    "$model" 1')

                            if getattr(config, "vmt_translucent", False): vmt_lines.append('    "$translucent" 1')
                            if getattr(config, "vmt_alphatest", False): vmt_lines.append('    "$alphatest" 1')
                            if getattr(config, "vmt_nocull", False): vmt_lines.append('    "$nocull" 1')

                            if getattr(config, "vmt_phong", False):
                                vmt_lines.append('    "$phong" "1"')
                                vmt_lines.append(f'    "$phongboost" "{getattr(config, "vmt_phongboost", 1.0):.2f}"')
                                vmt_lines.append(f'    "$phongexponent" "{getattr(config, "vmt_phongexponent", 25)}"')
                                vmt_lines.append(f'    "$phongfresnelranges" "{getattr(config, "vmt_phongfresnelranges", "[0.05 0.5 1]")}"')
                                if getattr(config, "vmt_phongalbedotint", False):
                                    vmt_lines.append('    "$phongalbedotint" "1"')
                                else:
                                    pt = getattr(config, "vmt_phongtint", (1.0, 1.0, 1.0))
                                    if not (abs(pt[0] - 1.0) < 0.01 and abs(pt[1] - 1.0) < 0.01 and abs(pt[2] - 1.0) < 0.01):
                                        vmt_lines.append(f'    "$phongtint" "[{pt[0]:.2f} {pt[1]:.2f} {pt[2]:.2f}]"')
                                if getattr(config, "vmt_phongmask_source", "NORMAL_ALPHA") == "BASE_ALPHA":
                                    vmt_lines.append('    "$basemapalphaphongmask" "1"')

                            if getattr(config, "vmt_envmap", False):
                                vmt_lines.append('    "$envmap" "env_cubemap"')
                                et = getattr(config, "vmt_envmaptint", (0.3, 0.3, 0.3))
                                vmt_lines.append(f'    "$envmaptint" "[{et[0]:.2f} {et[1]:.2f} {et[2]:.2f}]"')
                                if getattr(config, "vmt_envmapfresnel", False):
                                    vmt_lines.append('    "$envmapfresnel" "1"')
                                mask_src = getattr(config, "vmt_envmapmask_source", "NORMAL_ALPHA")
                                if mask_src == "NORMAL_ALPHA" and bump_active:
                                    vmt_lines.append('    "$normalmapalphaenvmapmask" 1')
                                elif mask_src == "BASE_ALPHA":
                                    vmt_lines.append('    "$basealphaenvmapmask" 1')

                            if custom_lines:
                                vmt_lines.append('')
                                for cl in custom_lines:
                                    vmt_lines.append(cl)

                            vmt_lines.append('}')
                            vmt_content_final = "\n".join(vmt_lines) + "\n"
                            
                            try:
                                with open(vmt_path, 'w') as f: 
                                    f.write(vmt_content_final)
                            except Exception as e: 
                                print(f"[SourceOps ERROR] Failed to write VMT: {e}")

                    vtf_needs_update = self.overwrite_vtf or not vtf_path.is_file()
                    if has_normal and not vtf_normal_path.is_file():
                        vtf_needs_update = True
                        
                    if not vtf_needs_update:
                        continue 

                    if img_or_color:
                        tga_path = None
                        tga_normal_path = None
                        
                        if is_gen:
                            tga_path = str(target_dir.joinpath(f"{mat_clean}.tga"))
                            if not self._write_solid_tga(tga_path, img_or_color, alpha_val):
                                tga_path = None
                                
                            if has_normal:
                                tga_normal_path = str(target_dir.joinpath(f"{mat_clean}_normalmap.tga"))
                                self._write_solid_tga(tga_normal_path, [0.5, 0.5, 1.0], 1.0)
                        else:
                            bake_alpha = alpha_val if not is_gen else 1.0
                            final_img, was_modified = self._prepare_image_for_export(img_or_color, max_size=4096, alpha_val=bake_alpha)
                            
                            tga_path = self._save_temp_texture(final_img, str(target_dir), mat_clean)
                            
                            assigned_norm = getattr(config, "normal_map", "").strip()
                            if generate_normal:
                                nmap_img = self._generate_normal_map_image(final_img, scale=getattr(config, "vtf_nscale", 2.0), wrap=getattr(config, "vtf_nwrap", False))
                                if nmap_img:
                                    tga_normal_path = self._save_temp_texture(nmap_img, str(target_dir), f"{mat_clean}_normalmap")
                                    self._cleanup_image(nmap_img)
                            elif assigned_norm:
                                norm_img = bpy.data.images.get(assigned_norm)
                                if not norm_img:
                                    m_found = bpy.data.materials.get(assigned_norm)
                                    if m_found:
                                        norm_img, _, _, _, _ = self._get_material_texture_data(m_found)
                                if not norm_img:
                                    for im in bpy.data.images:
                                        if Path(im.name).stem == Path(assigned_norm).stem:
                                            norm_img = im
                                            break
                                if norm_img:
                                    proc_img, was_proc = self._process_assigned_normal(norm_img, config)
                                    final_norm_img, was_norm_modified = self._prepare_image_for_export(proc_img, max_size=4096)
                                    tga_normal_path = self._save_temp_texture(final_norm_img, str(target_dir), f"{mat_clean}_normalmap")
                                    if was_norm_modified:
                                        self._cleanup_image(final_norm_img)
                                    if was_proc:
                                        self._cleanup_image(proc_img)
                                else:
                                    nmap_img = self._generate_normal_map_image(final_img, scale=getattr(config, "vtf_nscale", 2.0), wrap=getattr(config, "vtf_nwrap", False))
                                    if nmap_img:
                                        tga_normal_path = self._save_temp_texture(nmap_img, str(target_dir), f"{mat_clean}_normalmap")
                                        self._cleanup_image(nmap_img)

                            if was_modified: 
                                self._cleanup_image(final_img)

                        if tga_path or tga_normal_path:
                            executor.submit(
                                self._process_vtf_tasks, 
                                tga_path, str(vtf_path), 
                                tga_normal_path, str(vtf_normal_path), 
                                config, has_normal, 
                                str(addon_dir) if addon_dir else None, mat_clean
                            )

        print(f"[SourceOps] ========================================")
        print(f"[SourceOps] COMPLETED MATERIAL EXPORT FOR: {self.name}")
        print(f"[SourceOps] ========================================\n")

    def export_meshes(self):
        print(f"\n[SourceOps] Starting Mesh Export...")
        self.ensure_modelsrc_folder()

        if not self.sequence_items:
            self.export_anim(self.armature, None, self.directory.joinpath('anims', 'idle.SMD'))

        for sequence in self.sequence_items:
            path = self.directory.joinpath('anims', f'{common.clean_filename(sequence.name)}.SMD')
            self.export_anim(self.armature, sequence.action, path)

        if self.reference:
            objects = self.get_all_objects(self.reference)
            path = self.get_body_path(self.reference)
            self.export_mesh(self.armature, objects, path)

        if self.collision:
            objects = self.get_all_objects(self.collision)
            path = self.get_body_path(self.collision)
            self.export_mesh(self.armature, objects, path)

        lods = [
            self.lod_1_collection, self.lod_2_collection, self.lod_3_collection, 
            self.lod_4_collection, self.lod_5_collection, self.lod_6_collection
        ]
        
        for lod_col in lods:
            if lod_col:
                objects = self.get_all_objects(lod_col)
                path = self.get_body_path(lod_col)
                self.export_mesh(self.armature, objects, path)

        if self.bodygroups:
            for bodygroup in self.bodygroups.children:
                for collection in bodygroup.children:
                    objects = self.get_all_objects(collection)
                    path = self.get_body_path(collection)
                    self.export_mesh(self.armature, objects, path)

        if self.stacking:
            for collection in self.stacking.children:
                objects = self.get_all_objects(collection)
                path = self.get_body_path(collection)
                self.export_mesh(self.armature, objects, path)
                
        print(f"[SourceOps] Mesh Export Completed.\n")

    def export_anim(self, armature, action, path):
        self.export_smd(armature, [], action, path)

    def export_mesh(self, armature, objects, path):
        if self.mesh_type == 'SMD':
            self.export_smd(armature, objects, None, path)
        elif self.mesh_type == 'FBX':
            self.export_fbx(armature, objects, path)

    def export_smd(self, armature, objects, action, path):
        try:
            smd_file = path.open('w')
        except:
            self.report(f'Failed to export: {path}', exception=True)
        else:
            smd = SMD(self.prepend_armature, self.ignore_transforms)
            smd.from_blender(armature, objects, action)
            smd_file.write(smd.to_string())
            smd_file.close()

    def export_fbx(self, armature, objects, path):
        try:
            export_fbx(path, armature, objects, self.prepend_armature, self.ignore_transforms)
        except:
            self.report(f'Failed to export: {path}', exception=True)

    def get_all_objects(self, collection):
        if not collection: return []
        valid_objects = [obj for obj in collection.all_objects if obj.name in bpy.context.view_layer.objects]
        return common.remove_duplicates(valid_objects)

    def get_body_path(self, collection):
        name = common.clean_filename(collection.name)
        return self.directory.joinpath(f'{name}.{self.mesh_type}')

    def generate_qc(self):
        if not self.reference and not self.stacking:
            return self.report(f'Unable to generate QC for: {self.name} (reference and stacking both not set)')

        if not self.armature and not self.static:
            self.static = True

        self.ensure_modelsrc_folder()
        path = self.directory.joinpath(f'{self.stem}.qc')

        try:
            qc = path.open('w')
        except:
            return self.report(f'Failed to open: {path}', exception=True)

        qc.write(f'$modelname "{self.name}.mdl"\n\n')

        if not self.material_folder_items:
            qc.write('$cdmaterials ""\n\n')
        else:
            for material_folder in self.material_folder_items:
                folder_name = material_folder.name.replace('\\', '/').strip('/')
                
                while folder_name.lower().startswith('materials/'):
                    folder_name = folder_name[10:]
                    
                if folder_name:
                    qc.write(f'$cdmaterials "{folder_name}/"\n')
                else:
                    qc.write('$cdmaterials ""\n')
            qc.write('\n')

        qc.write(f'$surfaceprop "{self.surface}"\n')

        if self.glass:
            qc.write('\n$mostlyopaque\n')

        if self.static:
            qc.write('\n$staticprop\n')

        if self.origin_source == 'MANUAL':
            origin_x = self.origin_x
            origin_y = self.origin_y
            origin_z = self.origin_z
            rotation = -self.rotation
        elif self.origin_source == 'OBJECT' and self.origin_object:
            loc, rot, _ = self.origin_object.matrix_world.decompose()
            origin_x = loc.x
            origin_y = loc.y
            origin_z = loc.z
            rotation = -degrees(rot.to_euler().z)
        else:
            origin_x = 0
            origin_y = 0
            origin_z = 0
            rotation = 0

        if self.static and self.mesh_type == 'FBX':
            origin_x, origin_y = -origin_y, origin_x
            rotation -= 180
        else:
            rotation -= 90

        if not (self.static and self.static_prop_combine):
            qc.write(f'\n$origin {origin_x:.6f} {origin_y:.6f} {origin_z:.6f} {rotation:.6f}\n')

        qc.write(f'\n$scale {self.scale:.6f}\n')

        if self.reference:
            name = common.clean_filename(self.reference.name)
            qc.write(f'\n$body "{name}" "{name}.{self.mesh_type}"\n')

        lods = [
            (self.lod_1_distance, self.lod_1_collection),
            (self.lod_2_distance, self.lod_2_collection),
            (self.lod_3_distance, self.lod_3_collection),
            (self.lod_4_distance, self.lod_4_collection),
            (self.lod_5_distance, self.lod_5_collection),
            (self.lod_6_distance, self.lod_6_collection),
        ]
        has_lods = any([col for dist, col in lods])

        if self.reference and has_lods:
            qc.write('\n// --- LOD SECTION ---\n')
            for dist, lod_col in lods:
                if lod_col and len(self.get_all_objects(lod_col)) > 0:
                    qc.write(f'$lod {dist}\n')
                    qc.write('{\n')
                    ref_name = common.clean_filename(self.reference.name)
                    lod_name = common.clean_filename(lod_col.name)
                    qc.write(f'    replacemodel "{ref_name}.{self.mesh_type}" "{lod_name}.{self.mesh_type}"\n')
                    qc.write('}\n')
            qc.write('// -------------------\n')

        if not self.rename_material == '':
            qc.write(f'\n$renamematerial {self.rename_material}\n')

        if self.collision:
            name = common.clean_filename(self.collision.name)
            command = 'collisionjoints' if self.joints else 'collisionmodel'
            qc.write(f'\n${command} "{name}.{self.mesh_type}" {{\n')
            command = 'concaveperjoint' if self.joints else 'concave'
            qc.write(f'    ${command}\n')
            command = f'mass {self.mass}' if self.mass > 0 else 'automass'
            qc.write(f'    ${command}\n')
            qc.write('    $maxconvexpieces 10000\n')
            qc.write('}\n')

        if self.bodygroups:
            for bodygroup in self.bodygroups.children:
                bodygroup_name = common.clean_filename(bodygroup.name)
                qc.write(f'\n$bodygroup "{bodygroup_name}" {{\n')
                for collection in bodygroup.children:
                    name = common.clean_filename(collection.name)
                    if len(self.get_all_objects(collection)) > 0:
                        qc.write(f'    studio "{name}.{self.mesh_type}"\n')
                    else:
                        qc.write(f'    blank\n')
                qc.write('}\n')

        if self.stacking:
            for collection in self.stacking.children:
                if len(self.get_all_objects(collection)) > 0:
                    name = common.clean_filename(collection.name)
                    qc.write(f'\n$model "{name}" "{name}.{self.mesh_type}"\n')

        if not self.sequence_items:
            qc.write('\n$sequence "idle" "anims/idle.SMD"\n')

        for sequence in self.sequence_items:
            qc.write(f'\n$sequence "{sequence.name}" {{\n')
            qc.write(f'    "anims/{common.clean_filename(sequence.name)}.SMD"\n')
            if sequence.use_framerate:
                qc.write(f'    fps {sequence.framerate}\n')
            else:
                qc.write(f'    fps {bpy.context.scene.render.fps}\n')
            if sequence.use_range:
                qc.write(f'    frames {sequence.start} {sequence.end}\n')
            if sequence.snap:
                qc.write('    snap\n')
            if sequence.loop:
                qc.write('    loop\n')
            qc.write(f'    activity "{sequence.activity}" {sequence.weight}\n')
            for event in sequence.event_items:
                qc.write(f'    {{ event "{event.event}" {event.frame} "{event.value}" }}\n')
            qc.write('}\n')

        for attachment in self.attachment_items:
            if self.armature and attachment.bone:
                bone_name = f"{self.armature.name}.{attachment.bone}" if self.prepend_armature else attachment.bone
                qc.write(f'\n$attachment "{attachment.name}" "{bone_name}" {attachment.offset[0]} {attachment.offset[1]} {attachment.offset[2]}')
                
                if attachment.absolute:
                    qc.write(' absolute')
                if attachment.rigid:
                    qc.write(' rigid')
                qc.write(f' rotate {attachment.rotation[0]} {attachment.rotation[1]} {attachment.rotation[2]}\n')

        if self.skin_items:
            qc.write('\n$texturegroup "skinfamilies"\n')
            qc.write('{\n')

            for skin in self.skin_items:
                skin_str = f'"{skin.name}"'
                linked_mats = getattr(skin, "linked_materials", "").strip()
                if linked_mats:
                    for l_mat in linked_mats.split():
                        if l_mat:
                            skin_str += f' "{l_mat}"'
                qc.write(f'    {{ {skin_str} }}\n')

            qc.write('}\n')
        
        if len(self.particle_items) > 0:
            qc.write('\n$keyvalues\n')
            qc.write('{\n')
            qc.write('    particles\n')
            qc.write('    {\n')
            
            for index, particle in enumerate(self.particle_items):
                qc.write(f'        "effect{index}"\n')
                qc.write('        {\n')
                qc.write(f'            "name" "{particle.name}"\n')
                qc.write(f'            "attachment_type" "{particle.attachment_type}"\n')
                if particle.attachment_point:
                    qc.write(f'            "attachment_point" "{particle.attachment_point}"\n')
                qc.write('        }\n')
            
            qc.write('    }\n')
            qc.write('}\n')
        
        qc.close()

    def compile_qc(self):
        qc = self.directory.joinpath(f'{self.stem}.qc')
        if qc.is_file():
            self.ensure_models_folder()
            self.remove_models_old()

            is_plusplus = self.studiomdl.name.lower() == 'studiomdlplusplus.exe'
            env_vars = None

            if (os.name == 'posix'):
                cwd = self.game.parent
                wine_exe = str(self.wine) if str(self.wine) and str(self.wine) != '.' else 'wine'
                args = [wine_exe, str(self.studiomdl.relative_to(cwd)), '-nop4', '-fullcollide',
                        '-game', str(self.game.relative_to(cwd)), str(qc.relative_to(cwd))]
            else:
                if is_plusplus:
                    cwd = str(self.bin)
                    env_vars = os.environ.copy()
                    env_vars['VPROJECT'] = str(self.game)
                else:
                    cwd = None
                    
                args = [str(self.studiomdl), '-nop4', '-fullcollide', '-game', str(self.game), str(qc)]

            try:
                if env_vars:
                    pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, env=env_vars, universal_newlines=True)
                else:
                    pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, universal_newlines=True)

                log_output = []
                for line in pipe.stdout:
                    print(line, end='')
                    log_output.append(line)

                pipe.wait()
                code = pipe.returncode
                
                log_file = self.directory.joinpath(f'{self.stem}.log')
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.writelines(log_output)
                
                if code == 3221225785 or code == -1073741511:
                    error_msg = f"CRITICAL DLL CRASH: {self.studiomdl.name} crashed instantly! It is incompatible with the .dll files in your bin folder."
                    return error_msg
                elif code == 3221225781 or code == -1073741515:
                    error_msg = f"CRITICAL DLL CRASH: {self.studiomdl.name} crashed instantly! It is missing required .dll files."
                    return error_msg
                elif code == 4294967295 or code == -1:
                    error_msg = f"FATAL ERROR (-1): {self.studiomdl.name} crashed. This usually means your Game Path or Bin Path in the Games Panel is invalid."
                    return error_msg

            except Exception as e:
                return f"Compiler exception: {e}"

            if code == 0:
                self.move_files()
            else:
                return f'Failed to compile (Code {code}): {qc.name}. Check Blender Console for details.'
        else:
            return f'Unable to find: {qc}'

    def open_folder(self):
        try:
            bpy.ops.wm.path_open(filepath=str(self.directory))
        except:
            return self.report(f'Failed to open: {self.directory}', exception=True)

    def view_model(self):
        addon_name = self.stem
        
        if self.models.name.lower() == 'models':
            out_root = self.models.parent
        else:
            out_root = self.models
            
        if getattr(self, 'create_folders_alone', False):
            model = out_root.joinpath('models', self.name)
        elif self.use_addon_folder:
            model = out_root.joinpath(addon_name, 'models', self.name)
        else:
            model = self.models.joinpath(self.name)
            
        mdl = model.with_suffix('.mdl')
        dx90 = model.with_suffix('.dx90.vtx')

        if os.name == 'posix':
            cwd = self.game.parent
            wine_exe = str(self.wine) if str(self.wine) and str(self.wine) != '.' else 'wine'
            args = [wine_exe, str(self.hlmv.relative_to(cwd)), '-game',
                    str(self.game.relative_to(cwd)), str(mdl.relative_to(cwd))]
        else:
            cwd = None
            args = [str(self.hlmv), '-game', str(self.game), str(mdl)]

        if dx90.is_file():
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        else:
            return self.report(f'Failed to view: {mdl}')

    def view_model_plusplus(self):
        addon_name = self.stem
        
        if self.models.name.lower() == 'models':
            out_root = self.models.parent
        else:
            out_root = self.models
            
        if getattr(self, 'create_folders_alone', False):
            model = out_root.joinpath('models', self.name)
        elif self.use_addon_folder:
            model = out_root.joinpath(addon_name, 'models', self.name)
        else:
            model = self.models.joinpath(self.name)
            
        mdl = model.with_suffix('.mdl')
        dx90 = model.with_suffix('.dx90.vtx')

        if not self.hlmvplusplus_exe.is_file():
            return self.report(f"Failed to find hlmvplusplus.exe in {self.hlmvplusplus_dir}")

        if os.name == 'posix':
            cwd = self.game.parent
            wine_exe = str(self.wine) if str(self.wine) and str(self.wine) != '.' else 'wine'
            args = [wine_exe, str(self.hlmvplusplus_exe.relative_to(cwd)), '-game',
                    str(self.game.relative_to(cwd)), str(mdl.relative_to(cwd))]
        else:
            cwd = str(self.hlmvplusplus_dir)
            args = [str(self.hlmvplusplus_exe), '-game', str(self.game), str(mdl)]

        if dx90.is_file():
            subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        else:
            return self.report(f'Failed to view: {mdl}')

    def move_files(self):
        path_src = self.game.joinpath('models', self.name)
        addon_name = self.stem
        
        if self.models.name.lower() == 'models':
            out_root = self.models.parent
        else:
            out_root = self.models

        if getattr(self, 'create_folders_alone', False):
            path_dst = out_root.joinpath('models', self.name)
        elif self.use_addon_folder:
            path_dst = out_root.joinpath(addon_name, 'models', self.name)
        else:
            path_dst = self.models.joinpath(self.name)

        if path_src == path_dst:
            return

        common.verify_folder(path_dst.parent)

        for suffix in ('.dx90.vtx', '.dx80.vtx', '.sw.vtx', '.vvd', '.mdl', '.phy'):
            src = path_src.with_suffix(suffix)
            dst = path_dst.with_suffix(suffix)

            if src.is_file():
                if dst.is_file():
                    try: 
                        dst.unlink()
                    except Exception as e: 
                        pass
                try: 
                    move(src, dst)
                except Exception as e: 
                    pass

    def ensure_modelsrc_folder(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        self.directory.joinpath('anims').mkdir(parents=True, exist_ok=True)

    def remove_modelsrc_old(self):
        for file in self.directory.rglob('*'):
            if file.suffix in ('.SMD', '.FBX'):
                if file.is_file():
                    file.unlink()

    def ensure_models_folder(self):
        addon_name = self.stem
        if self.models.name.lower() == 'models':
            out_root = self.models.parent
        else:
            out_root = self.models
            
        if getattr(self, 'create_folders_alone', False):
            path_dst = out_root.joinpath('models', self.name)
        elif self.use_addon_folder:
            path_dst = out_root.joinpath(addon_name, 'models', self.name)
        else:
            path_dst = self.models.joinpath(self.name)
            
        path_dst.parent.mkdir(parents=True, exist_ok=True)

    def remove_models_old(self):
        addon_name = self.stem
        if self.models.name.lower() == 'models':
            out_root = self.models.parent
        else:
            out_root = self.models
            
        if getattr(self, 'create_folders_alone', False):
            path_dst = out_root.joinpath('models', self.name)
        elif self.use_addon_folder:
            path_dst = out_root.joinpath(addon_name, 'models', self.name)
        else:
            path_dst = self.models.joinpath(self.name)
            
        for suffix in ('.dx90.vtx', '.dx80.vtx', '.sw.vtx', '.vvd', '.mdl', '.phy'):
            path = path_dst.with_suffix(suffix)
            if path.is_file(): 
                try: 
                    path.unlink()
                except Exception as e: 
                    pass

    def report(self, message, exception=False):
        if exception: 
            print_exc()
        return message
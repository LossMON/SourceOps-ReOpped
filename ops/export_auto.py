import bpy
import time
import concurrent.futures
from threading import Lock
from .. import utils
from .. types . model_export . model import Model


class SOURCEOPS_OT_ExportAuto(bpy.types.Operator):
    bl_idname = 'sourceops.export_auto'
    bl_options = {'REGISTER'}
    bl_label = 'Export Auto'
    bl_description = 'Export checked models, generate QCs, compile MDLs.\nCtrl click to customize export steps'

    def draw(self, context):
        layout = self.layout
        sourceops = context.scene.sourceops
        col = layout.column()
        
        col.prop(sourceops, 'auto_export_meshes')
        col.prop(sourceops, 'auto_generate_qc')
        
        col.prop(sourceops, 'auto_compile_qc')
        sub_comp = col.column()
        sub_comp.enabled = sourceops.auto_compile_qc
        sub_comp.prop(sourceops, 'use_studiomdlplusplus')
        
        col.separator()
        col.prop(sourceops, 'auto_use_addon_folder')
        col.prop(sourceops, 'auto_create_material_folder')
        col.prop(sourceops, 'auto_export_materials')
        
        sub = col.column()
        sub.enabled = sourceops.auto_export_materials
        sub.prop(sourceops, 'auto_overwrite_vtf')
        sub.prop(sourceops, 'auto_overwrite_vmt')
        
        col.separator()
        
        row = col.row()
        row.prop(sourceops, 'auto_view_model')
        row.prop(sourceops, 'auto_view_model_plusplus')

    @classmethod
    def poll(cls, context):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)
        sourceops = utils.common.get_globals(context)
        model = utils.common.get_model(sourceops)
        return prefs and game and sourceops and model

    def invoke(self, context, event):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)

        if not utils.game.verify(game):
            self.report({'ERROR'}, 'Game is invalid')
            return {'CANCELLED'}

        if event.ctrl:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):
        prefs = utils.common.get_prefs(context)
        game = utils.common.get_game(prefs)
        sourceops = utils.common.get_globals(context)

        start = time.time()
        self._lock = Lock()
        self._results =[]

        checked_models =[m for m in sourceops.model_items if getattr(m, 'export_checked', True)]
        
        if not checked_models:
            active_model = utils.common.get_model(sourceops)
            if active_model:
                checked_models =[active_model]
                
        if not checked_models:
            self.report({'WARNING'}, 'No models selected for export!')
            return {'CANCELLED'}

        source_models =[Model(game, m) for m in checked_models]

        for source_model in source_models:
            source_model.use_addon_folder = sourceops.auto_use_addon_folder
            source_model.create_material_folder = sourceops.auto_create_material_folder
            source_model.overwrite_vtf = sourceops.auto_overwrite_vtf
            source_model.overwrite_vmt = sourceops.auto_overwrite_vmt
            source_model.use_studiomdlplusplus = sourceops.use_studiomdlplusplus
            
            error = self.export(source_model, sourceops)
            if error:
                self.report({'ERROR'}, f"Export Error on {source_model.name}: {error}")
                return {'CANCELLED'}

        if sourceops.auto_compile_qc:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures =[executor.submit(m.compile_qc) for m in source_models]
                for future in concurrent.futures.as_completed(futures):
                    err = future.result()
                    if err:
                        with self._lock:
                            self._results.append(err)

        if self._results:
            for error in self._results:
                self.report({'ERROR'}, error)
            return {'CANCELLED'}

        # Execute only the requested viewer
        if sourceops.auto_view_model:
            for m in source_models:
                m.view_model()
                
        if sourceops.auto_view_model_plusplus:
            for m in source_models:
                m.view_model_plusplus()

        if len(checked_models) > 1:
            self.report({'INFO'}, f'Exported {len(checked_models)} models in {round(time.time() - start, 1)} seconds')
        else:
            m = checked_models[0]
            forced_static = not m.armature and not m.static
            static_message = ' (forced static due to lack of armature)' if forced_static else ''
            self.report({'INFO'}, f'Exported {m.name} in {round(time.time() - start, 1)} seconds{static_message}')

        return {'FINISHED'}

    def export(self, source_model: Model, sourceops):
        if sourceops.auto_export_materials:
            source_model.export_materials_func(sourceops.auto_use_addon_folder)

        if sourceops.auto_export_meshes:
            error = source_model.export_meshes()
            if error:
                return error

        if sourceops.auto_generate_qc:
            error = source_model.generate_qc()
            if error:
                return error
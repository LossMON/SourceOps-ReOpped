from pathlib import Path
from ..utils.common import resolve

def trigger_backup(self, context):
    """Instantly saves your settings to the permanent JSON file whenever you make a change."""
    try:
        from . import backup
        backup.backup(backup.filepath())
    except Exception:
        pass

def update_game(self, context):
    self['game'] = resolve(self.game)
    game = Path(self.game)

    if game.joinpath('gameinfo.txt').is_file():
        bin_dir = game.parent.joinpath('bin')

        # Check if compiler is in the root bin dir
        has_compiler = (bin_dir.joinpath('studiomdlplusplus.exe').is_file() or 
                        bin_dir.joinpath('quickmdl.exe').is_file() or 
                        bin_dir.joinpath('studiomdl.exe').is_file())

        if not has_compiler:
            for path in bin_dir.iterdir():
                if path.is_dir() and (path.joinpath('studiomdlplusplus.exe').is_file() or path.joinpath('quickmdl.exe').is_file() or path.joinpath('studiomdl.exe').is_file()):
                    bin_dir = path
                    break

        self['bin'] = str(bin_dir)
        self['modelsrc'] = str(game.joinpath('modelsrc'))
        self['models'] = str(game.joinpath('models'))
        self['mapsrc'] = str(game.joinpath('mapsrc'))
        
        # Auto-detect HLMV++ folder
        hlmv_pp_dir = bin_dir
        if not hlmv_pp_dir.joinpath('hlmvplusplus.exe').is_file():
            if game.parent.joinpath('bin', 'win64', 'hlmvplusplus.exe').is_file():
                hlmv_pp_dir = game.parent.joinpath('bin', 'win64')
            elif game.parent.joinpath('bin', 'x64', 'hlmvplusplus.exe').is_file():
                hlmv_pp_dir = game.parent.joinpath('bin', 'x64')
        
        self['hlmvplusplus'] = str(hlmv_pp_dir)
        
    trigger_backup(self, context)

def update_bin(self, context):
    self['bin'] = resolve(self.bin)
    trigger_backup(self, context)

def update_modelsrc(self, context):
    self['modelsrc'] = resolve(self.modelsrc)
    trigger_backup(self, context)

def update_models(self, context):
    self['models'] = resolve(self.models)
    trigger_backup(self, context)

def update_mapsrc(self, context):
    self['mapsrc'] = resolve(self.mapsrc)
    trigger_backup(self, context)

def update_hlmvplusplus(self, context):
    self['hlmvplusplus'] = resolve(self.hlmvplusplus)
    trigger_backup(self, context)

def verify(game):
    gameinfo = Path(game.game).joinpath('gameinfo.txt')
    bin_path = Path(game.bin)
    
    has_compiler = (bin_path.joinpath('studiomdlplusplus.exe').is_file() or 
                    bin_path.joinpath('quickmdl.exe').is_file() or 
                    bin_path.joinpath('studiomdl.exe').is_file())
                    
    return gameinfo.is_file() and has_compiler
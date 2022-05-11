import os
import platform

from maya import cmds


def userPrefsPath() -> str:
    if platform.system() == "Windows":
        prefPath = os.path.expanduser('~/maya/prefs')
    else:
        prefPath = os.path.expanduser('~/Library/Preferences/Autodesk/Maya/prefs')
    return prefPath


def open_project_dir(name: str = 'root'):
    """
    Opens a project directory as specified by its name. If it is not a valid directory
    name then nothing will be opened. If the directory does not exist it will simply
    not do anything as well.

    Accepted inputs to name:
        - images
        - images-tmp
        - sourceimages
        - scenes
        - REF
        - ANIM
        - RENDER
        - FX
    """
    workspace = cmds.workspace(q=True, fn=True)
    paths = {
        # Project Directories
        'root': workspace,
        'images': cmds.renderSettings(fin=True, fp=True),
        'images-tmp': cmds.renderSettings(fin=True, fpt=True),
        'sourceimages': f'{workspace}/sourceimages/',
        'scenes': f'{workspace}/scenes/',

        # Scene Directories
        'REF': f'{workspace}/scenes/REF/',
        'ANIM': f'{workspace}/scenes/ANIM/',
        'RENDER': f'{workspace}/scenes/RENDER/',
        'FX': f'{workspace}/scenes/FX/'
    }

    if name not in paths:
        return

    path = paths[name]
    if not os.path.exists(path):
        return

    os.startfile(path)

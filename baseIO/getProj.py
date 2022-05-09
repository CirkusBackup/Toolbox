import maya.cmds as cmds


def getProject():
    proj = cmds.workspace(q=True, directory=True, rd=True)
    return proj


def filepath():
    filename = cmds.file(query=True, sceneName=True)
    return filename


def sceneFolder():
    return filepath().rsplit('/', 1)[0]


def sceneFile():
    return filepath().rsplit('/', 1)[-1]


def sceneName():
    return sceneFile().split('.')[0]

import maya.cmds as cmds


def getRenderLayers():
    """
    Returns render layers and their states.
    """
    layers = cmds.ls(type="renderLayer")
    layerData = []

    # Filter out extra legacy and default render layers.
    for layer in layers:
        if ':defaultRenderLayer' in layer:
            print(f'skipping {layer}')
        elif '_defaultRenderLayer' in layer:
            print(f'skipping {layer}')
        else:
            renderable = cmds.getAttr(f'{layer}.renderable')
            layerData.append([layer, renderable])

    return layerData


def getStartFrame():
    startFrame = cmds.playbackOptions(q=True, min=True)
    startFrameStr = str('{0:g}'.format(startFrame))
    return str(startFrameStr)


def getEndFrame():
    endFrame = cmds.playbackOptions(q=True, max=True)
    endFrameStr = str('{0:g}'.format(endFrame))
    return str(endFrameStr)

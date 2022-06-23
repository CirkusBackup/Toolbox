from textwrap import dedent

import maya.cmds as cmds
import re
import os


# export animation
def publishFile(abcFilename, preroll: dict = {}):
    # get workspace
    workspace = cmds.workspace(q=True, directory=True, rd=True)
    workspaceLen = len(workspace.split('/'))
    # get filename
    filename = cmds.file(q=True, sn=True)
    # get relative path (from scenes)
    relativePath = ''
    for dir in filename.split('/')[workspaceLen:-1]:
        relativePath += f'{dir}/'

    # string of objects to export
    exportString = ''
    sel = cmds.ls(sl=True)
    for item in sel:
        exportString += f' -root {item}'

    # get timeline
    startFrame = int(cmds.playbackOptions(q=True, minTime=True))
    endFrame = int(cmds.playbackOptions(q=True, maxTime=True))

    # set folder to export to
    folderPath = '%scache/alembic/%s' % (workspace, relativePath)
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    # check if plugin is already loaded
    if not cmds.pluginInfo('AbcImport', query=True, loaded=True):
        try:
            # load abcExport plugin
            cmds.loadPlugin('AbcImport')
        except:
            cmds.error('Could not load AbcImport plugin')

    # export .abc
    additionalAttr = ''
    # IO attributes
    additionalAttributes = ['alembicName', 'IOID', 'material']
    # redshift attributes
    additionalAttributes += ['rsObjectId', 'rsEnableSubdivision', 'rsMaxTessellationSubdivs', 'rsDoSmoothSubdivision',
                             'rsMinTessellationLength', 'rsOutOfFrustumTessellationFactor', 'rsEnableDisplacement',
                             'rsMaxDisplacement', 'rsDisplacementScale']
    for attr in additionalAttributes:
        additionalAttr += ' -attr %s' % (attr)

    prerollStart = preroll.get('start', startFrame - 1)
    prerollStep = preroll.get('step', 1)

    command = dedent(f'''
    -frameRange {prerollStart} {startFrame - 1} -step {prerollStep} -preroll
    -frameRange {startFrame} {endFrame}{additionalAttr}
    -uvWrite
    -writeVisibility
    -wholeFrameGeo
    -worldSpace
    -writeUVSets
    -dataFormat ogawa{exportString}
    -file "{workspace}cache/alembic/{relativePath}{abcFilename}.abc"
    ''').replace('\n', ' ')
    # load plugin
    if not cmds.pluginInfo('AbcExport', query=True, loaded=True):
        try:
            # load abcExport plugin
            cmds.loadPlugin('AbcExport')
        except:
            cmds.error('Could not load AbcExport plugin')
    # write to disk
    cmds.AbcExport(j=command)
    return f'{workspace}cache/alembic/{relativePath}{abcFilename}.abc'


def runSilent():
    # construct filename from user input
    names = createFilenames()
    publishName = names[0] + '_' + names[1]
    return publishFile(publishName)


# update name and run
def runWithUI():
    # construct filename from user input
    prefixString = cmds.textField('prefixText', q=True, text=True)
    nameString = cmds.textField('nameText', q=True, text=True)
    publishName = prefixString + '_' + nameString
    prerollstart = cmds.intField('preroll_start', q=True, v=True)
    prerollStep = cmds.floatField('preroll_step', q=True, v=True)
    preroll = {}

    if cmds.checkBox('preroll_enabled', q=True, v=True):
        preroll = {
            'start': prerollstart, 
            'step': prerollStep
        }

    delete_anim_window()
    publishFile(publishName, preroll)


def createFilenames():
    # get filename
    filename = cmds.file(q=True, sn=True, shn=True).split('.')[0]
    # set text
    publishName = ''
    sel = cmds.ls(sl=True)
    selection = []
    # remove any unnecessary characters and namespaces
    for item in sel:
        selection.append(re.split(':|\|', item)[-1].replace('_', ''))
    selection = list(set(selection))
    for i, s in enumerate(selection):
        if i != 0:
            publishName += '_'
        publishName += s
    # shorten name if longer than 50 characters
    if len(publishName) > 50:
        publishName = '%s_anim' % (selection[0])
    # lengthen name if none exists
    if len(publishName) == 0:
        publishName = 'anim'
    return [filename, publishName]


def anim_setText(*args):
    # get filename
    names = createFilenames()
    cmds.textField('prefixText', e=True, tx=names[0])
    cmds.textField('nameText', e=True, tx=names[1])


def IO_publishAnim_window():
    # UI objects

    layout = cmds.rowColumnLayout(adj=1)
    cmds.rowLayout(p=layout, nc=3, cw=[1, 100])
    cmds.text(label='Prefix', align='right')
    cmds.textField('prefixText', w=250)

    cmds.rowLayout(p=layout, nc=3, cw=[1, 100])
    cmds.text(label='Publish Name', align='right')
    cmds.textField('nameText', w=250)
    cmds.iconTextButton(style='iconOnly', image1='refresh.png', c=anim_setText)

    cmds.rowColumnLayout(p=layout, adj=1)
    cmds.text(l='', h=20)
    cmds.text(ww=True,l='Preroll is used for simulation. Start defines what frame to start the preroll, step defines how large of a step each frame is. Preroll run before the alembic starts exporting.')

    cmds.rowLayout(p=layout, nc=6, cw=[1, 100])
    cmds.text(label='Preroll', align='right')
    cmds.text(label='Start')
    cmds.intField('preroll_start')
    cmds.text(label='Step')
    cmds.floatField('preroll_step', step=0.01, v=1)
    cmds.checkBox('preroll_enabled', l='Enabled', v=0)

    cmds.rowColumnLayout(p=layout, adj=1)
    cmds.text(l='', h=20)
    publishForm = cmds.formLayout(p=layout, h=50)
    btn1 = cmds.button(l='Publish', h=50, c='runWithUI()')
    btn2 = cmds.button(l='Close', h=50, c='cmds.deleteUI("Publish Animation Window")')
    # UI layout
    cmds.formLayout(
        publishForm,
        edit=True,
        attachForm=[
            (btn1, 'bottom', 0),
            (btn1, 'left', 0),
            (btn2, 'bottom', 0),
            (btn2, 'right', 0)
        ],
        attachControl=[
            (btn2, 'left', 0, btn1)
        ],
        attachPosition=[
            (btn1, 'right', 0, 50)
        ])
    anim_setText()


def delete_anim_window():
    workspaceName = 'Publish Animation Window'
    if (cmds.workspaceControl(workspaceName, exists=True)):
        cmds.deleteUI(workspaceName)


def IO_publishAnim(silent):
    if silent == 1:
        print('silent')
        return runSilent()
    else:
        workspaceName = 'Publish Animation Window'
        if (cmds.workspaceControl(workspaceName, exists=True)):
            cmds.deleteUI(workspaceName)
        cmds.workspaceControl(workspaceName, initialHeight=100, initialWidth=300, uiScript='IO_publishAnim_window()')

# IO_publishAnim(0)

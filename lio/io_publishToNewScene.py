import os
import subprocess

import maya.cmds as cmds

import lio
from LlamaIO import UserPrefs
from LlamaIO import containsDigits


def runExportScripts():
    animPath = lio.io_publishAnimation.IO_publishAnim(1)
    cameraPath = lio.io_publishCamera.io_exportCamera(1)

    makeNewFile(animPath, cameraPath)


# make nice file name
def niceFileName(filename, variant, initials):
    import re
    # split filename into workable parts
    fParts = filename.split('_')
    # retain prefix but make sure it's not 'shot'
    filePrefix = ''
    for parts in fParts:
        if containsDigits(parts):
            break
        if parts.lower() == 'shot':
            break
        if parts.lower() == 'sh':
            break
        filePrefix += f'{parts}_'
    # identify numbers
    numbers = re.sub("[a-zA-Z.]", "", filename)
    numbers = filter(None, numbers.split('_'))
    # identify version
    version = '_v001'
    if len(numbers) > 0:
        version = f'_v{numbers[-1]:03}'
    # identify shot number
    shotName = ''
    if len(numbers) > 1:
        shotName = f'SH{numbers[0]:04}'
    # add variant
    if variant:
        variant = f'_{variant}'
    # add variant
    if initials:
        initials = f'_{initials}'

    renderFileName = f'{filePrefix}{shotName}{variant}{version}{initials}.mb'
    return renderFileName


def makeNewFile(animPath, cameraPath):
    filename = cmds.file(q=True, sn=True)
    currentFolder = filename.rsplit('/', 1)[0]
    # replace current folder with 'RENDER'
    newFolder = currentFolder.replace('ANIM', 'RENDER')
    newFolder = newFolder.replace('TVC', 'RENDER')
    # make sure the folder exists
    if not os.path.exists(newFolder):
        os.makedirs(newFolder)
    # get final file name/path
    fileName = niceFileName(filename.rsplit('/', 1)[1], 'RENDER', UserPrefs.getUserPrefs())
    renderFilename = '%s/%s' % (newFolder, fileName)
    # execute
    command = f'C:/Progra~1/Autodesk/Maya2018/bin/mayabatch.exe -command "file -rename ""{renderFilename}"";file -save;"'
    # command = r'C:/Progra~1/Autodesk/Maya2018/bin/mayabatch.exe -command "saveFile(""%s"",""%s"",""%s"")"'%(renderFilename,animPath,cameraPath)
    subprocess.Popen(command, shell=True)


runExportScripts()

import maya.cmds as cmds
import maya.mel as mel
import json
import os
import urllib.request as request
from collections import OrderedDict

# Define constants
_GITHUB_RAW = 'https://raw.githubusercontent.com/CirkusBackup/Toolbox/main/'


def createShelf(shelfName):
    shelfExists = False
    sehlfs = cmds.layout('ShelfLayout', q=True, ca=True)
    for shelf in sehlfs:
        if shelf == shelfName:
            shelfExists = True

    if shelfExists:
        print(f'Shelf {shelfName} exists.')
    else:
        print(f'Shelf {shelfName} does not exist. Creating new shelf.')
        mel.eval(f'addNewShelfTab(\"{shelfName}\");')


def removeSeparator(shelfName, iconName):
    createShelf(shelfName)
    shelfButtons = cmds.shelfLayout(shelfName, q=True, childArray=True)

    if shelfButtons:
        for btn in shelfButtons:
            label = ''

            # Assert that this is a shelfButton
            if cmds.objectTypeUI(btn, isType='separator'):
                cmds.deleteUI(btn)


def removeButton(shelfName, iconName):
    shelfButtons = cmds.shelfLayout(shelfName, q=True, childArray=True)

    if shelfButtons:
        for btn in shelfButtons:
            label = ''

            # Assert that this is a shelfButton
            if cmds.objectTypeUI(btn, isType='shelfButton'):

                label = cmds.shelfButton(btn, q=True, label=True)

                # If this button has the label we're looking for,
                # delete the button.
                if iconName == label:
                    cmds.deleteUI(btn)


def downloadFile(remote: str, local: str):
    """'
    Downloads a file from online somewhere into a local file.
    """
    file_path = local.rsplit('/', 1)

    # Create the local dirs if not there
    if len(file_path) > 1:
        if not os.path.exists(f'{file_path[0]}'):
            os.makedirs(file_path[0])

    # Write the file to disk
    with request.urlopen(remote) as req:
        head = req.info()

        total_size = head['Content-Length']
        block_size = 8192
        cur_block = 0

        print(f'Starting download of file {remote} ({total_size} bytes)...')

        # Start downloading chunks
        with open(local, 'wb') as file:
            while True:
                chunk = req.read(block_size)
                if not chunk: break
                file.write(chunk)
                cur_block += 1
                percent = int(cur_block * block_size * 100 / total_size)
                if percent > 100:
                    percent = 100
                print(f'    {percent:.2f}%')
                if percent < 100:
                    print('\b\b\b\b\b')
                else:
                    print(f'Done: {local}')
        file.flush()


def checkGroups(shelfName):
    # check that shelf exists
    createShelf(shelfName)

    # read json
    try:
        JSONPath = cmds.textField('jsonPathText', q=True, text=True)
        with open(JSONPath) as data_file:
            data = json.load(data_file)

        children = cmds.columnLayout('listLayout', q=True, ca=True)
        allButtons = []
        for c in children:

            if cmds.checkBox(c, q=True, v=True):
                cName = cmds.checkBox(c, q=True, l=True)
                buttons = (data[cName]['buttons'])
                allButtons += buttons

            cmds.deleteUI(c)

        # remove separators
        removeSeparator(shelfName, 'separator')

        addIcons(shelfName, allButtons)
        cmds.deleteUI('Install Toolbox')
    except Exception:
        pass


def addIcons(shelfName, buttons):
    localScriptsPath = cmds.optionMenu('scriptsMenu', query=True, v=True)
    localIconsPath = cmds.optionMenu('iconsMenu', query=True, v=True)
    scriptsMenuI = cmds.optionMenu('scriptsMenu', query=True, sl=True)

    # resize progress bar
    cmds.progressBar('progressControl', edit=True,
                     vis=True, maxValue=len(buttons) - 1)

    # loop through dictionary
    for i, btn in enumerate(buttons):
        shelfElements = buttons[i]
        shelfString = 'cmds.shelfButton(rpt=True'
        # download icons from github
        try:
            icon = buttons[i]['icon']
            if isinstance(icon, str):
                icon = [icon]
            for ii, ico in enumerate(icon):
                if ico == 'separator':
                    print('seperator')
                    shelfString = 'cmds.separator(style=\'shelf\',horizontal=0'
                else:
                    # try to download file
                    downloadFile(f'{_GITHUB_RAW}icons/{ico}',
                                 f'{localIconsPath}/{ico}')
                    if ii == 0:
                        shelfString += ',i1=\'' + ico + '\''
        except Exception as e:
            print('file not available')
            print('Exception:', e)
            # set icon to default button because image can not be downloaded
            shelfString += ',i1=\'commandButton.png\''
        # update progress
        cmds.progressBar('progressControl', edit=True, step=1)

        # download script from github
        if scriptsMenuI > 1:
            try:
                script = buttons[i]['script']

                downloadFile(f'{_GITHUB_RAW}{script}',
                             f'{localScriptsPath}/{script}')
            except Exception:
                print('file not available')

        # download modules from github
        if scriptsMenuI > 1:
            try:
                modules = buttons[i]['modules']
                for mod in modules:
                    downloadFile(f'{_GITHUB_RAW}{mod}',
                                 f'{localScriptsPath}/{mod}')
            except Exception:
                print('file not available')
        try:
            label = buttons[i]['label']
            shelfString += f',l=\'{label}\''
        except Exception:
            label = ''
        try:
            com = buttons[i]['command']
            shelfString += f',c=\'{com}\''
        except Exception:
            com = ''
        try:
            stp = buttons[i]['stp']
            shelfString += f',stp=\'{stp}\''
        except Exception:
            # shelfString += ',stp=\'mel\''
            print('using mel')

        shelfString += ',w=32,h=32,p=\'' + shelfName + '\')'

        # remove old button
        if label:
            removeButton(shelfName, label)

        # add icons to shelf
        currentButton = eval(shelfString)

        try:
            mi = buttons[i]['menuItem']
            for i, l in enumerate(mi):
                cmds.shelfButton(currentButton, edit=True, mi=(
                    mi[i]['label'], mi[i]['command']))
        except Exception:
            pass


def CheckText():
    shelfName = cmds.textField('nameText', q=True, text=True)
    checkGroups(shelfName)


def filterOutSystemPaths(path):
    systemPath = 0
    if path[0] == '/':
        systemPath = 1
    allparts = path.split('/')
    for part in allparts:
        if part == 'ProgramData' or part == 'Program Files':
            systemPath = 1

    return systemPath


def browseForFile():
    filename = cmds.fileDialog2(fileMode=1, caption="Import Image")
    print(filename)
    cmds.textField('jsonPathText', e=True, tx=filename[0])
    updateGrpCheckboxes()
    # return filename


def updateGrpCheckboxes():
    try:
        children = cmds.columnLayout('listLayout', q=True, ca=True)
        for c in children:
            cmds.deleteUI(c)
    except Exception:
        pass

    JSONPath = cmds.textField('jsonPathText', q=True, tx=True)

    try:
        data = json.load(open(JSONPath), object_pairs_hook=OrderedDict)
        cmds.textField('jsonPathText', e=True, text=JSONPath)
        cmds.setParent('listLayout')
        for k in data:
            cb = cmds.checkBox(h=20, label=k, v=1)
            try:
                if data[k]["checkStatus"] == 0:
                    cmds.checkBox(cb, e=True, v=0)
                if data[k]["checkStatus"] == 2:
                    cmds.checkBox(cb, e=True, v=1, ed=0)
            except Exception:
                pass
    except Exception:
        pass


def installToolboxWindow():
    installForm = cmds.formLayout()
    textLabel = cmds.text(label='Shelf')
    nameText = cmds.textField('nameText', width=200, tx='CoolTool')
    scriptsMenu = cmds.optionMenu('scriptsMenu')
    jsonPathText = cmds.textField('jsonPathText', ed=False, pht='path to json')
    jsonPathBtn = cmds.button('jsonPathBtn', width=50,
                              label='...', c='browseForFile()')
    separator = ';' if cmds.about(nt=True) else ':'
    scriptsPaths = os.getenv('MAYA_SCRIPT_PATH')
    allparts = scriptsPaths.split(separator)
    for i, part in enumerate(allparts):
        if i == 0:
            cmds.menuItem(label='Manually install scripts')
        if i < 7:
            isSystemPath = filterOutSystemPaths(part)
            if isSystemPath == 0:
                cmds.menuItem(label=part)

    iconsMenu = cmds.optionMenu('iconsMenu')
    iconsPaths = os.getenv('XBMLANGPATH')
    iconsParts = iconsPaths.split(separator)

    for i, part in enumerate(iconsParts):
        if i < 6:
            isSystemPath = filterOutSystemPaths(part)
            if isSystemPath == 0:
                cmds.menuItem(label=part)

    progressControl = cmds.progressBar(
        'progressControl', maxValue=10, vis=False, width=250)

    btn1 = cmds.button(height=50, label='Install', c='CheckText()')
    btn2 = cmds.button(height=50, label='Close',
                       c='cmds.deleteUI(\'Install Toolbox\')')

    listLayout = cmds.columnLayout('listLayout', adjustableColumn=True)

    try:
        dirname = os.path.dirname(__file__)
    except Exception:
        print('running in test environment')
        dirname = 'C:/Users/Admin/Documents/Toolbox'

    JSONPath = f'{dirname}/toolboxShelf.json'

    try:
        data = json.load(open(JSONPath), object_pairs_hook=OrderedDict)
        cmds.textField('jsonPathText', e=True, text=JSONPath)
        for k in data:
            cb = cmds.checkBox(h=20, label=k, v=1)
            try:
                if data[k]["checkStatus"] == 0:
                    cmds.checkBox(cb, e=True, v=0)
                if data[k]["checkStatus"] == 2:
                    cmds.checkBox(cb, e=True, v=1, ed=0)
            except Exception:
                pass
    except Exception:
        pass

    cmds.formLayout(installForm, edit=True,
                    attachForm=[
                        (textLabel, 'top', 15),
                        (textLabel, 'left', 10),
                        (nameText, 'top', 10),
                        (nameText, 'right', 10),
                        (scriptsMenu, 'right', 10),
                        (iconsMenu, 'right', 10),
                        (jsonPathBtn, 'right', 10),
                        (progressControl, 'left', 10),
                        (progressControl, 'right', 10),
                        (btn1, 'bottom', 0),
                        (btn1, 'left', 0),
                        (btn2, 'bottom', 0),
                        (btn2, 'right', 0)
                    ],
                    attachControl=[
                        (nameText, 'left', 10, textLabel),
                        (scriptsMenu, 'top', 10, textLabel),
                        (scriptsMenu, 'left', 10, textLabel),
                        (iconsMenu, 'top', 10, scriptsMenu),
                        (iconsMenu, 'left', 10, textLabel),
                        (jsonPathText, 'top', 10, iconsMenu),
                        (jsonPathBtn, 'top', 10, iconsMenu),
                        (jsonPathText, 'left', 10, textLabel),
                        (jsonPathText, 'right', 10, jsonPathBtn),
                        (progressControl, 'top', 20, jsonPathText),
                        (progressControl, 'left', 10, textLabel),
                        (listLayout, 'top', 20, jsonPathText),
                        (listLayout, 'left', 10, textLabel),
                        (btn2, 'left', 0, btn1)
                    ],
                    attachPosition=[
                        (btn1, 'right', 0, 50)
                    ]
                    )


def toolbox_install():
    workspaceName = 'Install Toolbox'
    if cmds.workspaceControl('Install Toolbox', exists=True):
        cmds.deleteUI('Install Toolbox')
    cmds.workspaceControl(workspaceName, initialHeight=250,
                          initialWidth=200, uiScript='installToolboxWindow()')

# toolbox_install()

# import installToolbox
# installToolbox.toolbox_install()

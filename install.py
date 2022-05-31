import json
import os.path

from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
from maya import cmds
from maya.OpenMayaUI import MQtUtil
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from shiboken2 import wrapInstance
import urllib.request as request
from typing import Optional

__version__ = '1.0.0'

# Core constant's
_REPO = 'https://raw.githubusercontent.com/CirkusBackup/Toolbox/main/'
W_OBJ = 'cirkusinstallerwindow'
W_TITLE = 'Cirkus Toolbox Installer'


def _maya_main_window():
    """
    Returns an instance of the main window for maya.
    """
    return wrapInstance(int(MQtUtil.mainWindow()), QMainWindow)


def _maya_delete_ui(window_title, window_object):
    """
    Clean up and delete matching windows.
    """
    if cmds.window(window_object, q=True, exists=True):
        cmds.deleteUI(window_object)
    if cmds.dockControl(f'MayaWindow|{window_title}', q=True, exists=True):
        cmds.deleteUI(f'MayaWindow|{window_title}')


def _maya_delete_workspace(window_object):
    """
    Clean up any matchign workspace controls
    """
    control = f'{window_object}WorkspaceControl'
    if cmds.workspaceControl(control, q=True, exists=True):
        cmds.workspaceControl(control, e=True, close=True)
        cmds.deleteUI(control, control=True)


def download_data(url: str, local: str = None) -> Optional[str]:
    """
    Downloads data from an url. If local is not defined or set to None
    then it this will return the data in a string format otherwise
    it will be written to file.

    :url:    URL to where the data is being downloaded from.

    :local:  Full path to the local file the data will be written into.
             if this is empty then it will be returned,
    """
    data = None
    to_file = local is not None

    def write_file(r, f):
        while True:
            block = r.read(8129)
            if not block:
                break
            f.write(block)

    def write_data(r):
        nonlocal data
        if data is None:
            data = ''
        while True:
            block = r.read(8129)
            if not block:
                break
            data += block

    with request.urlopen(url) as req:
        # head = req.info()
        # total_size = int(head['Content-Length'])
        # block_size = 8129
        # cur_block = 0
        if to_file:
            with open(local, 'wb') as file:
                write_file(req, file)
        else:
            write_data(req)

    return data


class InstallData:

    def __int__(self):
        self._data = None

    def collect(self):
        pass

    def get(self) -> dict:
        pass


def _clean_up():
    """Cleans up all instances of the installation window from maya."""
    _maya_delete_ui(W_TITLE, W_OBJ)
    _maya_delete_workspace(W_OBJ)


def install_file():
    # TODO
    pass


def install_shelf():
    # TODO
    pass


class InstallerWindow(MayaQWidgetBaseMixin, QDialog):

    def __init__(self):
        _clean_up()
        super(InstallerWindow, self).__init__(_maya_main_window())

        # Setup base window properties
        self.setObjectName(W_OBJ)
        self.setWindowTitle(W_TITLE)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setFixedWidth(400)
        self.setMaximumWidth(700)

        self._toolbox_data = None

        # Build the UI
        self._build_ui()
        self.adjustSize()

    @property
    def is_local_install(self) -> bool:
        return self._install_from_options.currentText()

    def _build_ui(self):
        """
        Builds the UI for the installer window.
        """
        layout = QVBoxLayout()

        self.setStyleSheet('QComboBox { padding: 5px 10px; } #install-btn { background: #709B64; }')

        # Install options
        options_layout = QFormLayout()
        options_layout.setContentsMargins(30, 30, 30, 30)
        options_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        options_layout.setHorizontalSpacing(30)

        # Install Type
        self._install_from_options = QComboBox()
        self._install_from_options.addItems(['Remote Install', 'Local Install'])
        scripts_install_loc = QComboBox()
        icons_install_loc = QComboBox()
        shelf_name = QLineEdit(placeholderText='CoolTool')

        scripts_install_loc.addItem('Manually Install')
        icons_install_loc.addItem('Install path..')

        options_layout.addRow(QLabel('Install From'), self._install_from_options)
        options_layout.addRow(QLabel('Scripts Path'), scripts_install_loc)
        options_layout.addRow(QLabel('Icons Path'), icons_install_loc)
        options_layout.addRow(QLabel('Shelf Name'), shelf_name)

        # Add all the paths to the dropdown options.
        script_paths = os.getenv('MAYA_SCRIPT_PATH').split(';')
        icon_paths = os.getenv('XBMLANGPATH').split(';')

        for path in script_paths:
            scripts_install_loc.addItem(path)
        for path in icon_paths:
            icons_install_loc.addItem(path)

        # List of installable tools
        modules_layout = QVBoxLayout()
        modules_layout.setContentsMargins(30, 10, 0, 0)

        for i in range(10):
            tool = QCheckBox(f'Tool Name {i}')
            tool.setContentsMargins(30, 20, 0, 0)
            modules_layout.addWidget(tool)

        # Main operation buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        cancel_btn = QPushButton('Cancel', fixedHeight=50)
        install_btn = QPushButton('Install', objectName='install-btn', fixedHeight=50)

        buttons_layout.addWidget(install_btn)
        buttons_layout.addWidget(cancel_btn)

        # Create heading layout and labels
        heading = QVBoxLayout(alignment=Qt.AlignHCenter)
        heading.addWidget(QLabel('<h1>Cirkus Toolbox</h1>', alignment=Qt.AlignHCenter))
        heading.addWidget(QLabel('Select what tools you want to install and where they should be installed.'
                                 'All the available paths are defined as maya environment paths.',
                                 wordWrap=True, fixedHeight=50, fixedWidth=290, alignment=Qt.AlignTop))

        # Add all the layouts and set it to the widget
        layout.addLayout(heading)
        layout.addLayout(options_layout)
        layout.addWidget(QLabel('<h3>Available Tools to Install</h3>'))
        layout.addLayout(modules_layout)
        layout.addStretch()
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def install(self):
        """
        Runs the installer
        """
        # Handle invalid data to install from
        if self._toolbox_data is None:
            pass

    def _update_tools(self):
        """Updates all UI elements for the tools that can be installed."""
        pass

    def _fetch_tools_data(self) -> Optional[dict]:
        """
        Fetches the data for the installer. This will check in multiple
        locations depending on if it is being selected as a remote or local
        installiation.
        """
        # Attempt to download the tool's data from the repo.
        if not self.is_local_install:
            pass

        local_path = os.path.dirname(__file__)
        data = None
        if local_path is not None:
            file = os.path.join(local_path, 'toolboxShelf.json')
            return json.loads(file)

        return None


if __name__ == '__main__':
    installer = InstallerWindow()
    installer.show()

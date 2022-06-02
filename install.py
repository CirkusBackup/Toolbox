import json
import os.path
import inspect

from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon
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
            data += block.decode('utf-8')

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


class RowColumnWidget(QWidget):
    """Simple widget to build a set of rows and columns"""

    def __init__(self, columns: int = 2):
        super(RowColumnWidget, self).__init__()

        # Have a min value of 1
        if columns < 1:
            columns = 1

        self.columns = columns
        self._widgets = []
        self._columns = []

        self._layout = QHBoxLayout()
        self.setLayout(self._layout)

        for i in range(columns):
            layout_base = QVBoxLayout()
            layout = QVBoxLayout()
            layout_base.addLayout(layout)
            layout_base.addStretch()
            self._layout.addLayout(layout_base)
            self._columns.append(layout)

        self.adjustSize()

    def addWidget(self, widget: QWidget):
        self._widgets.append(widget)
        col = self.columns - 1 - len(self._widgets) % self.columns
        self._columns[col].addWidget(widget)

    def reset(self):
        widget: QWidget
        for widget in self._widgets:
            widget.deleteLater()
            widget.setParent(None)
        self._widgets.clear()


class ToolButtonWidget(QPushButton):

    def __init__(self, *args, **kwargs):
        super(ToolButtonWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCheckable(True)

        self.setStyleSheet('''
        ToolButtonWidget {
            background: transparent;
            border: 3px solid #5D5D5D;
            padding-top: 7px;
            padding-bottom: 7px;
            border-radius: 8px;
        }
        ToolButtonWidget:checked {
            border-color: #709B64;
        }
        ''')


class InstallerWindow(MayaQWidgetBaseMixin, QDialog):

    def __init__(self):
        _clean_up()
        super(InstallerWindow, self).__init__(_maya_main_window())

        # Setup base window properties
        self.setObjectName(W_OBJ)
        self.setWindowTitle(W_TITLE)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        # self.setFixedWidth(400)
        # self.setMaximumWidth(700)

        # Define base vars
        self._local_toolbox_dir: Optional[str] = None  # local install dir
        self._toolbox_data: Optional[dict] = None  # all data from toolboxShelf.json
        self._tools_list_widget = RowColumnWidget(2)
        self._remote_data: Optional[dict] = None

        self.splash = self._ui_install_progress_splash()

        # Build the UI
        self._build_ui()
        self._check_install_state()

    @property
    def is_local_install(self) -> bool:
        return self._install_from_options.currentIndex()

    def _check_install_state(self):
        """
        Sets the state of the install button to be enabled or disabled
        depending on if all parameters are valid. This will also update
        the listed tools in the UI to match if it is sourcing from either
        remote or local paths.
        """
        self._fetch_tools_data()
        if self.is_local_install:
            if self._local_toolbox_dir is None:
                self.install_btn.setEnabled(False)
                self._load_tools(None)
                return
        self._load_tools(self._remote_data)
        self.install_btn.setEnabled(True)

    def _select_install_dir(self):
        """
        Opens a dialog to select the directory where the Cirkus Toolbox tools are located.
        If the directory does not have the required files to install the tools from then
        a warning will be shown and not be set.
        """
        responce = QFileDialog.getExistingDirectory(
            parent=self,
            caption='Select install directory',
            directory=os.getcwd()
        )

        # ignore cancels
        if responce is None or len(responce) == 0:
            return

        # Check if the required files are in the directory to install with
        files = os.listdir(responce)
        if 'toolboxShelf.json' not in files:
            cmds.warning('Invalid Install Directory. This does not contain the required data to install the Cirkus '
                         'Toolbox with.')
            self._check_install_state()
            self._load_tools(None)
            return

        # Update internal vars and UI
        self._local_toolbox_dir = responce
        self._install_local_text.setText(responce)
        self._check_install_state()
        self._fetch_tools_data()

    def _ui_install_build(self) -> QLayout:
        """
        Builds UI elements to handle the options of switching between a remote
        or local installation.
        """
        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 0)
        layout.setHorizontalSpacing(30)

        content_layout = QHBoxLayout()

        # Install Type
        self._install_from_options = QComboBox()
        self._install_from_options.addItems(['Remote Install', 'Local Install'])

        local_layout = QHBoxLayout()
        local_widget = QWidget(layout=local_layout, visible=self._install_from_options.currentIndex())
        open_search_btn = QPushButton(icon=QIcon(':/folder-open.png'))
        self._install_local_text = QLineEdit(disabled=True)
        local_layout.addWidget(self._install_local_text)
        local_layout.addWidget(open_search_btn)

        local_layout.setContentsMargins(0, 0, 0, 0)

        local_dir = inspect.getfile(lambda: None)
        if '<maya console>' in local_dir:
            local_dir = ''
        self._install_local_text.setText(local_dir)

        content_layout.addWidget(self._install_from_options)
        content_layout.addWidget(local_widget)

        layout.addRow(QLabel('Install From'), content_layout)
        # layout.addRow(QLabel(''), local_widget)

        # Make Connections
        self._install_from_options.currentIndexChanged.connect(lambda x: (
            local_widget.setVisible(x), self._check_install_state()
        ))
        open_search_btn.clicked.connect(lambda x: self._select_install_dir())

        return layout

    def _ui_install_progress_splash(self) -> QLayout:
        pass

    def _build_ui(self):
        """
        Builds the UI for the installer window.
        """
        layout = QVBoxLayout()

        # Some simple styling
        self.setStyleSheet('''
        QComboBox { padding: 5px 10px; } 
        #install-btn { background: #709B64; border-radius: 8px; }
        #install-btn:hover { background: #97C989; }
        #install-btn:pressed { background: #3F5838; }
        #install-btn:disabled { background: #5E7059; }
        #cancel-btn { background: #5D5D5D; border-radius: 8px; }
        #cancel-btn:hover { background: #787878; }
        #cancel-btn:pressed { background: #2B2B2B; }
        ''')

        # Install options
        options_layout = QFormLayout()
        options_layout.setContentsMargins(30, 0, 30, 30)
        options_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        options_layout.setHorizontalSpacing(30)

        # Install Type
        scripts_install_loc = QComboBox()
        icons_install_loc = QComboBox()
        shelf_name = QLineEdit(placeholderText='CoolTool')

        scripts_install_loc.addItem('Manually Install')

        # options_layout.addRow(QLabel('Install From'), self._install_from_options)
        options_layout.addRow(QLabel('Scripts Path'), scripts_install_loc)
        options_layout.addRow(QLabel('Icons Path'), icons_install_loc)
        options_layout.addRow(QLabel('Shelf Name'), shelf_name)

        # Add all the paths to the dropdown options.
        script_paths: list = os.getenv('MAYA_SCRIPT_PATH').split(';')
        icon_paths: list = os.getenv('XBMLANGPATH').split(';')

        # Add all aviliable install paths in excluding system paths
        for path in filter(lambda x: '/Program' not in x and len(x) > 0, script_paths):
            scripts_install_loc.addItem(path)
        for path in filter(lambda x: '/Program' not in x and len(x) > 0, icon_paths):
            icons_install_loc.addItem(path)

        # Main operation buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        cancel_btn = QPushButton('Cancel', objectName='cancel-btn', fixedHeight=50)
        self.install_btn = QPushButton('Install', objectName='install-btn', fixedHeight=50)

        buttons_layout.addWidget(self.install_btn)
        buttons_layout.addWidget(cancel_btn)

        # Create heading layout and labels
        heading = QVBoxLayout(alignment=Qt.AlignHCenter)
        heading.addWidget(QLabel('<h1>Cirkus Toolbox</h1>', alignment=Qt.AlignHCenter))
        heading.addWidget(QLabel('Select what tools you want to install and where they should be installed.'
                                 'All the available paths are defined as maya environment paths.',
                                 wordWrap=True, fixedHeight=50, fixedWidth=290, alignment=Qt.AlignTop))

        # Add all the layouts and set it to the widget
        layout.addLayout(heading)
        layout.addLayout(self._ui_install_build())
        layout.addLayout(options_layout)
        layout.addWidget(QLabel('<h3 align="center">Available Tools to Install</h3>'))
        # layout.addLayout(modules_layout)
        layout.addWidget(self._tools_list_widget)
        layout.addStretch()
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def install(self):
        """
        Runs the installer
        """
        # TODO  If this is a local install check that the install path is valid before
        #       continuting.
        # Handle invalid data to install from
        if self._toolbox_data is None:
            return

    def _load_tools(self, shelves: Optional[dict]):
        """
        Loads all the tools into memory and updates the UI elements to reflect all
        the aviliable tools that can be installed.
        """
        self._toolbox_data = shelves

        # Remove all old widgets from list
        self._tools_list_widget.reset()

        if shelves is None:
            return

        # Update UI Elements
        for tool in shelves:
            widget = ToolButtonWidget(tool, parent=self)
            self._tools_list_widget.addWidget(widget)

    def _fetch_tools_data(self):
        """
        Fetches the data for the installer. This will check in multiple
        locations depending on if it is being selected as a remote or local
        installiation.
        """
        # Attempt to download the tool's data from the repo online.
        if not self.is_local_install:
            if self._remote_data is None:
                data = download_data(f'{_REPO}toolboxShelf.json')
                self._remote_data = json.loads(data)
            self._load_tools(self._remote_data)
            return

        # Load from file
        if self._local_toolbox_dir is not None:
            file = os.path.join(self._local_toolbox_dir, 'toolboxShelf.json')
            with open(file, 'r') as content:
                self._load_tools(json.loads(content.read()))


if __name__ == '__main__':
    installer = InstallerWindow()
    installer.show()

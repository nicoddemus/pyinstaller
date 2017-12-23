#-----------------------------------------------------------------------------
# Copyright (c) 2014-2017, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

import os
from PyInstaller.utils.hooks import collect_data_files, get_qmake_path, qt_plugins_binaries
import PyInstaller.compat as compat

hiddenimports = ["sip",
                 "PyQt5.QtCore",
                 "PyQt5.QtGui",
                 "PyQt5.QtNetwork",
                 "PyQt5.QtWebChannel",
                 "PyQt5.QtWebEngineCore",
                 ]

# Find the additional files necessary for QtWebEngine.
datas = (collect_data_files('PyQt5', True, os.path.join('Qt', 'resources')) +
         collect_data_files('PyQt5', True, os.path.join('Qt', 'translations')) +
         [x for x in collect_data_files('PyQt5', False, os.path.join('Qt'))
          if 'QtWebEngineProcess' in os.path.basename(x[0]) or os.path.basename(x[0]) == 'qt.conf'])

if compat.is_linux:
    binaries = (
        # Include required QT plugins for QtWebEngine.
        qt_plugins_binaries('xcbglintegrations', namespace='PyQt5') +
        # The automatic library detection fails for `NSS <https://packages.ubuntu.com/search?keywords=libnss3>`_, which is used by QtWebEngine. Pull in the missing files.
        # TODO: how to locate this? The ``locate`` command finds non-system locations (``/usr/lib/firefix/libnss3.so``, for example) in addition to the path below.
        [('/usr/lib/x86_64-linux-gnu/nss/*.so', '.')]
    )

# Note that for QtWebEngineProcess to be able to find icudtl.dat the bundle_identifier
# must be set to 'org.qt-project.Qt.QtWebEngineCore'. This can be done by passing
# bundle_identifier='org.qt-project.Qt.QtWebEngineCore' to the BUNDLE command in
# the .spec file. FIXME: This is not ideal and a better solution is required.
qmake = get_qmake_path('5')
if qmake:
    libdir = compat.exec_command(qmake, "-query", "QT_INSTALL_LIBS").strip()

    if compat.is_darwin:
        binaries = [
            (os.path.join(libdir, 'QtWebEngineCore.framework', 'Versions', '5',\
                          'Helpers', 'QtWebEngineProcess.app', 'Contents', 'MacOS', 'QtWebEngineProcess'),
             os.path.join('QtWebEngineProcess.app', 'Contents', 'MacOS'))
        ]

        resources_dir = os.path.join(libdir, 'QtWebEngineCore.framework', 'Versions', '5', 'Resources')
        datas += [
            (os.path.join(resources_dir, 'icudtl.dat'),''),
            (os.path.join(resources_dir, 'qtwebengine_resources.pak'), ''),
            # The distributed Info.plist has LSUIElement set to true, which prevents the
            # icon from appearing in the dock.
            (os.path.join(libdir, 'QtWebEngineCore.framework', 'Versions', '5',\
                           'Helpers', 'QtWebEngineProcess.app', 'Contents', 'Info.plist'),
                     os.path.join('QtWebEngineProcess.app', 'Contents'))
        ]


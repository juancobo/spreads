# -*- coding: utf-8 -*-

# Copyright (C) 2014 Johannes Baiter <johannes.baiter@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from PySide6 import QtWidgets as QtGui

from spreads.plugin import HookPlugin, SubcommandHooksMixin
from . import gui
import gui_rc  # noqa

logger = logging.getLogger('spreadsplug.gui')


class GuiCommand(HookPlugin, SubcommandHooksMixin):
    __name__ = 'gui'

    @classmethod
    def add_command_parser(cls, rootparser, config):
        guiparser = rootparser.add_parser(
            'gui', help="Start the GUI wizard")
        guiparser.set_defaults(subcommand=GuiCommand.wizard)

    @staticmethod
    def wizard(config):
        logger.debug("Starting GUI")
        app = QtGui.QApplication([])

        wizard = gui.SpreadsWizard(config)
        wizard.show()
        app.exec_()

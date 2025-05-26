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

"""
Public plugin API (realized through a range of abstract classes) and utility
functions for enumerating and loading plugins.
"""

import abc
import logging
from collections import OrderedDict

import pkg_resources
from blinker import Namespace
from enum import Enum

from spreads.config import OptionTemplate
from spreads.util import (abstractclassmethod, DeviceException,
                          MissingDependencyException)


logger = logging.getLogger("spreads.plugin")

# Global cache of devices and extensions
devices = None
extensions = dict()


class ExtensionException(Exception):
    """" Raised when something went wrong during plugin enumeration/ or
         instantiation.
    """
    def __init__(self, message=None, extension=None):
        super(ExtensionException, self).__init__(message)
        self.extension = extension


class SpreadsPlugin(object):  # pragma: no cover
    """ Plugin base class. """
    signals = Namespace()
    on_progressed = signals.signal('plugin:progressed', doc="""\
    Sent by a :py:class:`SpreadsPlugin` when it has progressed in a
    long-running operation.

    :argument :py:class:`SpreadsPlugin`:    the SpreadsPlugin that progressed
    :keyword float progress:                the progress as a value between 0
                                            and 1
    """)

    @classmethod
    def configuration_template(cls):
        """ Allows a plugin to define its configuration keys.

        The returned dictionary has to be flat (i.e. no nested dicts)
        and contain a OptionTemplate object for each key.

        Example::

          {
           'a_setting': OptionTemplate(value='default_value'),
           'another_setting': OptionTemplate(value=[1, 2, 3],
                                           docstring="A list of things"),
           # In this case, 'full-fat' would be the default value
           'milk': OptionTemplate(value=('full-fat', 'skim'),
                                docstring="Type of milk",
                                selectable=True),
          }

        :returns:   dict with `unicode` ->
                    :py:class:`spreads.config.OptionTemplate`
        """
        pass

    def __init__(self, config):
        """ Initialize the plugin.

        :param config: The global configuration object. If the plugin has a
                        `__name__` attribute, only the section with
                        plugin-specific values gets stored in the `config`
                        attribute
        :type config: :py:class:`confit.ConfigView`
        """
        if hasattr(self, '__name__'):
            self.config = config[self.__name__]
        else:
            self.config = config


class DeviceFeatures(Enum):  # pragma: no cover
    """ Enum that provides various constants that :py:class:`DeviceDriver`
    implementations can expose in their :py:attr:`DeviceDriver.features` tuple
    to declare support for one or more given features.
    """
    #: Device can grab a preview picture
    PREVIEW = 1

    #: Device class allows the operation of two devices simultaneously
    #: (mainly to be used by cameras, where each device is responsible for
    #: capturing a single page.
    IS_CAMERA = 2

    #: Device can display arbitrary messages on its screen
    CAN_DISPLAY_TEXT = 3

    #: Device can read set its own focus distance and read out its autofocus
    CAN_ADJUST_FOCUS = 4


class DeviceDriver(SpreadsPlugin):  # pragma: no cover
    """ Base class for device drivers.

        Subclass to implement support for different devices.
    """
    __metaclass__ = abc.ABCMeta

    #: Tuple of :py:class:`DeviceFeatures` constants that designate the
    #: features the device offers.
    features = ()

    @classmethod
    def configuration_template(cls):
        """ Returns some pre-defined options when the implementing devices
            has the :py:attr:`DeviceFeatures.IS_CAMERA` feature.
        """
        templates = {}
        if DeviceFeatures.IS_CAMERA in cls.features:
            templates.update({
                "parallel_capture": OptionTemplate(
                    value=True,
                    docstring="Trigger capture on multiple devices at once.",
                    selectable=False),
                "flip_target_pages": OptionTemplate(
                    value=False,
                    docstring="Temporarily switch target pages (useful for "
                              "e.g. East-Asian books)"),
                "upside_down": OptionTemplate(
                    value=False,
                    docstring="Cameras are mounted upside-down.")})
        if DeviceFeatures.CAN_ADJUST_FOCUS in cls.features:
            templates.update({
                "focus_mode": OptionTemplate(
                    value=["autofocus_all", "autofocus_initial",
                           "manual"],
                    docstring="Select focus mode", selectable=True),
                "focus_distance": OptionTemplate(
                    value=0, docstring="Distance to focus subject",
                    depends={'device': {'focus_mode': 'manual'}})})
        return templates

    @abstractclassmethod
    def yield_devices(cls, config):  # noqa
        """ Search for usable devices, return a generator that yields them one
        at a time as instances of the implementing class.

        :param config:  spreads configuration
        :type config:   :py:class:`spreads.confit.ConfigView`
        :returns:       Instantiated device objects
        :rtype:         Type of implementing class
        """
        raise NotImplementedError

    def __init__(self, config, device):
        """ Set connection information and other properties.

        :param config:  spreads configuration
        :type config:   :py:class:`spreads.confit.ConfigView`
        :param device:  USB device to use for the object
        :type device:   py:class:`usb.core.Device`
        """
        self.config = config
        self._device = device

    @abc.abstractmethod
    def connected(self):
        """ Check if the device is still connected.

        :rtype:     bool
        """
        raise NotImplementedError

    def set_target_page(self, target_page):
        """ Set the device target page, if applicable.

        :param target_page: The target page
        :type target_page:  unicode, one of `odd` or `even`
        """
        raise NotImplementedError

    @abc.abstractmethod
    def prepare_capture(self):
        """ Prepare device for scanning.

        What this means exactly is up to the implementation and the type
        of device, usually it involves things like switching into record
        mode and applying all relevant settings.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def capture(self, path):
        """ Capture a single image with the device.

        :param path:    Path for the image
        :type path:     :py:class:`pathlib.Path`

        """
        raise NotImplementedError

    @abc.abstractmethod
    def finish_capture(self):
        """ Tell device to finish capturing.

        What this means exactly is up to the implementation and the type of
        device, with a camera it could e.g. involve retracting the lense.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_configuration(self, updated):
        """ Update the device configuration.

        The implementing device driver should propagate these updates to the
        hardware and make sure everything is applied correctly.

        :param updated:     Updated configuration values
        :type updated:      dict
        """
        raise NotImplementedError


class HookPlugin(SpreadsPlugin):
    """ Base class for HookPlugins.

    Implement one of the available mixin classes
    (:py:class:`SubcommandHooksMixin`, :py:class:`CaptureHooksMixin`,
    py:class:`TriggerHooksMixin`, :py:class:`ProcessHooksMixin`,
    :py:class:`OutputHooksMixin`) to register for the appropriate hooks.
    """
    pass


class SubcommandHooksMixin(object):
    """ Mixin for plugins that want to provide custom subcommands. """
    __metaclass__ = abc.ABCMeta

    @abstractclassmethod
    def add_command_parser(cls, rootparser, config):  # noqa
        """ Allows a plugin to register a new command with the command-line
            parser.

        The subparser that is added to :param rootparser: should set the class'
        ``__call__`` method as the ``func`` (via
        :py:meth:`argparse.ArgumentParser.set_defaults`) that is executed
        when the subcommand is specified on the CLI.

        :param rootparser: The root parser that this plugin should add a
                           subparser to.
        :type rootparser:  :py:class:`argparse.ArgumentParser`
        :param config:     The application configuration
        :type config:      :py:class:`spreads.config.Configuration`
        """
        pass


class CaptureHooksMixin(object):
    """ Mixin for plugins that want to hook into the capture process. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def prepare_capture(self, devices):
        """ Perform some action before capturing begins.

        :param devices:     The devices used for capturing
        :type devices:      list of :py:class:`DeviceDriver`
        """
        pass

    @abc.abstractmethod
    def capture(self, devices, path):
        """ Perform some action after each successful capture.

        :param devices:     The devices used for capturing
        :type devices:      list of :py:class:`DeviceDriver`
        :param path:        Workflow path
        :type path:         :py:class:`pathlib.Path`
        """
        pass

    @abc.abstractmethod
    def finish_capture(self, devices, path):
        """ Perform some action after capturing has finished.

        :param devices:     The devices used for capturing
        :type devices:      list of :py:class:`DeviceDriver`
        :param path:        Workflow path
        :type path:         :py:class:`pathlib.Path`
        """
        pass


class TriggerHooksMixin(object):
    """ Mixin for plugins that want to provice customized ways of triggering
        a capture.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def start_trigger_loop(self, capture_callback):
        """ Start a thread that runs an event loop and periodically triggers
            a capture by calling the `capture_callback`.

        :param capture_callback:    The function that triggers a capture
        :type capture_callback:     function
        """
        pass

    @abc.abstractmethod
    def stop_trigger_loop(self):
        """ Stop the thread started by :py:meth:`start_trigger_loop`. """
        pass


class ProcessHooksMixin(object):
    """ Mixin for plugins that want to provide postprocessing functionality.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process(self, pages, target_path):
        """ Perform one or more actions that either modify the captured images
            or generate a different output.

        :param pages:       Pages to be processed
        :type pages:        list of :py:class:`spreads.workflow.Page`
        :param target_path: Target directory for processed files
        :type target_path:  :py:class:`pathlib.Path`
        """
        pass


class OutputHooksMixin(object):
    """ Mixin for plugins that want to create output files. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def output(self, pages, target_path, metadata, table_of_contents):
        """ Assemble an output file from the pages.

        :param pages:       Project path
        :type pages:        list of :py:class:`spreads.workflow.Page`
        :param target_path: Target directory for processed files
        :type target_path:  :py:class:`pathlib.Path`
        :param metadata:    Metadata for workflow
        :type metadata:     :py:class:`spreads.metadata.Metadata`
        :param table_of_contents: Table of Contents for workflow
        :type table_of_contents: list of :py:class:`spreads.workflow.TocEntry`
        """
        pass


def available_plugins():
    """ Get the names of all installed plugins.

    :returns:    List of plugin names
    """
    return sorted([ext.name for ext in
                   pkg_resources.iter_entry_points('spreadsplug.hooks')])


def get_plugins(*names):
    """ Get instantiated and configured plugin instances.

    :param names:   One or more plugin names
    :type names:    unicode
    :returns:       Mapping of plugin name to plugin instance
    :rtype:         dict of unicode -> :py:class:`SpreadsPlugin`
    """
    # Reference to global extension cache
    global extensions
    plugins = OrderedDict()
    for name in names:
        # Already in cache?
        if name in extensions:
            plugins[name] = extensions[name]
            continue
        # Nope, so let's instantiate it...
        try:
            logger.debug("Looking for extension \"{0}\"".format(name))
            ext = next(pkg_resources.iter_entry_points('spreadsplug.hooks',
                                                       name=name))
        except StopIteration:
            raise ExtensionException("Could not locate extension '{0}'"
                                     .format(name), name)
        try:
            plugin = ext.load()
            plugins[name] = plugin
            # ... and put it into the cache
            extensions[name] = plugin
        except ImportError as err:
            message = err.message
            if message.startswith('No module named'):
                message = message[16:]
            raise ExtensionException(
                "Missing Python dependency for extension '{0}': {1}"
                .format(name, message, name))
        except MissingDependencyException as err:
            raise ExtensionException(
                "Error while locating external application dependency for "
                "extension '{0}':\n{1}".format(err.message, name))
    return plugins


def available_drivers():
    """ Get the names of all installed device drivers.

    :returns:    List of driver names
    """
    return [ext.name
            for ext in pkg_resources.iter_entry_points('spreadsplug.devices')]


def get_driver(driver_name):
    """ Get a device driver.

    :param driver_name: Name of driver to instantiate
    :type driver_name:  unicode
    :returns:           The driver class
    :rtype:             :py:class:`DeviceDriver` class
    """
    try:
        ext = next(pkg_resources.iter_entry_points('spreadsplug.devices',
                                                   name=driver_name))
    except StopIteration:
        raise ExtensionException("Could not locate driver '{0}'"
                                 .format(driver_name), driver_name)
    try:
        return ext.load()
    except ImportError as err:
        raise ExtensionException(
            "Missing dependency for driver '{0}': {1}"
            .format(driver_name, err.message[16:]), driver_name)


def get_devices(config, force_reload=False):
    """ Get initialized and configured device instances.

    :param config:          Global configuration
    :type config:           :py:class:`spreads.config.Configuration`
    :param force_reload:    Don't load devices from cache
    :type force_reload:     bool
    :return:                Device instances
    :rtype:                 list of :py:class:`DeviceDriver` objects
    """
    # Reference to global device cache
    global devices
    if not devices or force_reload:
        if 'driver' not in config.keys():
            raise DeviceException(
                "No driver has been configured\n"
                "Please run `spread configure` to select a driver.")
        driver = get_driver(config["driver"].get())
        logger.debug("Finding devices for driver \"{0}\""
                     .format(driver.__name__))
        devices = list(driver.yield_devices(config['device']))
        if not devices:
            raise DeviceException(
                "Could not find any compatible devices!\n"
                "Make sure your devices are turned on and properly connected "
                "to the machine.")
    return devices

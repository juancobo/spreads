Plugins
*******

*spreads* comes with a variety of plugins pre-installed. Plugins perform their
actions at several designated points in the workflow. They can also add
specify options that can be set from one of the interfaces.

.. note::

    As of version 1.0.0dev, all plugins have been updated for Python 3 compatibility
    and include comprehensive testing frameworks. Hardware-dependent plugins now
    support mock testing for development and CI/CD environments.

subcommand plugins
==================
These plugins add additional commands to the *spread* application. This way,
plugins can implement additional workflow steps or provide alternative interfaces
for the application.

gui
---
Launches a graphical interface to the workflow. The steps are the same as with
the :ref:`CLI wizard <cli_tutorial>`, additionally a small thumbnail of every
captured image is shown during the capture process. 

.. note::
    
    The GUI plugin has been updated to use **PySide6** for modern Qt support.
    Legacy PySide installations are no longer supported.

Requires an installation of the *PySide6* packages. Refer to the :ref:`GUI tutorial <gui_tutorial>` for more
information.

web
---
Launches the spread web interface that offers a REST-ish API with which you
can control the application from any HTTP client. It also includes a
client-side JavaScript application that can be used from any recent browser
(Firefox or Chrome recommended). Fore more details, consult the `Web interface
documentation <web_doc>` and the `REST API documentation <rest_api>`

.. option:: --standalone-device

   Enable standalone mode. This option can be used for devices that are
   dedicated to scanning (e.g. a RaspberryPi that runs spreads and nothing
   else). At the moment the only additional feature it enables is the ability
   to shutdown the device from the web interface and REST API.

.. option:: --debug

   Run the application debugging mode.

.. option:: --project-dir <path>

   Location where workflow files are stored. By default this is `~/scans`.

.. option:: --mode [scanner, processor, full (default)]

   Select the mode the web plugin is supposed to run in.
   scanner: Only offer components neccessary for capture and
   download/submission to a postprocessing server
   processor: Start as a postprocessing server that can receive workflows over
   the network from other 'scanner' instances
   full: Combines the above two modes, allows for capture and
   postprocessing/output generation on the same machine

.. option:: --port <port> (default: 5000)

   Select port on which the web plugin is supposed to listen on


.. _postproc_plugs:

*postprocess* plugins
=====================
An extension to the *postprocess* command. Performs one or more actions that
either modify the captured images or generate a different output.

.. _plug_autorotate:

autorotate
----------
Automatically rotates the images according to their device of origin.

.. _plug_scantailor:

scantailor
----------
Automatically generate a ScanTailor configuration file for your scanned book
and generate output images from it. After the configuration has been generated,
you can adjust it in the ScanTailor UI, that will be opened automatically,
unless you specified the :option:`auto <--auto -a>` option. The generation of
the output images will run on all CPU cores in parallel.

.. option:: --autopilot

   Run ScanTailor on on autopilot and do not require and user input during
   postprocessing. This skips the step where you can manually adjust the
   ScanTailor configuration.

.. option:: --detection <content/page> [default: content]

   By default, ScanTailor will use content boundaries to determine what to
   include in its output. With this option, you can tell it to use the page
   boundaries instead.

.. option:: --no-content

   Disable content detection step.

.. option:: --rotate

   Enable rotation step.

.. option:: --no-deskew

   Do not deskew images.

.. option:: --no-split-pages

   Do not split pages.

.. option:: --no-auto-margins

   Disable automatically detect margins.


.. _plug_tesseract:

tesseract
---------
Perform optical character recognition on the scanned pages, using the
*tesseract* application, that has to be installed in order for the plugin to
work. For every recognized page, a HTML document in hOCR format will be written
to *project-directory/done*. These files can be used by the output plugins
to include the recognized text.

.. option:: --language LANGUAGE

   Tell tesseract which language to use for OCR. You can get a list of all
   installed languages on your system by running `spread capture --help`.

.. _output_plugs:

*output* plugins
================
An extension to the *out* command. Generates one or more output files from
the scanned and postprocessed images. Writes its output to *project-directory/done*.

.. _plug_pdfbeads:

pdfbeads
--------
Generate a PDF file from the scanned and postprocessed images, using the
*pdfbeads* tool. If OCR has been performed before, the PDF will include a
hidden text layer with the recognized text.

.. _djvubind:

djvubind
--------
Generate a DJVU file from the scanned and postprocessed images, using the
*djvubind* tool.

.. _device_drivers:

*device* drivers
================
Device drivers handle communication with imaging hardware. As of version 1.0.0dev,
all drivers include comprehensive error handling and testing frameworks.

chdkcamera
----------
**Enhanced CHDK Camera Driver** - Controls Canon cameras running CHDK firmware.

.. note::

    **Version 1.0.0dev Improvements:**
    
    * Fixed Python 3 unicode compatibility issues
    * Enhanced error handling and automatic recovery
    * Support for additional camera models (QualityFix variants, A3300)
    * Comprehensive mock testing framework for hardware-independent development
    * Improved zoom and focus control algorithms
    * Better EXIF orientation handling

**Supported Camera Models:**

* Standard Canon cameras with CHDK firmware
* **QualityFix models**: Canon cameras requiring special quality settings (A810, A1200, etc.)
* **Canon A3300**: Special handling for RAW-only remote shooting
* Most Canon PowerShot series with CHDK support

**Key Features:**

* Remote shooting via USB PTP
* RAW/DNG format support
* Automatic focus control (manual, autofocus)
* Zoom level management with validation
* White balance control across multiple lighting conditions
* Real-time preview image acquisition
* Target page setting for book scanning workflows
* On-camera text display for user feedback

**Configuration Options:**

.. option:: --sensitivity <iso_value>

   ISO sensitivity setting (default: 80)

.. option:: --shutter-speed <fraction>

   Shutter speed as fraction (e.g., "1/25")

.. option:: --zoom-level <level>

   Zoom level (validated against camera capabilities)

.. option:: --shoot-raw

   Enable RAW/DNG format shooting

.. option:: --monochrome

   Enable monochrome shooting mode

.. option:: --whitebalance <mode>

   White balance mode: Auto, Daylight, Cloudy, Tungsten, Fluorescent, Custom

**Testing and Development:**

The CHDK camera driver now includes a comprehensive mock testing framework that allows
development and testing without physical hardware. This enables:

* Continuous integration testing
* Development on systems without camera hardware
* Validation of error handling scenarios
* Performance testing and optimization

gphoto2camera
-------------
**gPhoto2 Camera Driver** - Controls digital cameras via gPhoto2 library.

Supports a wide range of digital cameras through the libgphoto2 library.
Ideal for cameras that don't support CHDK firmware.

dummy
-----
**Dummy Camera Driver** - Simulation driver for testing and development.

Useful for testing workflows and development without physical camera hardware.

...existing code...

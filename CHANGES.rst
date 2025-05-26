1.0.0 (2025/05/25)
    Python 3 Migration & Modernization
    
    - Migrate from Python 2.7 to Python 3.8+
    - Drop support for Python 2.7 (End of Life since 2020)
    - Update all Python dependencies to current secure versions:
      * colorama 0.2.4 → 0.4.6
      * PyYAML 3.10 → 6.0.2 (multiple security fixes)
      * blinker 1.3 → 1.9.0
      * roman 2.0.0 → 4.2
      * psutil 2.0.0 → 6.1.0
      * isbnlib 3.3.8 → 3.10.14
    - Remove Python 2-only dependencies (futures, enum34, pathlib)
    - Replace PySide with PySide6 for GUI support
    - Update Flask and web dependencies for security
    - Modernize CI: Travis CI → GitHub Actions support
    - Fix unicode/basestring references for Python 3 compatibility
    - Replace raw_input() with input()
    - Update setuptools configuration
    - Comprehensive security vulnerability fixes

0.4.2 (2014/01/05)
    - Fix packaging issues
    - Small bugfix for older Tesseract versions

0.4.1 (2013/12/25)
    - Fix 'spread' tool
    - Include missing 'vendor' package in distribution

0.4 (2013/12/25)
    - Use `chdkptp` utility for controlling cameras with CHDK firmware
    - Fix instability when shooting with CHDK cameras
    - Shoot images in RAW/DNG file format *(experimental)*
    - Remove `download` step, images will be directly streamed to the project
      directory
    - Remove `combine` plugin, images will be combined in `capture` step
    - Device driver and plugins, as well as their order of execution can be set
      interactively via the `configure` subcommand, which has to be run before
      the first usage.
    - Lots of internal API changes

0.3.3 (2013/08/28)
    - Fix typo in device manager that prevent drivers from being loaded

0.3.2 (2013/08/24)
    - fixes a problem with the devices drivers

0.3.1 (2013/08/23)
    - fixes a problem that prevented spreads to be installed

0.3 (2013/08/23)
    - Plugins can add completely new subcommands.
    - GUI plugin that provides a graphical workflow wizard.
    - Tesseract plugin that can perform OCR on captured images.
    - pdfbeads plugin can include recognized text in a hidden layer if OCR has
      been performed beforehand.
    - Use EXIF tags to persist orientation information instead of JPEG
      comments.
    - Better logging with colorized output
    - Simplified multithreading/multiprocessing code
    - CHDK driver is a lot more stable now

0.2 (2013/06/30)
    - New plugin system based on Doug Hellmann's `stevedore` package,
      allows packages to extend spreads without being included in the core
      distribution
    - The driver for CHDK cameras no longer relies on gphoto2 and ptpcam,
      but relies on Abel Deuring's `pyptpchdk` package to communicate with
      the cameras.
    - `Wand` is now used to deal with image data instead of `Pillow`
    - New 'colorcorrection' plugin allows users to automatically correct
      white balance.
    - Improved tutorial

0.1 (2013/06/23)
    Initial release

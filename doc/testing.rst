Testing and Development
**********************

As of version 1.0.0dev, spreads includes a comprehensive testing framework
that enables robust development and continuous integration workflows.

Testing Framework
=================

The spreads testing framework provides several key capabilities:

* **Hardware-independent testing** through comprehensive mocking
* **Cross-platform compatibility testing**
* **Automated dependency validation**
* **Performance and regression testing**
* **Plugin API validation**

Running Tests
=============

Basic Test Execution
--------------------

To run the complete test suite::

    python -m pytest tests/ -v

To run tests for a specific component::

    python -m pytest tests/chdkcamera_test.py -v

To run tests with coverage reporting::

    python -m pytest tests/ --cov=spreads --cov=spreadsplug

Hardware Mock Testing
=====================

Many spreads components interact with hardware (cameras, scanners, etc.). The
testing framework includes sophisticated mocking capabilities that simulate
hardware behavior without requiring physical devices.

CHDK Camera Mock Testing
------------------------

The CHDK camera driver includes a comprehensive mock testing framework::

    # Run CHDK camera tests without hardware
    python -m pytest tests/test_chdkptp_mock.py -v

This test suite validates:

* Camera initialization and configuration
* Image capture workflows
* Focus and zoom control
* Error handling and recovery
* Different camera model behaviors (QualityFix, A3300, etc.)
* EXIF orientation handling
* Preview image acquisition

The mock framework simulates:

* Camera device discovery
* PTP communication protocols
* Lua script execution on camera
* Image data streaming
* Error conditions and recovery scenarios

Development Environment Setup
=============================

Setting up a development environment with testing capabilities:

1. **Clone the repository**::

    git clone https://github.com/spreads/spreads.git
    cd spreads

2. **Create a virtual environment**::

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install development dependencies**::

    pip install -e .
    pip install -r test-requirements.txt

4. **Run the test suite**::

    python -m pytest tests/ -v

Testing Without Hardware
========================

All hardware-dependent components can be tested without physical devices:

Camera Testing
--------------

Test camera functionality without physical cameras::

    # Test all camera drivers
    python -m pytest tests/ -k camera -v
    
    # Test specific camera features
    python -m pytest tests/test_chdkptp_mock.py::test_capture_functionality -v

The mock camera drivers simulate:

* Device discovery and connection
* Image capture with various settings
* Focus and zoom control
* Error conditions and recovery
* Different camera model behaviors

Plugin Testing
--------------

Test plugin functionality in isolation::

    # Test specific plugins
    python -m pytest tests/autorotate_test.py -v
    python -m pytest tests/tesseract_test.py -v
    python -m pytest tests/scantailor_test.py -v

Continuous Integration
=====================

The testing framework is designed for CI/CD environments:

GitHub Actions
--------------

Example GitHub Actions workflow::

    name: Tests
    on: [push, pull_request]
    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix:
            python-version: [3.8, 3.9, '3.10', '3.11', '3.12', '3.13']
        steps:
        - uses: actions/checkout@v3
        - name: Set up Python ${{ matrix.python-version }}
          uses: actions/setup-python@v3
          with:
            python-version: ${{ matrix.python-version }}
        - name: Install dependencies
          run: |
            pip install -e .
            pip install -r test-requirements.txt
        - name: Run tests
          run: |
            python -m pytest tests/ -v --cov=spreads --cov=spreadsplug

Docker Testing
--------------

Test in containerized environments::

    # Build test container
    docker build -t spreads-test .
    
    # Run tests in container
    docker run spreads-test python -m pytest tests/ -v

Writing Tests
=============

When contributing to spreads, follow these testing guidelines:

Test Structure
--------------

* Place tests in the ``tests/`` directory
* Name test files with ``_test.py`` suffix
* Use descriptive test function names starting with ``test_``
* Group related tests in classes when appropriate

Mock Usage
----------

For hardware-dependent code, use the provided mock frameworks::

    import pytest
    from unittest.mock import MagicMock, patch
    
    @pytest.fixture
    def mock_camera():
        # Create mock camera device
        mock_device = MagicMock()
        mock_device.capture.return_value = b"mock_image_data"
        return mock_device
    
    def test_capture_workflow(mock_camera):
        # Test capture functionality
        result = mock_camera.capture()
        assert result == b"mock_image_data"

Plugin Testing
--------------

When writing plugin tests, ensure you test:

* Plugin discovery and loading
* Configuration validation
* Core functionality with various inputs
* Error handling and edge cases
* Integration with the plugin API

Example plugin test structure::

    def test_plugin_configuration():
        """Test plugin configuration template."""
        tmpl = MyPlugin.configuration_template()
        assert 'required_option' in tmpl
    
    def test_plugin_functionality():
        """Test core plugin functionality."""
        plugin = MyPlugin(config)
        result = plugin.process(input_data)
        assert result is not None

Debugging Tests
===============

For debugging failing tests:

Verbose Output
--------------

Run tests with maximum verbosity::

    python -m pytest tests/ -vvv --tb=long

Debug Specific Tests
-------------------

Run a single test with debugging::

    python -m pytest tests/test_specific.py::test_function -vvv -s

Use Python debugger::

    import pdb; pdb.set_trace()  # Add to test code
    python -m pytest tests/test_specific.py::test_function -s

Performance Testing
===================

The testing framework includes performance benchmarks:

Benchmark Tests
---------------

Run performance tests::

    python -m pytest tests/ -k benchmark -v

Memory Usage Testing
--------------------

Test memory usage patterns::

    python -m pytest tests/ --benchmark-max-memory=512MB

Contributing Tests
==================

When contributing to spreads:

1. **Write tests for new features**
2. **Update tests when modifying existing functionality**
3. **Ensure all tests pass before submitting pull requests**
4. **Include both positive and negative test cases**
5. **Mock external dependencies appropriately**
6. **Document any special test requirements**

The comprehensive testing framework ensures that spreads remains stable and
reliable across different environments and hardware configurations.
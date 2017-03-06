# libsidplayfp-python
An interface to [libsidplayfp](https://sourceforge.net/projects/sidplay-residfp/) for Python 3 using [cffi](http://cffi.readthedocs.io/en/latest/). Most classes from libsidplayfp's public interface are wrapped into Python classes for ease of use.

The documentation is available from [Read the Docs](http://libsidplayfp-python.readthedocs.io/). Take care when using this library as most parts of the API are not tested thoroughly. It might crash the Python interpreter if an error occurs in the backend. This package is only tested under GNU/Linux but might work under Windows or Mac as well.

## Installation

As the API "out-of-line" mode of cffi is used, a C/C++ compiler is required. Obviously cffi >= 1.0.0 and libsidplayfp >= 1.8 are required as well.

Installation can be done via ``setup.py``:
```
python3 setup.py install
```

## Usage/Documentation

 * [Documentation](http://libsidplayfp-python.readthedocs.io/) is available at Read the Docs.
 * [An example](http://libsidplayfp-python.readthedocs.io/en/latest/example.html) is also available there.

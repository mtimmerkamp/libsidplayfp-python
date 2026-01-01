#!/usr/bin/env python3
# This file is part of libsidplyfp(-python), a Python wrapper to
# libsidplayfp, a SID player engine.

# Copyright (C) 2017 Maximilian Timmerkamp

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pathlib

from cffi import FFI


ffibuilder = FFI()


src_dir = pathlib.Path(__file__).absolute().parent
src_file = src_dir / 'libsidplayfp_wrapper.cpp'
header_file = src_dir / 'libsidplayfp_wrapper.h'


ffibuilder.set_source(
    'libsidplayfp._libsidplayfp',
    src_file.read_text(),
    libraries=['sidplayfp'],
    source_extension='.cpp')
ffibuilder.cdef(header_file.read_text())


if __name__ == '__main__':
    ffibuilder.compile(verbose=True)

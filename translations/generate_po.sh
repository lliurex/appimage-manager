#!/bin/bash

PYTHON_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p appimage-manager/

xgettext $PYTHON_FILES -o appimage-manager/appimage-manager.pot


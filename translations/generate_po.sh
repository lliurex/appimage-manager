#!/bin/bash

PYTHON_FILES="../src/*.py"

mkdir -p appimage-manager/

xgettext $PYTHON_FILES -o appimage-manager/appimage-manager.pot


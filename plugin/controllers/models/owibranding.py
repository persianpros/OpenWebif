#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: owbranding
##########################################################################
# Copyright (C) 2014 - 2020 E2OpenPlugins
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
##############################################################################

from Tools.Directories import fileExists, pathExists
from time import time
import os
import hashlib
from enigma import getBoxType
from boxbranding import getMachineBuild, getDisplayType, getRCName, getImageArch
from Components.SystemInfo import SystemInfo

model = getBoxType()
platform = getMachineBuild()

def getAllInfo():
	info = {}

	grabpip = 0
	if "4k" or "uhd" or "ultra" in model or SystemInfo["HiSilicon"] or platform == "dm4kgen":
		grabpip = 1

	info['grabpip'] = grabpip or 0

	lcd = 0
	if "lcd" in model or getDisplayType() in ("bwlcd96", "bwlcd128", "bwlcd140", "bwlcd255", "colorlcd128", "colorlcd220", "colorlcd400", "colorlcd480", "colorlcd720", "colorlcd800"):
		lcd = 1

	info['lcd'] = lcd or 0

	remote = getRCName()

	if getImageArch() == "sh4" and remote not in ("nbox", "hl101"):
		remote = "spark"

	info['remote'] = remote

	return info


STATIC_INFO_DIC = getAllInfo()

def getLcd():
	return STATIC_INFO_DIC['lcd']

def getGrabPip():
	return STATIC_INFO_DIC['grabpip']

class rc_model:
	def getRcFolder(self):
		return STATIC_INFO_DIC['remote']

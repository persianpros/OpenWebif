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
from Tools.StbHardware import getFPVersion, getBoxProc
from Components.SystemInfo import BoxInfo, SystemInfo

model = BoxInfo.getItem("model")
platform = BoxInfo.getItem("platform")
fp_version = str(getFPVersion())
procmodel = getBoxProc()


def getAllInfo():
	info = {}

	grabpip = 0
	if "4k" or "uhd" or "ultra" in model or SystemInfo["HiSilicon"] or platform == "dm4kgen":
		grabpip = 1

	info['grabpip'] = grabpip or 0

	lcd = 0
	if "lcd" in model or BoxInfo.getItem("displaytype") in ("bwlcd96", "bwlcd128", "bwlcd140", "bwlcd255", "colorlcd128", "colorlcd220", "colorlcd400", "colorlcd480", "colorlcd720", "colorlcd800"):
		lcd = 1

	info['lcd'] = lcd or 0

	remote = BoxInfo.getItem("rcname")
	if model == "et9x00" and not procmodel == "et9500":
		remote = "et9x00"
	elif procmodel == "et9500":
		remote = "et9500"
	elif model in ("et5x00", "et6x00") and not procmodel == "et6500":
		remote = "et6x00"
	elif procmodel == "et6500":
		remote = "et6500"
	elif model == "azboxhd" and not procmodel in ("elite", "ultra"):
		remote = "azboxhd"
	elif procmodel in ("elite", "ultra"):
		remote = "azboxelite"
	elif model == "ventonhdx" or procmodel == "ini-3000" and fp_version.startswith('1'):
		remote = "ini0"
	elif procmodel in ("ini-5000", "ini-7000", "ini-7012"):
		remote = "ini1"
	elif model == "ventonhdx" or procmodel == "ini-3000" and not fp_version.startswith('1'):
		remote = "ini2"
	elif BoxInfo.getItem("architecture") == "sh4" and remote not in ("nbox", "hl101"):
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

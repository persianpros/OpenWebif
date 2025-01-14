# -*- coding: utf-8 -*-

##############################################################################
#                        2011-2022 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from six.moves.urllib.parse import unquote
from enigma import eDVBDB
from Components.NimManager import nimmanager
import Components.ParentalControl


def reloadLameDB(self):
	self.eDVBDB.reloadServicelist()


def reloadUserBouquets(self):
	self.eDVBDB.reloadBouquets()


def reloadTransponders(self):
	nimmanager.readTransponders()


def reloadParentalControl(self):
	Components.ParentalControl.parentalControl.open()


def reloadServicesLists(self, mode):
	self.eDVBDB = eDVBDB.getInstance()
	res = "False"
	msg = "missing or wrong parameter mode [0=both, 1=lamedb only, 2=userbouqets only, 3=transponders, 4=parentalcontrol white-/blacklist]"
	mode = unquote(mode)
	if mode == "0":
		reloadLameDB(self)
		reloadUserBouquets(self)
		res = True
		msg = "reloaded both"
	elif mode == "1":
		reloadLameDB(self)
		res = True
		msg = "reloaded lamedb"
	elif mode == "2":
		reloadUserBouquets(self)
		res = True
		msg = "reloaded bouquets"
	elif mode == "3":
		reloadTransponders(self)
		res = True
		msg = "reloaded transponders"
	elif mode == "4":
		reloadParentalControl(self)
		res = True
		msg = "reloaded parentalcontrol white-/blacklist"

	return {
		"result": res,
		"message": msg
	}

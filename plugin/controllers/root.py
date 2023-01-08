# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: RootController
##########################################################################
# Copyright (C) 2011 - 2022 E2OpenPlugins
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
##########################################################################

from os.path import exists
from six import ensure_binary

from twisted.web import static, http, proxy
from Components.config import config
from Components.Harddisk import harddiskmanager

from Plugins.Extensions.OpenWebif.controllers.models.grab import grabScreenshot
from Plugins.Extensions.OpenWebif.controllers.base import BaseController
from Plugins.Extensions.OpenWebif.controllers.web import WebController, ApiController
from Plugins.Extensions.OpenWebif.controllers.ajax import AjaxController
from Plugins.Extensions.OpenWebif.controllers.opkg import OpkgController
from Plugins.Extensions.OpenWebif.controllers.AT import ATController
from Plugins.Extensions.OpenWebif.controllers.ER import ERController
from Plugins.Extensions.OpenWebif.controllers.BQE import BQEController
from Plugins.Extensions.OpenWebif.controllers.wol import WOLSetupController, WOLClientController
from Plugins.Extensions.OpenWebif.controllers.file import FileController

from Plugins.Extensions.OpenWebif.controllers.defaults import PICON_PATH, getPublicPath, VIEWS_PATH, setMobile, refreshPiconPath


class RootController(BaseController):
	"""
	Root Web Controller
	"""

	def __init__(self, session, path=""):
		BaseController.__init__(self, path=path, session=session)

		self.putChild2("web", WebController(session))
		self.putGZChild("api", ApiController(session))
		self.putGZChild("ajax", AjaxController(session))
		self.putChild2("file", FileController())
		self.putChild2("grab", grabScreenshot(session))
		self.putChild2('hardware', static.File(ensure_binary("/usr/share/enigma2/hardware")))
		for static_val in ('js', 'css', 'static', 'images', 'fonts'):
			self.putChild2(static_val, static.File(ensure_binary(getPublicPath() + '/' + static_val)))
		for static_val in ('modern', 'themes', 'webtv', 'vxg'):
			if exists(getPublicPath(static_val)):
				self.putChild2(static_val, static.File(ensure_binary(getPublicPath() + '/' + static_val)))

		if exists('/usr/bin/shellinaboxd'):
			self.putChild2("terminal", proxy.ReverseProxyResource('::1', 4200, b'/'))
		self.putGZChild("opkg", OpkgController(session))
		self.putChild2("autotimer", ATController(session))
		self.putChild2("epgrefresh", ERController(session))
		self.putChild2("bouqueteditor", BQEController(session))
		self.putChild2("wol", WOLClientController())
		self.putChild2("wolsetup", WOLSetupController(session))
		if PICON_PATH:
			self.setPiconChild(PICON_PATH)
		try:
			from Plugins.Extensions.OpenWebif.controllers.NET import NetController
			self.putChild2("net", NetController(session))
		except:  # nosec # noqa: E722
			pass
		try:
			harddiskmanager.on_partition_list_change.append(self.onPartitionChange)
		except:  # nosec # noqa: E722
			pass

	def onPartitionChange(self, why, part):
		refreshPiconPath()
		if PICON_PATH:
			self.setPiconChild(PICON_PATH)

	def setPiconChild(self, pp):
		self.putChild2("picon", static.File(ensure_binary(pp)))

	# this function will be called before a page is loaded
	def prePageLoad(self, request):
		# we set withMainTemplate here so it's a default for every page
		self.withMainTemplate = True

	# the "pages functions" must be called P_pagename
	# example http://boxip/index => P_index
	def P_index(self, request):
		if config.OpenWebif.webcache.responsive_enabled.value and exists(VIEWS_PATH + "/responsive"):
			return {}
		setMobile()
		uagent = request.getHeader('User-Agent')
		if exists(VIEWS_PATH + "/responsive"):
			if uagent.lower().find("iphone") != -1 or uagent.lower().find("ipod") != -1 or uagent.lower().find("blackberry") != -1 or uagent.lower().find("mobile") != -1 or uagent.lower().find("android") != -1:
				setMobile(True)
				return {}

		return {}

#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

##########################################################################
# OpenWebif: grab
##########################################################################
# Copyright (C) 2011 - 2020 E2OpenPlugins
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

from enigma import eConsoleAppContainer
from boxbranding import getImageArch
if getImageArch() == "sh4":
	from twisted.web import static, resource, http, server
	import os
else:
	from Screens.InfoBar import InfoBar
	from twisted.web import resource, server
	from enigma import eDBoxLCD
	import time
	from Plugins.Extensions.OpenWebif.controllers.utilities import getUrlArg

GRAB_PATH = '/usr/bin/grab'


if getImageArch() == "sh4":
	class grabScreenshot(resource.Resource):
		def __init__(self, session, path=""):
			resource.Resource.__init__(self)
			self.session = session
			self.container = eConsoleAppContainer()
			self.container.appClosed.append(self.grabFinished)
			# self.container.dataAvail.append(self.grabData)

		def render(self, request):
			self.request = request
			graboptions = [GRAB_PATH]

			if "format" in request.args.keys():
				self.fileformat = request.args["format"][0]
			else:
				self.fileformat = "jpg"

			if self.fileformat == "jpg":
				graboptions.append("-j")
				graboptions.append("95")
			elif self.fileformat == "png":
				graboptions.append("-p")
			elif self.fileformat != "bmp":
				self.fileformat = "bmp"

			if "r" in request.args.keys():
				size = request.args["r"][0]
				graboptions.append("-r")
				graboptions.append("%d" % int(size))

			if "mode" in request.args.keys():
				mode = request.args["mode"][0]
				if mode == "osd":
					graboptions.append("-o")
				elif mode == "video":
					graboptions.append("-v")

			try:
				ref = self.session.nav.getCurrentlyPlayingServiceReference().toString()
			except:
				ref = None

			if ref is not None:
				self.sref = '_'.join(ref.split(':', 10)[:10])
			else:
				self.sref = 'screenshot'

			self.filepath = "/tmp/screenshot." + self.fileformat
			graboptions.append(self.filepath)
			self.container.execute(GRAB_PATH, *graboptions)
			return server.NOT_DONE_YET

		def grabData(self, data):
			print("[W] grab:", data,)

		def grabFinished(self, retval=None):
			fileformat = self.fileformat
			if fileformat == "jpg":
				fileformat = "jpeg"
			try:
				fd = open(self.filepath)
				data = fd.read()
				fd.close()
				self.request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (self.sref, self.fileformat))
				self.request.setHeader('Content-Type', 'image/%s' % fileformat)
				self.request.setHeader('Content-Length', '%i' % len(data))
				self.request.write(data)
			except Exception as error:
				self.request.setResponseCode(http.OK)
				self.request.write("Error creating screenshot:\n %s" % error)
			try:
				os.unlink(self.filepath)
			except:
				print("Failed to remove:", self.filepath)
			try:
				self.request.finish()
			except RuntimeError as error:
				print("[OpenWebif] grabFinished error: %s" % error)
			del self.request
			del self.filepath
else:
	class GrabRequest(object):
		def __init__(self, request, session):
			self.request = request

			mode = None
			graboptions = [GRAB_PATH, '-q', '-s']

			fileformat = getUrlArg(request, "format", "jpg")
			if fileformat == "jpg":
				graboptions.append("-j")
				graboptions.append("95")
			elif fileformat == "png":
				graboptions.append("-p")
			elif fileformat != "bmp":
				fileformat = "bmp"

			size = getUrlArg(request, "r")
			if size != None:
				graboptions.append("-r")
				graboptions.append("%d" % int(size))

			mode = getUrlArg(request, "mode")
			if mode != None:
				if mode == "osd":
					graboptions.append("-o")
				elif mode == "video":
					graboptions.append("-v")
				elif mode == "pip":
					graboptions.append("-v")
					if InfoBar.instance.session.pipshown:
						graboptions.append("-i 1")
				elif mode == "lcd":
					eDBoxLCD.getInstance().dumpLCD()
					fileformat = "png"
					command = "cat /tmp/lcdshot.%s" % fileformat

			self.filepath = "/tmp/screenshot." + fileformat
			self.container = eConsoleAppContainer()
			self.container.appClosed.append(self.grabFinished)
			self.container.stdoutAvail.append(request.write)
			self.container.setBufferSize(32768)
			if mode == "lcd":
				if self.container.execute(command):
					raise Exception("failed to execute: ", command)
				sref = 'lcdshot'
			else:
				self.container.execute(GRAB_PATH, *graboptions)
				try:
					if mode == "pip" and InfoBar.instance.session.pipshown:
						ref = InfoBar.instance.session.pip.getCurrentService().toString()
					else:
						ref = session.nav.getCurrentlyPlayingServiceReference().toString()
					sref = '_'.join(ref.split(':', 10)[:10])
				except:  # noqa: E722
					sref = 'screenshot'
			sref = sref + '_' + time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
			request.notifyFinish().addErrback(self.requestAborted)
			request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (sref, fileformat))
			request.setHeader('Content-Type', 'image/%s' % fileformat.replace("jpg", "jpeg"))
			# request.setHeader('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
			# request.setHeader('Cache-Control', 'no-store, must-revalidate, post-check=0, pre-check=0')
			# request.setHeader('Pragma', 'no-cache')

		def requestAborted(self, err):
			# Called when client disconnected early, abort the process and
			# don't call request.finish()
			del self.container.appClosed[:]
			self.container.kill()
			del self.request
			del self.container

		def grabFinished(self, retval=None):
			try:
				self.request.finish()
			except RuntimeError as error:
				print("[OpenWebif] grabFinished error: %s" % error)
			# Break the chain of ownership
			del self.request


	class grabScreenshot(resource.Resource):
		def __init__(self, session, path=None):
			resource.Resource.__init__(self)
			self.session = session

		def render(self, request):
			# Add a reference to the grabber to the Request object. This keeps
			# the object alive at least until the request finishes
			request.grab_in_progress = GrabRequest(request, self.session)
			return server.NOT_DONE_YET

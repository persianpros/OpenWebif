# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: FileController
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

from os.path import realpath, exists, isdir, basename
from re import match
from glob import glob
from six.moves.urllib.parse import quote
from json import dumps
from six import ensure_binary

from twisted.web import static, resource, http

from Screens.LocationBox import defaultInhibitDirs
from Components.config import config
from Plugins.Extensions.OpenWebif.controllers.utilities import lenient_force_utf_8, sanitise_filename_slashes, getUrlArg


def new_getRequestHostname(self):
	host = self.getHeader(b'host')
	if host:
		if host[0] == '[':
			return host.split(']', 1)[0] + "]"
		return host.split(':', 1)[0].encode('ascii')
	return self.getHost().host.encode('ascii')


# Do wee need this?
#http.Request.getRequestHostname = new_getRequestHostname


class FileController(resource.Resource):
	def render(self, request):
		action = getUrlArg(request, "action", "download")
		file = getUrlArg(request, "file")

		if file != None:
			filename = lenient_force_utf_8(file)
			filename = sanitise_filename_slashes(realpath(filename))

			if not exists(filename):
				return "File '%s' not found" % (filename)

			if action == "stream":
				name = getUrlArg(request, "name", "stream")
				port = config.OpenWebif.port.value
				proto = 'http'
				if request.isSecure():
					port = config.OpenWebif.https_port.value
					proto = 'https'
				ourhost = request.getHeader('host')
				m = match('.+\:(\d+)$', ourhost)
				if m is not None:
					port = m.group(1)

				response = "#EXTM3U\n#EXTVLCOPT:http-reconnect=true\n#EXTINF:-1,%s\n%s://%s:%s/file?action=download&file=%s" % (name, proto, request.getRequestHostname(), port, quote(filename))
				request.setHeader("Content-Disposition", 'attachment;filename="%s.m3u"' % name)
				request.setHeader("Content-Type", "application/x-mpegurl")
				return response
			elif action == "delete":
				request.setResponseCode(http.OK)
				return "TODO: DELETE FILE: %s" % (filename)
			elif action == "download":
				request.setHeader("Content-Disposition", "attachment;filename=\"%s\"" % (filename.split('/')[-1]))
				rfile = static.File(ensure_binary(filename), defaultType="application/octet-stream")
				return rfile.render(request)
			else:
				return "wrong action parameter"

		path = getUrlArg(request, "dir")
		if path != None:
			pattern = '*'
			nofiles = False
			pattern = getUrlArg(request, "pattern", "*")
			nofiles = getUrlArg(request, "nofiles") != None
			directories = []
			files = []
			request.setHeader("content-type", "application/json; charset=utf-8")
			if exists(path):
				if path == '/':
					path = ''
				try:
					files = glob(path + '/' + pattern)
				except OSError:
					files = []
				files.sort()
				tmpfiles = files[:]
				for x in tmpfiles:
					if isdir(x):
						directories.append(x + '/')
						files.remove(x)
				if nofiles:
					files = []
				return ensure_binary(dumps({"result": True, "dirs": directories, "files": files}, indent=2))
			else:
				return ensure_binary(dumps({"result": False, "message": "path %s not exits" % (path)}, indent=2))

		tree = "tree" in request.args
		path = getUrlArg(request, "id")
		if tree:
			request.setHeader("content-type", "application/json; charset=utf-8")
			directories = []
			if path is None or path == "#":
				path = "/"
			if exists(path):
				if path == "/":
					path = ""
				try:
					files = glob(path + '/*')
				except OSError:
					files = []
				files.sort()
				tmpfiles = files[:]
				for x in tmpfiles:
					if isdir(x) and x not in defaultInhibitDirs:
						directories.append({"id": x, "text": basename(x), "children": True})
			if path == "":
				return ensure_binary(dumps([{"id": "/", "text": "Root", "children": directories}]))
			else:
				return ensure_binary(dumps([{"id": path, "text": basename(path), "children": directories}]))

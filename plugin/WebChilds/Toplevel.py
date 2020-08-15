#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
#from os import listdir
#from os.path import abspath, splitext
#from twisted.web import static
#from twisted.python import util
#from Tools.Directories import resolveFilename, SCOPE_PLUGINS
#from Plugins.Extensions.OpenWebif import __file__
#
#externalChildren = []
#
#"""
#	.htc Files for IE Fixes need a certain Content-Type
#"""
#import mimetypes
#mimetypes.add_type('text/x-component', '.htc')
#mimetypes.add_type('text/cache-manifest', '.appcache')
#mimetypes.add_type('video/MP2T', '.ts')
#static.File.contentTypes = static.loadMimeTypes()
#
#if hasattr(static.File, 'render_GET'):
#	class File(static.File):
#		def render_POST(self, request):
#			return self.render_GET(request)
#else:
#	File = static.File
#
#def addExternalChild(child):
#	externalChildren.append(child)
#
#def importExternalModules():
#	dir = abspath(resolveFilename(SCOPE_PLUGINS) + "Extensions/OpenWebif/WebChilds/External/")
#	for file in listdir(dir):
#		module_name, ext = splitext(file) # Handles no-extension files, etc.
#
#		if ext == '.pyo' and module_name != "__init__":				
#			try:
#				exec "import " + module_name
#				print('[importExternalModules] Imported external module: %s' % (module_name))
#		
#			except ImportError, e:				
#				print('[importExternalModules] Could not import external module: %s' % (module_name))
#				print('[importExternalModules] Exception Caught\n%s' %e)
#
#def getToplevel(session):
#	root = File(util.sibpath(__file__, "controllers/views/web"))
#
#	importExternalModules()
#
#	for child in externalChildren:
#		if len(child) > 1:
#			root.putChild(child[0], child[1])
#
#	return root

loaded_plugins = []

def addExternalChild(plugin_args):
	if len(plugin_args) == 4:
		for plugin in loaded_plugins:
			if plugin[0] == plugin_args[0]:
				print("[OpenWebif] error: path '%s' already registered" % plugin[0])
				return
		loaded_plugins.append(plugin_args)

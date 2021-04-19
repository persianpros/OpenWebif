#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

##########################################################################
# OpenWebif: info
##########################################################################
# Copyright (C) 2011 - 2021 E2OpenPlugins
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

import os
import six
import time
from twisted import version
from socket import has_ipv6, AF_INET6, AF_INET, inet_ntop, inet_pton, getaddrinfo

import NavigationInstance
from Components.About import about
from Components.config import config
from Components.NimManager import nimmanager
from Components.Harddisk import harddiskmanager
from Components.Network import iNetwork
from ServiceReference import ServiceReference
from RecordTimer import parseEvent, RecordTimerEntry
from timer import TimerEntry
from Screens.InfoBar import InfoBar
from Tools.Directories import fileExists
from enigma import eDVBVolumecontrol, eServiceCenter, eServiceReference, getEnigmaVersionString, eEPGCache, getBoxType, getBoxBrand, eGetEnigmaDebugLvl, getE2Rev
from Tools.StbHardware import getFPVersion, getBoxProc, getBoxProcType, getHWSerial, getBoxRCType
from Plugins.Extensions.OpenWebif.controllers.i18n import _
from Plugins.Extensions.OpenWebif.controllers.defaults import OPENWEBIFVER, TRANSCODING
from Plugins.Extensions.OpenWebif.controllers.utilities import removeBad, removeBad2
import boxbranding
from Plugins.Extensions.OpenWebif.controllers.models.owibranding import getLcd, getGrabPip


def getEnigmaVersionString():
	return about.getEnigmaVersionString()


STATICBOXINFO = None


def getIPMethod(iface):
	# iNetwork.getAdapterAttribute is crap and not portable
	ipmethod = _("SLAAC")
	if fileExists('/etc/network/interfaces'):
		ifaces = '/etc/network/interfaces'
		for line in open(ifaces).readlines():
			if not line.startswith('#'):
				if line.startswith('iface') and "inet6" in line and iface in line:
					if "static" in line:
						ipmethod = _("static")
					if "dhcp" in line:
						ipmethod = _("DHCP")
					if "manual" in line:
						ipmethod = _("manual/disabled")
					if "6to4" in line:
						ipmethod = "6to4"
	return ipmethod


def getIPv4Method(iface):
	# iNetwork.getAdapterAttribute is crap and not portable
	ipv4method = _("static")
	if fileExists('/etc/network/interfaces'):
		ifaces = '/etc/network/interfaces'
		for line in open(ifaces).readlines():
			if not line.startswith('#'):
				if line.startswith('iface') and "inet " in line and iface in line:
					if "static" in line:
						ipv4method = _("static")
					if "dhcp" in line:
						ipv4method = _("DHCP")
					if "manual" in line:
						ipv4method = _("manual/disabled")
	return ipv4method


def getLinkSpeed(iface):
	speed = _("unknown")
	try:
		with open('/sys/class/net/' + iface + '/speed', 'r') as f:
			speed = f.read().strip()
	except:  # nosec # noqa: E722
		if os.path.isdir('/sys/class/net/' + iface + '/wireless'):
			try:
				speed = os.popen('iwconfig ' + iface + ' | grep "Bit Rate"').read().split(':')[1].split(' ')[0]
			except: # nosec # noqa: E722
				pass
	speed = str(speed) + " MBit/s"
	speed = speed.replace("10000 MBit/s", "10 GBit/s")
	speed = speed.replace("1000 MBit/s", "1 GBit/s")
	return speed


def getNICChipSet(iface):
	nic = _("unknown")
	try:
		nic = os.path.realpath('/sys/class/net/' + iface + '/device/driver').split('/')[-1]
		nic = str(nic)
	except:  # nosec # noqa: E722
		pass
	return nic


def getFriendlyNICChipSet(iface):
	friendlynic = getNICChipSet(iface)
	friendlynic = friendlynic.replace("bcmgenet", "Broadcom Gigabit Ethernet")
	friendlynic = friendlynic.replace("bcmemac", "Broadcom STB 10/100 EMAC")
	return friendlynic


def normalize_ipv6(orig):
	net = []

	if '/' in orig:
		net = orig.split('/')
		if net[1] == "128":
			del net[1]
	else:
		net.append(orig)

	addr = net[0]

	addr = inet_ntop(AF_INET6, inet_pton(AF_INET6, addr))

	if len(net) == 2:
		addr += "/" + net[1]

	return (addr)


def getAdapterIPv6(ifname):
	addr = _("IPv4-only kernel")
	firstpublic = None

	if fileExists('/proc/net/if_inet6'):
		addr = _("IPv4-only Python/Twisted")

		if has_ipv6 and version.major >= 12:
			proc = '/proc/net/if_inet6'
			tempaddrs = []
			for line in open(proc).readlines():
				if line.startswith('fe80'):
					continue

				tmpaddr = ""
				tmp = line.split()
				if ifname == tmp[5]:
					tmpaddr = ":".join([tmp[0][i:i + 4] for i in list(range(0, len(tmp[0]), 4))])

					if firstpublic is None and (tmpaddr.startswith('2') or tmpaddr.startswith('3')):
						firstpublic = normalize_ipv6(tmpaddr)

					if tmp[2].lower() != "ff":
						tmpaddr = "%s/%s" % (tmpaddr, int(tmp[2].lower(), 16))

					tmpaddr = normalize_ipv6(tmpaddr)
					tempaddrs.append(tmpaddr)

			if len(tempaddrs) > 1:
				tempaddrs.sort()
				addr = ', '.join(tempaddrs)
			elif len(tempaddrs) == 1:
				addr = tempaddrs[0]
			elif len(tempaddrs) == 0:
				addr = _("none/IPv4-only network")

	return {'addr': addr, 'firstpublic': firstpublic}


def formatIp(ip):
	if ip is None or len(ip) != 4:
		return "0.0.0.0"  # nosec
	return "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])


def getInfo(session=None, need_fullinfo=False):
	# TODO: get webif versione somewhere!
	info = {}
	global STATICBOXINFO

	if not (STATICBOXINFO is None or need_fullinfo):
		return STATICBOXINFO

	info['brand'] = getBoxBrand()
	info['model'] = getBoxType()
	info['platform'] = boxbranding.getMachineBuild()

	try:
		info['procmodel'] = getBoxProc()
	except:  # nosec # noqa: E722
		info['procmodel'] = boxbranding.getMachineProcModel()

	try:
		info['procmodeltype'] = getBoxProcType()
	except:  # nosec # noqa: E722
		info['procmodeltype'] = None

	try:
		info['lcd'] = getLcd()
	except:  # nosec # noqa: E722
		info['lcd'] = 0

	try:
		info['grabpip'] = getGrabPip()
	except:  # nosec # noqa: E722
		info['grabpip'] = 0

	cpu = about.getCPUInfoString()
	info['chipset'] = cpu
	info['cpubrand'] = about.getCPUBrand()
	info['socfamily'] = boxbranding.getSoCFamily()
	info['cpuarch'] = about.getCPUArch()
	if config.OpenWebif.about_benchmark.value is True:
		info['cpubenchmark'] = about.getCPUBenchmark()
	else:
		info['cpubenchmark'] = _("Disabled in configuration")
	info['flashtype'] = about.getFlashType()

	memFree = 0
	for line in open("/proc/meminfo", 'r'):
		parts = line.split(':')
		key = parts[0].strip()
		if key == "MemTotal":
			info['mem1'] = parts[1].strip().replace("kB", _("kB"))
		elif key in ("MemFree", "Buffers", "Cached"):
			memFree += int(parts[1].strip().split(' ', 1)[0])
	info['mem2'] = "%s %s" % (memFree, _("kB"))
	info['mem3'] = _("%s free / %s total") % (info['mem2'], info['mem1'])
	if config.OpenWebif.about_benchmarkram.value is True:
		info['rambenchmark'] = about.getRAMBenchmark()
	else:
		info['rambenchmark'] = _("Disabled in configuration")

	info['uptime'] = about.getBoxUptime()

	info["webifver"] = OPENWEBIFVER
	info['imagedistro'] = boxbranding.getImageDistro()
	info['oever'] = boxbranding.getImageBuild()
	info['visionversion'] = boxbranding.getVisionVersion()
	info['visionrevision'] = boxbranding.getVisionRevision()
	info['visionmodule'] = about.getVisionModule()

	if fileExists("/etc/openvision/multiboot"):
		multibootflag = open("/etc/openvision/multiboot", "r").read().strip()
		if multibootflag == "1":
			info['multiboot'] = _("Yes")
		else:
			info['multiboot'] = _("No")
	else:
		info['multiboot'] = _("Yes")

	info['enigmaver'] = getEnigmaVersionString()
	info['enigmarev'] = getE2Rev()
	info['driverdate'] = about.getDriverInstalledDate()
	info['kernelver'] = boxbranding.getKernelVersion()

	modulelayoutcommand = os.popen('find /lib/modules/ -type f -name "openvision.ko" -exec modprobe --dump-modversions {} \; | grep "module_layout" | cut -c-11').read().strip()

	info['modulelayout'] = modulelayoutcommand
	info['dvbapitype'] = about.getDVBAPI()
	info['gstreamerversion'] = about.getGStreamerVersionString()
	info['ffmpegversion'] = about.getFFmpegVersionString()
	info['pythonversion'] = about.getPythonVersionString()

	try:
		info['hwserial'] = getHWSerial()
	except:  # nosec # noqa: E722
		info['hwserial'] = None

	if (info['hwserial'] is None or info['hwserial'] == "unknown"):
		info['hwserial'] = about.getCPUSerial()

	try:
		info['boxrctype'] = getBoxRCType()
	except:  # nosec # noqa: E722
		info['boxrctype'] = None

	if (info['boxrctype'] is None or info['boxrctype'] == "unknown"):
		if fileExists("/usr/bin/remotecfg"):
			info['boxrctype'] = _("Amlogic remote")
		elif fileExists("/usr/sbin/lircd"):
			info['boxrctype'] = _("LIRC remote")

	info['ovrctype'] = boxbranding.getRCType()
	info['ovrcname'] = boxbranding.getRCName()
	info['ovrcidnum'] = boxbranding.getRCIDNum()

	info['transcoding'] = boxbranding.getHaveTranscoding()
	info['multitranscoding'] = boxbranding.getHaveMultiTranscoding()

	info['displaytype'] = boxbranding.getDisplayType()

	info['updatedatestring'] = about.getUpdateDateString()
	info['enigmadebuglvl'] = eGetEnigmaDebugLvl()

	info['imagearch'] = boxbranding.getImageArch()
	info['imagefolder'] = boxbranding.getImageFolder()
	info['imagefilesystem'] = boxbranding.getImageFileSystem()
	info['feedsurl'] = boxbranding.getFeedsUrl()
	info['developername'] = boxbranding.getDeveloperName()
	info['builddatestring'] = about.getBuildDateString()
	info['imagefpu'] = boxbranding.getImageFPU()
	info['havemultilib'] = boxbranding.getHaveMultiLib()

	try:
		info['fp_version'] = getFPVersion()
	except:  # nosec # noqa: E722
		info['fp_version'] = None

	info['tuners'] = []
	for i in list(range(0, nimmanager.getSlotCount())):
		print("[OpenWebif] -D- tuner '%d' '%s' '%s'" % (i, nimmanager.getNimName(i), nimmanager.getNim(i).getSlotName()))
		info['tuners'].append({
			"name": nimmanager.getNim(i).getSlotName(),
			"type": nimmanager.getNimName(i) + " (" + nimmanager.getNim(i).getFriendlyType() + ")",
			"rec": "",
			"live": ""
		})

	info['ifaces'] = []
	ifaces = iNetwork.getConfiguredAdapters()
	for iface in ifaces:
		info['ifaces'].append({
			"name": iNetwork.getAdapterName(iface),
			"friendlynic": getFriendlyNICChipSet(iface),
			"linkspeed": getLinkSpeed(iface),
			"mac": iNetwork.getAdapterAttribute(iface, "mac"),
			"dhcp": iNetwork.getAdapterAttribute(iface, "dhcp"),
			"ipv4method": getIPv4Method(iface),
			"ip": formatIp(iNetwork.getAdapterAttribute(iface, "ip")),
			"mask": formatIp(iNetwork.getAdapterAttribute(iface, "netmask")),
			"v4prefix": sum([bin(int(x)).count('1') for x in formatIp(iNetwork.getAdapterAttribute(iface, "netmask")).split('.')]),
			"gw": formatIp(iNetwork.getAdapterAttribute(iface, "gateway")),
			"ipv6": getAdapterIPv6(iface)['addr'],
			"ipmethod": getIPMethod(iface),
			"firstpublic": getAdapterIPv6(iface)['firstpublic']
		})

	info['hdd'] = []
	for hdd in harddiskmanager.hdd:
		dev = hdd.findMount()
		if dev:
			stat = os.statvfs(dev)
			free = stat.f_bavail * stat.f_frsize / 1048576.
		else:
			free = -1

		if free <= 1024:
			free = "%i %s" % (free, _("MB"))
		else:
			free = free / 1024.
			free = "%.1f %s" % (free, _("GB"))

		size = hdd.diskSize() * 1000000 / 1048576.
		if size > 1048576:
			size = "%.1f %s" % ((size / 1048576.), _("TB"))
		elif size > 1024:
			size = "%.1f %s" % ((size / 1024.), _("GB"))
		else:
			size = "%d %s" % (size, _("MB"))

		iecsize = hdd.diskSize()
		# Harddisks > 1000 decimal Gigabytes are labelled in TB
		if iecsize > 1000000:
			iecsize = (iecsize + 50000) // float(100000) / 10
			# Omit decimal fraction if it is 0
			if (iecsize % 1 > 0):
				iecsize = "%.1f %s" % (iecsize, _("TB"))
			else:
				iecsize = "%d %s" % (iecsize, _("TB"))
		# Round harddisk sizes beyond ~300GB to full tens: 320, 500, 640, 750GB
		elif iecsize > 300000:
			iecsize = "%d %s" % (((iecsize + 5000) // 10000 * 10), _("GB"))
		# ... be more precise for media < ~300GB (Sticks, SSDs, CF, MMC, ...): 1, 2, 4, 8, 16 ... 256GB
		elif iecsize > 1000:
			iecsize = "%d %s" % (((iecsize + 500) // 1000), _("GB"))
		else:
			iecsize = "%d %s" % (iecsize, _("MB"))

		info['hdd'].append({
			"model": hdd.model(),
			"capacity": size,
			"labelled_capacity": iecsize,
			"free": free,
			"mount": dev,
			"friendlycapacity": _("%s free / %s total") % (free, size + ' ("' + iecsize + '")')
		})

	info['shares'] = []
	autofiles = ('/etc/auto.network', '/etc/auto.network_vti')
	for autofs in autofiles:
		if fileExists(autofs):
			method = "autofs"
			for line in open(autofs).readlines():
				if not line.startswith('#'):
					# Replace escaped spaces that can appear inside credentials with underscores
					# Not elegant but we wouldn't want to expose credentials on the OWIF anyways
					tmpline = line.replace("\ ", "_")
					tmp = tmpline.split()
					if not len(tmp) == 3:
						continue
					name = tmp[0].strip()
					type = "unknown"
					if "cifs" in tmp[1]:
						# Linux still defaults to SMBv1
						type = "SMBv1.0"
						settings = tmp[1].split(",")
						for setting in settings:
							if setting.startswith("vers="):
								type = setting.replace("vers=", "SMBv")
					elif "nfs" in tmp[1]:
						type = "NFS"

					# Default is r/w
					mode = _("r/w")
					settings = tmp[1].split(",")
					for setting in settings:
						if setting == "ro":
							mode = _("r/o")

					uri = tmp[2]
					parts = []
					parts = tmp[2].split(':')
					if parts[0] == "":
						server = uri.split('/')[2]
						uri = uri.strip()[1:]
					else:
						server = parts[0]

					ipaddress = None
					if server:
						# Will fail on literal IPs
						try:
							# Try IPv6 first, as will Linux
							if has_ipv6:
								tmpaddress = None
								tmpaddress = getaddrinfo(server, 0, AF_INET6)
								if tmpaddress:
									ipaddress = "[" + list(tmpaddress)[0][4][0] + "]"
							# Use IPv4 if IPv6 fails or is not present
							if ipaddress is None:
								tmpaddress = None
								tmpaddress = getaddrinfo(server, 0, AF_INET)
								if tmpaddress:
									ipaddress = list(tmpaddress)[0][4][0]
						except:  # nosec # noqa: E722
							pass

					friendlyaddress = server
					if ipaddress is not None and not ipaddress == server:
						friendlyaddress = server + " (" + ipaddress + ")"
					info['shares'].append({
						"name": name,
						"method": method,
						"type": type,
						"mode": mode,
						"path": uri,
						"host": server,
						"ipaddress": ipaddress,
						"friendlyaddress": friendlyaddress
					})
	# TODO: fstab

	info['EX'] = ''

	if session:
		try:
			#  gets all current stream clients for images using eStreamServer
			#  TODO: get tuner info for streams
			#  TODO: get recoding/timer info if more than one
			info['streams'] = GetStreamInfo()

			recs = NavigationInstance.instance.getRecordings()
			if recs:
				#  only one stream
				s_name = ''
				if len(info['streams']) == 1:
					sinfo = info['streams'][0]
					s_name = sinfo["name"] + ' (' + sinfo["ip"] + ')'
					print("[OpenWebif] -D- s_name '%s'" % s_name)

				sname = ''
				timers = []
				for timer in NavigationInstance.instance.RecordTimer.timer_list:
					if timer.isRunning() and not timer.justplay:
						timers.append(removeBad(timer.service_ref.getServiceName()))
						print("[OpenWebif] -D- timer '%s'" % timer.service_ref.getServiceName())
# TODO: more than one recording
				if len(timers) == 1:
					sname = timers[0]

				if sname == '' and s_name != '':
					sname = s_name

				print("[OpenWebif] -D- recs count '%d'" % len(recs))

				for rec in recs:
					feinfo = rec.frontendInfo()
					frontendData = feinfo and feinfo.getAll(True)
					if frontendData is not None:
						cur_info = feinfo.getTransponderData(True)
						if cur_info:
							nr = frontendData['tuner_number']
							info['tuners'][nr]['rec'] = getOrbitalText(cur_info) + ' / ' + sname

			service = session.nav.getCurrentService()
			if service is not None:
				sname = service.info().getName()
				feinfo = service.frontendInfo()
				frontendData = feinfo and feinfo.getAll(True)
				if frontendData is not None:
					cur_info = feinfo.getTransponderData(True)
					if cur_info:
						nr = frontendData['tuner_number']
						info['tuners'][nr]['live'] = getOrbitalText(cur_info) + ' / ' + sname
		except Exception as error:
			info['EX'] = error

	info['timerpipzap'] = False
	info['timerautoadjust'] = False

	try:
		timer = RecordTimerEntry(ServiceReference("1:0:1:0:0:0:0:0:0:0"), 0, 0, '', '', 0)
		if hasattr(timer, "pipzap"):
			info['timerpipzap'] = True
		if hasattr(timer, "autoadjust"):
			info['timerautoadjust'] = True
	except Exception as error:
		print("[OpenWebif] -D- RecordTimerEntry check %s" % error)

	STATICBOXINFO = info
	return info


def getStreamServiceAndEvent(ref):
	sname = "(unknown service)"
	eventname = ""
	if not isinstance(ref, eServiceReference):
		ref = eServiceReference(ref)
	servicereference = ServiceReference(ref)
	if servicereference:
		sname = removeBad(servicereference.getServiceName())
	epg = eEPGCache.getInstance()
	event = epg and epg.lookupEventTime(ref, -1, 0)
	if event:
		eventname = event.getEventName()
	return sname, eventname


def GetStreamInfo():
	streams = []
	nostreamServer = True
	try:
		from enigma import eStreamServer
		streamServer = eStreamServer.getInstance()
		if streamServer is not None:
			nostreamServer = False
			for x in streamServer.getConnectedClients():
				servicename, eventname = getStreamServiceAndEvent(x[1])
				if int(x[2]) == 0:
					strtype = "S"
				else:
					strtype = "T"
				streams.append({
					"ref": x[1],
					"name": servicename,
					"eventname": eventname,
					"ip": x[0],  # TODO: ip Address format
					"type": strtype
				})
	except Exception as error:  # nosec # noqa: E722
#		print("[OpenWebif] -D- no eStreamServer %s" % error)
		pass

	if nostreamServer:
		from Plugins.Extensions.OpenWebif.controllers.stream import streamList
		if len(streamList) > 0:
			for stream in streamList:
				servicename, eventname = getStreamServiceAndEvent(stream.ref)
				streams.append({
					"ref": stream.ref.toString(),
					"name": servicename,
					"eventname": eventname,
					"ip": stream.clientIP,
					"type": "S" # TODO : Transcoding
				})

	return streams


def getOrbitalText(cur_info):
	if cur_info:
		tunerType = cur_info.get('tuner_type')
		if tunerType == "DVB-S":
			pos = int(cur_info.get('orbital_position'))
			return getOrb(pos)
		if cur_info.get("system", -1) == 1:
			tunerType += "2"
		return tunerType
	return ''


def getOrb(pos):
	direction = _("E")
	if pos > 1800:
		pos = 3600 - pos
		direction = _("W")
	return "%d.%d° %s" % (pos / 10, pos % 10, direction)


def getFrontendStatus(session):
	inf = {}
	inf['tunertype'] = ""
	inf['tunernumber'] = ""
	inf['snr'] = ""
	inf['snr_db'] = ""
	inf['agc'] = ""
	inf['ber'] = ""

	from Screens.Standby import inStandby
	if inStandby is None:
		inf['inStandby'] = "false"
	else:
		inf['inStandby'] = "true"

	service = session.nav.getCurrentService()
	if service is None:
		return inf
	feinfo = service.frontendInfo()
	frontendData = feinfo and feinfo.getAll(True)

	if frontendData is not None:
		inf['tunertype'] = frontendData.get("tuner_type", "UNKNOWN")
		inf['tunernumber'] = frontendData.get("tuner_number")

	frontendStatus = feinfo and feinfo.getFrontendStatus()
	if frontendStatus is not None:
		percent = frontendStatus.get("tuner_signal_quality")
		if percent is not None:
			inf['snr'] = int(percent * 100 / 65535)
			inf['snr_db'] = inf['snr']
		percent = frontendStatus.get("tuner_signal_quality_db")
		if percent is not None:
			inf['snr_db'] = "%3.02f" % (percent / 100.0)
		percent = frontendStatus.get("tuner_signal_power")
		if percent is not None:
			inf['agc'] = int(percent * 100 / 65535)
		percent = frontendStatus.get("tuner_bit_error_rate")
		if percent is not None:
			inf['ber'] = int(percent * 100 / 65535)

	return inf


def getCurrentTime():
	t = time.localtime()
	return {
		"status": True,
		"time": "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
	}


def getStatusInfo(self):
	# Get Current Volume and Mute Status
	vcontrol = eDVBVolumecontrol.getInstance()
	statusinfo = {
		'volume': vcontrol.getVolume(),
		'muted': vcontrol.isMuted(),
		'transcoding': TRANSCODING,
		'currservice_filename': "",
		'currservice_id': -1,
	}

	# Get currently running Service
	event = None
	serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
	serviceref_string = None
	currservice_station = None
	if serviceref is not None:
		serviceHandler = eServiceCenter.getInstance()
		serviceHandlerInfo = serviceHandler.info(serviceref)

		service = self.session.nav.getCurrentService()
		serviceinfo = service and service.info()
		event = serviceinfo and serviceinfo.getEvent(0)
		serviceref_string = serviceref.toString()
		currservice_station = removeBad(serviceHandlerInfo.getName(serviceref))
	else:
		event = None
		serviceHandlerInfo = None

	if event is not None:
		# (begin, end, name, description, eit)
		curEvent = parseEvent(event)
		begin_timestamp = int(curEvent[0]) + (config.recording.margin_before.value * 60)
		end_timestamp = int(curEvent[1]) - (config.recording.margin_after.value * 60)
		statusinfo['currservice_name'] = removeBad(curEvent[2])
		statusinfo['currservice_serviceref'] = serviceref_string
		statusinfo['currservice_begin'] = time.strftime("%H:%M", (time.localtime(begin_timestamp)))
		statusinfo['currservice_begin_timestamp'] = begin_timestamp
		statusinfo['currservice_end'] = time.strftime("%H:%M", (time.localtime(end_timestamp)))
		statusinfo['currservice_end_timestamp'] = end_timestamp
		desc = curEvent[3]
		if six.PY2:
			desc = desc.decode('utf-8')
		if len(desc) > 220:
			desc = desc + u"..."
		if six.PY2:
			desc = desc.encode('utf-8')
		statusinfo['currservice_description'] = desc
		statusinfo['currservice_station'] = currservice_station
		if statusinfo['currservice_serviceref'].startswith('1:0:0'):
			statusinfo['currservice_filename'] = '/' + '/'.join(serviceref_string.split("/")[1:])
		full_desc = statusinfo['currservice_name'] + '\n'
		full_desc += statusinfo['currservice_begin'] + " - " + statusinfo['currservice_end'] + '\n\n'
		full_desc += removeBad2(event.getExtendedDescription())
		statusinfo['currservice_fulldescription'] = full_desc
		statusinfo['currservice_id'] = curEvent[4]
	else:
		statusinfo['currservice_name'] = "N/A"
		statusinfo['currservice_begin'] = ""
		statusinfo['currservice_end'] = ""
		statusinfo['currservice_description'] = ""
		statusinfo['currservice_fulldescription'] = "N/A"
		if serviceref:
			statusinfo['currservice_serviceref'] = serviceref_string
			if statusinfo['currservice_serviceref'].startswith('1:0:0') or statusinfo['currservice_serviceref'].startswith('4097:0:0'):
				this_path = '/' + '/'.join(serviceref_string.split("/")[1:])
				if os.path.exists(this_path):
					statusinfo['currservice_filename'] = this_path
			if serviceHandlerInfo:
				statusinfo['currservice_station'] = currservice_station
			elif serviceref_string.find("http") != -1:
				statusinfo['currservice_station'] = serviceref_string.replace('%3a', ':')[serviceref_string.find("http"):]
			else:
				statusinfo['currservice_station'] = "N/A"

	# Get Standby State
	from Screens.Standby import inStandby
	if inStandby is None:
		statusinfo['inStandby'] = "false"
	else:
		statusinfo['inStandby'] = "true"

	# Get recording state
	recs = NavigationInstance.instance.getRecordings()
	if recs:
		statusinfo['isRecording'] = "true"
		statusinfo['Recording_list'] = "\n"
		for timer in NavigationInstance.instance.RecordTimer.timer_list:
			if timer.state == TimerEntry.StateRunning:
				if not timer.justplay:
					statusinfo['Recording_list'] += removeBad(timer.service_ref.getServiceName()) + ": " + timer.name + "\n"
		if statusinfo['Recording_list'] == "\n":
			statusinfo['isRecording'] = "false"
	else:
		statusinfo['isRecording'] = "false"

	# Get streaminfo
	streams = GetStreamInfo()
	Streaming_list = []
	try:

		# TODO move this code to javascript getStatusinfo
		for stream in streams:
			st = ''
			s = stream["name"]
			e = stream["eventname"]
			i = stream["ip"]
			del stream
			if i is not None:
				st += i + ": "
			st += s + ' - ' + e
			if st != '':
				Streaming_list.append(st)

	except Exception as error:  # nosec # noqa: E722
#		print("[OpenWebif] -D- build Streaming_list %s" % error)
		pass

	if len(streams) > 0:
		statusinfo['Streaming_list'] = '\n'.join(Streaming_list)
		statusinfo['isStreaming'] = 'true'
	else:
		statusinfo['Streaming_list'] = ''
		statusinfo['isStreaming'] = 'false'

	return statusinfo


def getAlternativeChannels(service):
	alternativeServices = eServiceCenter.getInstance().list(eServiceReference(service))
	return alternativeServices and alternativeServices.getContent("S", True)


def GetWithAlternative(service, onlyFirst=True):
	if service.startswith('1:134:'):
		channels = getAlternativeChannels(service)
		if channels:
			if onlyFirst:
				return channels[0]
			else:
				return channels
	if onlyFirst:
		return service
	else:
		return None


def getPipStatus():
	return int(getInfo()['grabpip'] and hasattr(InfoBar.instance, 'session') and InfoBar.instance.session.pipshown)


def testPipStatus(self):
	pipinfo = {
		'pip': getPipStatus(),
	}
	return pipinfo

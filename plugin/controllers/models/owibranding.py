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
# Simulate the oe-a boxbranding module (Only functions required by OWIF)     #
##############################################################################

from Tools.Directories import fileExists, pathExists
from time import time
import os
import hashlib
from enigma import getBoxType, getBoxBrand
from Tools.StbHardware import getFPVersion, getBoxProc

fp_version = str(getFPVersion())
brand = getBoxBrand()
model = getBoxType()
procmodel = getBoxProc()

def getAllInfo():
	info = {}

	grabpip = 0
	if "4k" or "uhd" or "ultra" in model or brand in ("dinobot","maxytec") or model in ("dm900","dm920","sf8008","sf8008m","beyonwizv2","hd60","hd61","h9","h9combo","h10","i55plus") or pathExists("/proc/hisi") or fileExists("/usr/bin/hihalt"):
		grabpip = 1

	info['grabpip'] = grabpip or 0

	lcd = 0
	if "lcd" in model or model in ("e4hdultra","sf208","sf228","sf238","protek4k"):
		lcd = 1

	info['lcd'] = lcd or 0

	remote = "dmm1"

	if model in ("vusolo","vuduo","vuuno","vusolo2","vusolose","vuzero","vusolo4k","vuuno4k","vuultimo4k"):
		remote = "vu"
	elif model == "vuultimo":
		remote = "vu2"
	elif model == "vuduo2":
		remote = "vu3"
	elif model in ("vuuno4kse","vuzero4k","vuduo4k"):
		remote = "vu4"
	elif model in ("evoe3hd","geniuse3hd","axase3","axase3c"):
		remote = "e3hd"
	elif model == "et9x00" and not procmodel == "et9500":
		remote = "et9x00"
	elif procmodel == "et9500":
		remote = "et9500"
	elif model in ("et5x00","et6x00") and not procmodel == "et6500":
		remote = "et6x00"
	elif model == "et4x00":
		remote = "et4x00"
	elif procmodel == "et6500":
		remote = "et6500"
	elif model in ("et8000","et8500","et10000"):
		remote = "et8000"
	elif model == "et7x00":
		remote = "et7x00"
	elif model in ("et7000mini","et1x000"):
		remote = "et7x00mini"
	elif model in ("gbquad","gb800se","gb800ue","gb800solo","gb800seplus","gb800ueplus","gbipbox","gbultrase","gbultraue","gbx1","gbx3"):
		remote = "gb0"
	elif model == "gbquadplus":
		remote = "gb1"
	elif model in ("gbx2","gbx3h","gbultraueh"):
		remote = "gb2"
	elif model in ("gbquad4k","gbue4k","gbtrio4k","gbip4k","gbx34k"):
		remote = "gb3"
	elif model in ("formuler1","formuler3","formuler4","formuler4turbo"):
		remote = "formuler1"
	elif model in ("azboxme","azboxminime"):
		remote = "azboxme"
	elif model == "azboxhd" and not procmodel in ("elite","ultra"):
		remote = "azboxhd"
	elif procmodel in ("elite","ultra"):
		remote = "azboxelite"
	elif model in ("optimussos","optimussos1","optimussos1plus","optimussos2","optimussos2plus"):
		remote = "optimuss1"
	elif model == "optimussos3plus":
		remote = "optimuss2"	
	elif model in ("mbtwinplus","mbmicro","mbmicrov2"):
		remote = "miraclebox"
	elif model == "alphatriplehd":
		remote = "sab1"
	elif model == "xp1000":
		remote = "xp1000"
	elif brand in ("nbox","ferguson","sagemcom"):
		remote = "nbox"
	elif brand in ("fulan","forerver"):
		remote = "fulan"
	elif model in ("hd1100","hd1200","hd1265","hd51","hd11","hd500c","hd1500","vs1000","vs1500"):
		remote = "hd1100"
	elif model == "hd2400":
		remote = "hd2400"
	elif model == "hd530c":
		remote = "hd530c"
	elif model == "hd60":
		remote = "hd60"
	elif model == "hd61":
		remote = "ax4"
	elif model in ("multibox","multiboxplus"):
		remote = "maxytec1"
	elif model in ("spycat","spycatmini","spycatminiplus","spycat4kmini","spycat4k","spycat4kcombo"):
		remote = "xcore1"
	elif model in ("osmini","osminiplus","osmega"):
		remote = "xcore3"
	elif model in ("ixussone","ixusszero"):
		remote = "ixuss"
	elif model == "dm8000":
		remote = "dmm0"
	elif model in ("dm800","dm800se","dm500hd"):
		remote = "dmm1"
	elif model in ("dm7080","dm7020hd","dm7020hdv2","dm800sev2","dm500hdv2","dm520","dm820","dm900","dm920"):
		remote = "dmm2"
	elif model == "wetekplay":
		remote = "wetek"
	elif model == "wetekplay2":
		remote = "wetek2"
	elif model == "wetekhub":
		remote = "wetek3"
	elif model in ("osnino","osninoplus"):
		remote = "edision1"
	elif model == "osninopro":
		remote = "edision2"
	elif model in ("osmio4k","osmio4kplus","osmini4k"):
		remote = "edision3"
	elif model in ("fusionhd","fusionhdse","purehd","purehdse"):
		remote = "fusionhd"
	elif model in ("revo4k","galaxy4k"):
		remote = "revo"
	elif model in ("lunix34k","lunix"):
		remote = "qviart1"
	elif model == "lunix4k":
		remote = "qviart3"
	elif model == "lunixco":
		remote = "qviart4"
	elif model == "sh1":
		remote = "zgemma1"
	elif model == "lc":
		remote = "zgemma2"
	elif model in ("h3","h4","h5","h6","h7","h9","h9combo","i55plus"):
		remote = "zgemma3"
	elif model == "i55":
		remote = "zgemma5"
	elif model == "h10":
		remote = "zgemma7"
	elif model == "vipercombohdd":
		remote = "amiko1"
	elif model in ("vipercombo","vipert2c","viperslim"):
		remote = "amiko2"
	elif model == "alien5":
		remote = "amiko3"
	elif model == "viper4k":
		remote = "amiko4"
	elif model in ("k1pro","k2pro","k2prov2","k1plus","k1plusv2"):
		remote = "k1pro"
	elif model == "k3pro":
		remote = "k3pro"
	elif model in ("e4hd","e4hdhybrid"):
		remote = "e4hd"
	elif model in ("e4hdultra","e4hdcombo"):
		remote = "e4hdcombo"
	elif model in ("tmtwin","tm2t"):
		remote = "tm1"
	elif model in ("tmsingle","tmnano","tmnano2t","tmnano3t","tmnano2super"):
		remote = "tm2"
	elif model in ("tmnanose","tmnanosecombo"):
		remote = "tm3"
	elif model in ("tmnanosem2","tmnanosem2plus","tmnanoseplus"):
		remote = "tm4"
	elif model == "tmnanom3":
		remote = "tm5"
	elif model in ("tmtwin4k","tm4ksuper"):
		remote = "tm6"
	elif model in ("dinobot4kmini","dinobot4kplus","dinobot4k","dinobot4kse","dinobot4kl","dinobot4kpro","dinobotu55","dinoboth265"):
		remote = "dinobot"
	elif model in ("axashis4kcombo","axashis4kcomboplus"):
		remote = "axas1"
	elif model == "axashisc4k":
		remote = "axas2"
	elif model == "axashistwin":
		remote = "axas3"
	elif model in ("anadol4k","anadol4kv2"):
		remote = "anadol1"
	elif model == "anadolprohd5":
		remote = "anadol3"
	elif model == "iziboxx3":
		remote = "izibox1"
	elif model in ("arivatwin","arivacombo"):
		remote = "ariva"
	elif model == "odroidc2":
		remote = "hardkernel"
	elif model == "cube":
		remote = "cube"
	elif model in ("ebox5000","ebox5100","ebox7358","eboxlumi"):
		remote = "ebox5000"
	elif model == "sogno8800hd":
		remote = "sogno"
	elif model == "uniboxhde":
		remote = "uniboxhde"
	elif model == "ventonhdx" or procmodel == "ini-3000" and fp_version.startswith('1'):
		remote = "ini0"
	elif procmodel in ("ini-5000","ini-7000","ini-7012"):
		remote = "ini1"
	elif model == "ventonhdx" or procmodel == "ini-3000" and not fp_version.startswith('1'):
		remote = "ini2"
	elif model in ("sezam1000hd","sezam5000hd"):
		remote = "ini2"
	elif model in ("mbmini","mbminiplus","mbhybrid","mbtwin","mbultra"):
		remote = "ini3"
	elif model in ("atemio5x00","atemio6000","atemio6100","atemio6200","atemionemesis","xpeedlx","xpeedlx3","sezammarvel"):
		remote = "ini4"
	elif model == "beyonwizt3":
		remote = "ini5"
	elif model in ("bwidowx","bwidowx2"):
		remote = "ini6"
	elif model in ("beyonwizt2","beyonwizt4"):
		remote = "ini7"
	elif model == "opticumtt":
		remote = "ini8"
	elif model == "beyonwizu4":
		remote = "beyonwiz1"
	elif model == "beyonwizv2":
		remote = "beyonwiz2"
	elif model in ("starsatlx","axodin","axodinc"):
		remote = "odinm6"
	elif model in ("classm","genius","evo","galaxym6"):
		remote = "odinm7"
	elif model == "maram9":
		remote = "odinm9"
	elif model == "ustym4kpro":
		remote = "uclan"
	elif model == "valalinux":
		remote = "vala"
	elif model in ("force4","iqonios100hd","iqonios200hd","iqonios300hd","iqonios300hdv2","force2se","force2","force2plus","force2plushv","force2nano"):
		remote = "iqon1"
	elif model in ("force1","force1plus","worldvisionf1","worldvisionf1plus"):
		remote = "iqon2"
	elif model in ("force3uhdplus","force3uhd"):
		remote = "iqon3"
	elif model == "twinboxlcd":
		remote = "red1"
	elif model in ("singleboxlcd","twinboxlcdci5"):
		remote = "red2"
	elif model in ("triplex","ultrabox"):
		remote = "triplex"
	elif model == "xpeedc":
		remote = "gi1"
	elif model == "mediabox":
		remote = "mediabox"
	elif model == "9900lx":
		remote = "protek1"
	elif model in ("9910lx","9911lx","protek4k","9920lx"):
		remote = "protek2"
	elif model == "protek4kx1":
		remote = "protek3"
	elif model == "enfinity":
		remote = "evo1"
	elif model == "x2plus":
		remote = "evo2"
	elif model in ("xcombo","x1plus"):
		remote = "evo3"
	elif model == "t2cable":
		remote = "evo4"
	elif model in ("evomini","evominiplus"):
		remote = "evo5"
	elif model in ("evoslim","evoslimse","evoslimt2c"):
		remote = "evo8"
	elif model == "sf108":
		remote = "sf108"
	elif model in ("sf208","sf228","sf238"):
		remote = "sf2x8"
	elif model in ("sf3038","sf128","sf138","sf4008"):
		remote = "sf3038"
	elif model == "sf5008":
		remote = "sf5008"
	elif model in ("sf8008","sf8008m"):
		remote = "sf8008"
	elif model == "sf98":
		remote = "sf98"
	elif model in ("bre2ze","bre2ze4k","bre2zet2c"):
		remote = "wwio1"
	elif model in ("tiviarmin","tiviaraplus"):
		remote = "tiviar1"
	elif model in ("odin2hybrid","odinplus"):
		remote = "ax1"
	elif model == "axultra":
		remote = "ax51"
	elif model == "enibox":
		remote = "hdbox"
	elif model == "mago":
		remote = "relook"
	elif model == "tyrant":
		remote = "tyrant"
	elif model == "marvel1":
		remote = "visionnet"

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

#!/usr/bin/env python3
# coding: utf-8 -*-
"""
	Module: z_command.py

	Description: Implement the onCommand() 

"""

import Domoticz
import binascii
import time
import struct
import json

import z_var          # Global variables
import z_tools
import z_output
import z_domoticz


def mgtCommand( self, Devices, Unit, Command, Level, Color ) :
	Domoticz.Debug("#########################")
	Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + " Color: " + str(Color) )

	DSwitchtype= str(Devices[Unit].SwitchType)
	Domoticz.Debug("DSwitchtype : " + DSwitchtype)

	DSubType= str(Devices[Unit].SubType)
	Domoticz.Debug("DSubType : " + DSubType)

	DType= str(Devices[Unit].Type)
	DOptions = Devices[Unit].Options

	Dtypename=DOptions['TypeName']
	Domoticz.Debug("Dtypename : " + Dtypename)
	Dzigate=eval(DOptions['Zigate'])
	SignalLevel = self.ListOfDevices[Devices[Unit].DeviceID]['RSSI']

	EPin="01"
	EPout="01"  # If we don't have a cluster search, or if we don't find an EPout for a cluster search, then lets use EPout=01
	ClusterSearch = ""
	if Dtypename=="Switch" or Dtypename=="Plug" or Dtypename=="MSwitch" or Dtypename=="Smoke" or Dtypename=="DSwitch" or Dtypename=="Button" or Dtypename=="DButton":
		ClusterSearch="0006"
	if Dtypename=="LvlControl" :
		ClusterSearch="0008"
	if Dtypename=="ColorControl" :
		ClusterSearch="0300"
	
	for tmpEp in self.ListOfDevices[Devices[Unit].DeviceID]['Ep'] :
		if ClusterSearch in self.ListOfDevices[Devices[Unit].DeviceID]['Ep'][tmpEp] : #switch cluster
			EPout=tmpEp

	# 00 -> OFF
	# 01 -> ON
	# 02 -> Toggle
	#Can use timed on/off
	#z_output.sendZigateCmd("0093","02" + Devices[Unit].DeviceID + EPin + EPout + on/off + on_time + off_time)
	
	if Command == "Off" :
		self.ListOfDevices[Devices[Unit].DeviceID]['Heartbeat'] = 0  # Let's force a refresh of Attribute in the next Hearbeat
		z_output.sendZigateCmd("0092","02" + Devices[Unit].DeviceID + EPin + EPout + "00")
		if DSwitchtype == "16" :
			z_domoticz.UpdateDevice_v2(Devices, Unit, 0, "0",DOptions, SignalLevel)
		else :
			z_domoticz.UpdateDevice_v2(Devices, Unit, 0, "Off",DOptions, SignalLevel)
	if Command == "On" :
		self.ListOfDevices[Devices[Unit].DeviceID]['Heartbeat'] = 0  # Let's force a refresh of Attribute in the next Hearbeat
		z_output.sendZigateCmd("0092","02" + Devices[Unit].DeviceID + EPin + EPout + "01")
		if DSwitchtype == "16" :
			z_domoticz.UpdateDevice_v2(Devices, Unit, 1, "100",DOptions, SignalLevel)
		else:
			z_domoticz.UpdateDevice_v2(Devices, Unit, 1, "On",DOptions, SignalLevel)

	if Command == "Set Level" :
		#Level is normally an integer but may be a floating point number if the Unit is linked to a thermostat device
		#There is too, move max level, mode = 00/01 for 0%/100%
		#z_output.sendZigateCmd("0080","02" + Devices[Unit].DeviceID + EPin + EPout + OnOff + mode + rate)
		
		self.ListOfDevices[Devices[Unit].DeviceID]['Heartbeat'] = 0  # Let's force a refresh of Attribute in the next Hearbeat
		OnOff = '01' # 00 = off, 01 = on
		value=z_tools.Hex_Format(2,round(Level*255/100)) #To prevent off state with dimmer, only available with switch
		z_output.sendZigateCmd("0081","02" + Devices[Unit].DeviceID + EPin + EPout + OnOff + value + "0010")
		if DSwitchtype == "16" :
			z_domoticz.UpdateDevice_v2(Devices, Unit, 2, str(Level) ,DOptions, SignalLevel) #Need to use 1 as nvalue else, it will set it to off
		else:
			z_domoticz.UpdateDevice_v2(Devices, Unit, 1, str(Level) ,DOptions, SignalLevel) #Need to use 1 as nvalue else, it will set it to off

	if Command == "Set Color" :
		Domoticz.Debug("onCommand - Set Color - Level = " + str(Level) + " Color = " + str(Color) )
		Hue_List = json.loads(Color)
		
		#Color 
		#	ColorMode m;
		#	uint8_t t;     // Range:0..255, Color temperature (warm / cold ratio, 0 is coldest, 255 is warmest)
		#	uint8_t r;     // Range:0..255, Red level
		#	uint8_t g;     // Range:0..255, Green level
		#	uint8_t b;     // Range:0..255, Blue level
		#	uint8_t cw;    // Range:0..255, Cold white level
		#	uint8_t ww;    // Range:0..255, Warm white level (also used as level for monochrome white)
		#

		def rgb_to_xy(rgb):
			''' convert rgb tuple to xy tuple '''
			red, green, blue = rgb
			r = ((red + 0.055) / (1.0 + 0.055))**2.4 if (red > 0.04045) else (red / 12.92)
			g = ((green + 0.055) / (1.0 + 0.055))**2.4 if (green > 0.04045) else (green / 12.92)
			b = ((blue + 0.055) / (1.0 + 0.055))**2.4 if (blue > 0.04045) else (blue / 12.92)
			X = r * 0.664511 + g * 0.154324 + b * 0.162028
			Y = r * 0.283881 + g * 0.668433 + b * 0.047685
			Z = r * 0.000088 + g * 0.072310 + b * 0.986039
			cx = 0
			cy = 0
			if (X + Y + Z) != 0:
				cx = X / (X + Y + Z)
				cy = Y / (X + Y + Z)
			return (cx, cy)

		def rgb_to_hsl(rgb):
			''' convert rgb tuple to hls tuple '''
			r, g, b = rgb
			r = float(r/255)
			g = float(g/255)
			b = float(b/255)
			high = max(r, g, b)
			low = min(r, g, b)
			h, s, l = ((high + low) / 2,)*3

			if high == low:
				h = 0.0
				s = 0.0
			else:
				d = high - low
				s = d / (2 - high - low) if l > 0.5 else d / (high + low)
				h = {
					r: (g - b) / d + (6 if g < b else 0),
					g: (b - r) / d + 2,
					b: (r - g) / d + 4,
				}[high]
				h /= 6

			return h, s, l

		self.ListOfDevices[Devices[Unit].DeviceID]['Heartbeat'] = 0  # As we update the Device, let's restart and do the next pool in 5'

		#First manage level
		OnOff = '01' # 00 = off, 01 = on
		value=z_tools.Hex_Format(2,round(1+Level*254/100)) #To prevent off state
		z_output.sendZigateCmd("0081","02" + Devices[Unit].DeviceID + EPin + EPout + OnOff + value + "0000")

		#Now color
		#ColorModeNone = 0   // Illegal
		#ColorModeNone = 1   // White. Valid fields: none
		if Hue_List['m'] == 1:
			ww = int(Hue_List['ww']) # Can be used as level for monochrome white
			#TODO : Jamais vu un device avec ca encore
			Domoticz.Debug("Not implemented device color 1")	
		#ColorModeTemp = 2   // White with color temperature. Valid fields: t
		if Hue_List['m'] == 2:
			#Value is in mireds (not kelvin)
			#Correct values are from 153 (6500K) up to 588 (1700K)
			# t is 0 > 255
			TempKelvin = int(((255 - int(Hue_List['t']))*(6500-1700)/255)+1700);
			TempMired = 1000000 // TempKelvin
			z_output.sendZigateCmd("00C0","02" + Devices[Unit].DeviceID + EPin + EPout + z_tools.Hex_Format(4,TempMired) + "0000")
		#ColorModeRGB = 3    // Color. Valid fields: r, g, b.
		elif Hue_List['m'] == 3:
			x, y = rgb_to_xy((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
			#Convert 0>1 to 0>FFFF
			x = int(x*65536)
			y = int(y*65536)																   
			strxy = z_tools.Hex_Format(4,x) + z_tools.Hex_Format(4,y)
			z_output.sendZigateCmd("00B7","02" + Devices[Unit].DeviceID + EPin + EPout + strxy + "0000")
		#ColorModeCustom = 4, // Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
		elif Hue_List['m'] == 4:
			ww = int(Hue_List['ww'])
			cw = int(Hue_List['cw'])
			x, y = rgb_to_xy((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))	
			#TODO, Pas trouve de device avec ca encore ...
			Domoticz.Debug("Not implemented device color 2")
		#With saturation and hue, not seen in domoticz but present on zigate, and some device need it
		elif Hue_List['m'] == 9998:
			h,l,s = rgb_to_hsl((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
			saturation = s * 100   #0 > 100
			hue = h *360	       #0 > 360
			hue = int(hue*254//360)
			saturation = int(saturation*254//100)
			value = int(l * 254//100)
			OnOff = '01'
			z_output.sendZigateCmd("00B6","02" + Devices[Unit].DeviceID + EPin + EPout + z_tools.Hex_Format(2,hue) + z_tools.Hex_Format(2,saturation) + "0000")
			z_output.sendZigateCmd("0081","02" + Devices[Unit].DeviceID + EPin + EPout + OnOff + z_tools.Hex_Format(2,value) + "0010")

		#Update Device
		z_domoticz.UpdateDevice_v2(Devices, Unit, 1, str(value) ,DOptions, SignalLevel, str(Color))


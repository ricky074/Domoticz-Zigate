#!/usr/bin/env python3
# coding: utf-8 -*-
"""
	Module : z_tools.py

	Description: Zigate toolbox
"""
import binascii
import time
import struct
import json

def returnlen(taille , value) :
	while len(value)<taille:
		value="0"+value
	return str(value)


def Hex_Format(taille, value):
	value = hex(int(value))[2:]
	if len(value) > taille:
		return 'f' * taille
	while len(value)<taille:
		value="0"+value
	return str(value)

def IEEEExist(self, IEEE) :
	#check in ListOfDevices for an existing IEEE
	if IEEE :
		if IEEE in self.ListOfDevices and IEEE != '' :
			return True
		else:
			return False

def DeviceExist(self, Addr , IEE = ''):
	import Domoticz

	#Validity check
	if Addr == '':
		return False
	#check in ListOfDevices
	if Addr in self.ListOfDevices:
		if 'Status' in self.ListOfDevices[Addr] :
			return True
	#if gived, test IEE
	#if IEE:
#		for i in self.ListOfDevices:
#			d = self.ListOfDevices[i]
#			Domoticz.Debug(DeviceExist + str(d))
#			if d.get('IEEE','wrong iee') == IEE:
#				Domoticz.Log("DeviceExist - Addr = " + Addr + " IEEE = " + IEE + " already assigned on " + str(d) )
#				Domoticz.Log("DeviceExist - update self.ListOfDevices[" + Addr + "] with " + d )
#				#update adress
#				self.ListOfDevices[Addr] = d
#				del i
#				return True
	#unknow device
	return False


def initDeviceInList(self, Addr) :
	if Addr != '' :
		self.ListOfDevices[Addr]={}
		self.ListOfDevices[Addr]['Ep']={}
		self.ListOfDevices[Addr]['Status']="004d"
		self.ListOfDevices[Addr]['Heartbeat']="0"
		self.ListOfDevices[Addr]['RIA']="0"
		self.ListOfDevices[Addr]['RSSI']={}
		self.ListOfDevices[Addr]['Battery']={}
		self.ListOfDevices[Addr]['Model']={}
		self.ListOfDevices[Addr]['MacCapa']={}
		self.ListOfDevices[Addr]['IEEE']={}
		self.ListOfDevices[Addr]['Type']={}
		self.ListOfDevices[Addr]['ProfileID']={}
		self.ListOfDevices[Addr]['ZDeviceID']={}


def CheckDeviceList(self, key, val) :
	import Domoticz

	Domoticz.Debug("CheckDeviceList - Address search : " + str(key))
	Domoticz.Debug("CheckDeviceList - with value : " + str(val))

	DeviceListVal=eval(val)
	if DeviceExist(self, key, DeviceListVal.get('IEEE','')) == False :
		Domoticz.Debug("CheckDeviceList - Address will be add : " + str(key))
		initDeviceInList(self, key)
		self.ListOfDevices[key]['RIA']="10"
		if 'Ep' in DeviceListVal :
			self.ListOfDevices[key]['Ep']=DeviceListVal['Ep']
		if 'Type' in DeviceListVal :
			self.ListOfDevices[key]['Type']=DeviceListVal['Type']
		if 'Model' in DeviceListVal :
			self.ListOfDevices[key]['Model']=DeviceListVal['Model']
		if 'MacCapa' in DeviceListVal :
			self.ListOfDevices[key]['MacCapa']=DeviceListVal['MacCapa']
		if 'IEEE' in DeviceListVal :
			self.ListOfDevices[key]['IEEE']=DeviceListVal['IEEE']
		if 'ProfileID' in DeviceListVal :
			self.ListOfDevices[key]['ProfileID']=DeviceListVal['ProfileID']
		if 'ZDeviceID' in DeviceListVal :
			self.ListOfDevices[key]['ZDeviceID']=DeviceListVal['ZDeviceID']
		if 'Status' in DeviceListVal :
			self.ListOfDevices[key]['Status']=DeviceListVal['Status']
		if 'RSSI' in DeviceListVal :
			self.ListOfDevices[key]['RSSI']=DeviceListVal['RSSI']

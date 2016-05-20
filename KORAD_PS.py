# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 23:05:05 2014

@author: jason
"""

from Tkinter import *
from ttk import *
import Tkinter as ttk
import tkMessageBox
import serial
import time
import struct

#==============================================================================
# Define protocol commands
#==============================================================================
REQUEST_STATUS = b"STATUS?"  # Request actual status.
    # 0x40 (Output mode: 1:on, 0:off)
    # 0x20 (OVP and/or OCP mode: 1:on, 0:off)
    # 0x01 (CV/CC mode: 1:CV, 0:CC)
REQUEST_ID = b"*IDN?"

REQUEST_SET_VOLTAGE = b"VSET"  # request the set voltage
REQUEST_ACTUAL_VOLTAGE = b"VOUT"  # Request output voltage

REQUEST_SET_CURRENT = b"ISET"  # Request the set current
REQUEST_ACTUAL_CURRENT = b"IOUT"  # Requst the output current

SET_VOLTAGE = b"VSET"  # Set the maximum output voltage
SET_CURRENT = b"ISET"  # Set the maximum output current

SET_OUTPUT = b"OUT"  # Enable the power output

SET_OVP = b"OVP"  # Enable(1)/Disable(0) OverVoltageProtection

SET_OCP = b"OCP"  # Enable(1)/Disable(0) OverCurrentProtection

RCL_MEM = b"RCL"
SAV_MEM = b"SAV"

BEEP = b"BEEP"
LOCK = b"LOCK"

TRACK_SERIES = b"TRACK"

status = {
    "ch1_mode"  : 0,    # 0==CC, 1==CV
    "ch2_mode"  : 0,    # 0==CC, 1==CV
    "tracking"  : 0,    # 00==Indep, 01==Series, 10=Parrallel
    "ovp_mode"  : 0,    #
    "ocp_mode"  : 0,    #
    "output1"   : 0,    # 0==Off, 1==On
    "output2"   : 0     # 0==Off, 1==On
    #"output"   : 0     # 0==Off, 1==On
    #"lock"     : 0,    # 0==Locked, 1==Unlocked
    #"beep"     : 0,    # 0==Off, 1==On

}

#==============================================================================
# Methods
#==============================================================================

def Lock_Device(value):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    request_string = "{0}{1}?".format(LOCK,value)
    PS.write(request_string)  # Request the target voltage
    #Get_Status()

def Beep_Off(value):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    request_string = "{0}{1}?".format(BEEP,value)
    PS.write(request_string)  # Request the target voltage
    #Get_Status()

def GetID():
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    PS.write(REQUEST_ID)  # Request the ID from the Power Supply
    PSID = PS.read(16)
    PS.flushInput()
    return(PSID)


def Get_I_Set(channel):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    request_string = "{0}{1}?".format(REQUEST_SET_CURRENT,channel)
    PS.write(request_string)  # Request the target current
    I_set = PS.read(5)
    if (I_set == b''):
        I_set = b'0'
    I_set = float(I_set)
    print(str('Current is set to ')+str(I_set))
    PS.flushInput()
    return(I_set)


def Get_V_Set(channel):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    request_string = "{0}{1}?".format(REQUEST_SET_VOLTAGE,channel)
    PS.write(request_string)  # Request the target voltage
    V_set = float(PS.read(5))
    print(str('Voltage is set to ')+str(V_set))
    PS.flushInput()
    return(V_set)


def Get_Status():
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    PS.write(REQUEST_STATUS)  # Request the status of the PS
    Stat = str(PS.read(1)).encode('hex')
    update_status(Stat)
    PS.flushInput()
    return(Stat)

def update_status(stat):
    scale = 16 ## equals to hexadecimal
    num_of_bits = 8
    stat_bin = bin(int(stat, scale))[2:].zfill(num_of_bits)

    status["ch1_mode"]  = int(stat_bin[7])
    status["ch2_mode"]  = int(stat_bin[6])
    status["tracking"]  = int(stat_bin[4]+stat_bin[5],2)
    status["ovp_mode"]  = int(stat_bin[3])
    status["ocp_mode"]  = int(stat_bin[2])
    status["output1"]   = int(stat_bin[1])
    status["output2"]   = int(stat_bin[0])

def SetVoltage(channel,Voltage):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    if (float(Voltage) > float(VMAX)):
        Voltage = VMAX
    Voltage = "{:2.2f}".format(float(Voltage))
    request_string = "{0}{1}:".format(SET_VOLTAGE,channel)
    Output_string = request_string + bytes(Voltage)
    PS.write(Output_string)
    print(Output_string)
    PS.flushInput()
    time.sleep(0.2)
    VeriVolt = "{:2.2f}".format(float(Get_V_Set(channel)))  # Verify PS accepted
        # the setting
#    print(VeriVolt)
#    print(Voltage)
    while (VeriVolt != Voltage):
        PS.write(Output_string)  # Try one more time
    if ( channel == 1 ):
        vEntry.delete(0, 5)
        vEntry.insert(0, "{:2.2f}".format(float(VeriVolt)))
    if ( channel == 2 ):
        v2Entry.delete(0, 5)
        v2Entry.insert(0, "{:2.2f}".format(float(VeriVolt)))
    return(Output_string)


def SetCurrent(channel,Current):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    if (float(Current) > float(IMAX)):
        Current = IMAX
    Current = "{:2.3f}".format(float(Current))
    request_string = "{0}{1}:".format(SET_CURRENT,channel)
    Output_string = request_string + bytes(Current)
    PS.write(Output_string)
    print(Output_string)
    PS.flushInput()
    time.sleep(0.2)
    VeriAmp = "{:2.3f}".format(float(Get_I_Set(channel)))
    if (VeriAmp != Current):
        VeriAmp = 0.00
    if ( channel == 1 ):
        iEntry.delete(0, 5)
        iEntry.insert(0, "{:2.3f}".format(float(VeriAmp)))
    if ( channel == 2 ):
        i2Entry.delete(0, 5)
        i2Entry.insert(0, "{:2.3f}".format(float(VeriAmp)))
    return(Output_string)


def V_Actual(channel):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    request_string = "{0}{1}?".format(REQUEST_ACTUAL_VOLTAGE,channel)
    PS.write(request_string)  # Request the actual voltage
    time.sleep(0.015)
    V_actual = PS.read(5)
    if (V_actual == b''):
            V_actual = b'0'  # deal with the occasional NULL from PS
#    print('V_actual = ' + str(V_actual))
    V_actual = float(V_actual)
    PS.flushInput()
    return(V_actual)


def I_Actual(channel):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    request_string = "{0}{1}?".format(REQUEST_ACTUAL_CURRENT,channel)
    PS.write(request_string)  # Request the actual current
    time.sleep(0.015)
    I_actual = PS.read(5)
    if (I_actual == b''):
            I_actual = b'0'  # deal with the occasional NULL from PS
    I_actual = float(I_actual)
    PS.flushInput()
    return(I_actual)

def ToggleOP():
    Get_Status()
    if ( status["output1"] == 1 ):
        Output_string = SetOP('0')
    if ( status["output1"] == 0 ):
        Output_string = SetOP('1')
    return(Output_string)

def SetOP(OnOff):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()

    Output_string = SET_OUTPUT + bytes(OnOff)

    PS.write(Output_string)
    print(Output_string)
    PS.flushInput()
    return(Output_string)


def ToggleOVP():
    Get_Status()
    if ( status["ovp_mode"] == 1 ):
        Output_string = SetOVP(b'0')
    if ( status["ovp_mode"] == 0 ):
        Output_string = SetOVP(b'1')
    return(Output_string)

def SetOVP(OnOff):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    Output_string = SET_OVP + OnOff
    PS.write(Output_string)
    print(Output_string)
    PS.flushInput()
    return(Output_string)

def ToggleOCP():
    Get_Status()
    if ( status["ocp_mode"] == 1 ):
        Output_string = SetOCP(b'0')
    if ( status["ocp_mode"] == 0 ):
        Output_string = SetOCP(b'1')
    return(Output_string)

def SetOCP(OnOff):
    PS = serial.Serial("/dev/ttyACM0",
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       timeout=1)
    PS.flushInput()
    Output_string = SET_OCP + OnOff
    PS.write(Output_string)
    print(Output_string)
    PS.flushInput()
    return(Output_string)

def Update_VandI():
#    print(V_Actual())
    V_actual = "{:2.2f}".format(V_Actual(1))
    vReadoutLabel.configure(text="{} {}".format(V_actual, 'V'))
    V2_actual = "{:2.2f}".format(V_Actual(2))
    vReadout2Label.configure(text="{} {}".format(V2_actual, 'V'))
#    print(V_actual)

    I_actual = "{0:.3f}".format(I_Actual(1))
    iReadoutLabel.configure(text="{} {}".format(I_actual, 'A'))
    I2_actual = "{0:.3f}".format(I_Actual(2))
    iReadout2Label.configure(text="{} {}".format(I2_actual, 'A'))
#    print(I_actual)


def Application_Loop():
#        print('application loop run')
        app.after(75, Update_VandI)
        app.after(100, Application_Loop)


def SetVA():
    Volts = vEntry.get()
    SetVoltage(1,Volts)

    Amps = iEntry.get()
    if (Amps == ''):
        Amps = b'0'
        print('changed Amps1 to 0')
    Amps = "{0:.3f}".format(float(Amps))
    SetCurrent(1,Amps)

    Volts2 = v2Entry.get()
    SetVoltage(2,Volts2)

    Amps2 = i2Entry.get()
    if (Amps2 == ''):
        Amps2 = b'0'
        print('changed Amps2 to 0')
    Amps2 = "{0:.3f}".format(float(Amps2))
    SetCurrent(2,Amps2)

def MemSet(MemNum):
    print(MemNum)


#==============================================================================
# Variables
#==============================================================================
V_set = "{0:.2f}".format(Get_V_Set(1), 'V')
I_set = "{0:.3f}".format(Get_I_Set(1), 'I')
V2_set = "{0:.2f}".format(Get_V_Set(2), 'V')
I2_set = "{0:.3f}".format(Get_I_Set(2), 'I')
PSID = GetID()
Lock_Device(1)
#Beep_Off(1)
Stat = Get_Status()
print(b'PSID = '+PSID)
print('Status = '+Stat)
VMAX = '31'
IMAX = '5.1'


#==============================================================================
# Create Window
#==============================================================================
app = Tk()
app.geometry("700x280+1200+1200")
app.title('TK Experiment')

# Actual Readout area
#==============================================================================
actualLabel = ttk.Label(app)
actualLabel.grid(row=0, column=0, sticky='W', padx=50, pady=10)
actualLabel.configure(text='Actual Values')


channel1Label = ttk.Label(app)
channel1Label.grid(row=1, column=0, sticky='W', padx=50, pady=10)
channel1Label.configure(text='Channel 1')
vReadoutLabel = ttk.Label(app, text="unknown")
vReadoutLabel.grid(row=2, column=0, sticky='E', padx=50, pady=5)
iReadoutLabel = ttk.Label(app, text="unknown")
iReadoutLabel.grid(row=3, column=0, sticky='E', padx=50, pady=0)


channel2Label = ttk.Label(app)
channel2Label.grid(row=1, column=1, sticky='W', padx=50, pady=10)
channel2Label.configure(text='Channel 2')
vReadout2Label = ttk.Label(app, text="unknown")
vReadout2Label.grid(row=2, column=1, sticky='E', padx=50, pady=5)
iReadout2Label = ttk.Label(app, text="unknown")
iReadout2Label.grid(row=3, column=1, sticky='E', padx=50, pady=0)

#spacerLabel = ttk.Label(app, text="         ")
#spacerLabel.grid(row=0, column=1, sticky=N)

# Set textentry area
#==============================================================================
setValLabel = ttk.Label(app, text="Set")
setValLabel.grid(row=0, column=2, sticky='N', padx=50, pady=10)

setSetCh1Label = ttk.Label(app, text="Channel 1")
setSetCh1Label.grid(row=1, column=2, sticky='N', padx=50, pady=10)
Volts = StringVar(name=str(V_set))
vEntry = Entry(app, textvariable=Volts)
vEntry.delete(0, 5)
vEntry.insert(0, Volts)
vEntry["width"] = 5
vEntry.grid(row=2, column=2, sticky='E', padx=50, pady=0)
#Amps = vEntry.get()
Amps = StringVar(name=str(I_set))
iEntry = Entry(app, textvariable=Amps)
iEntry.delete(0, 5)
iEntry.insert(0, Amps)
iEntry["width"] = 5
iEntry.grid(row=3, column=2, sticky='E', padx=50, pady=0)
#Amps = iEntry.get()


setSetCh2Label = ttk.Label(app, text="Channel 2")
setSetCh2Label.grid(row=1, column=3, sticky='N', padx=50, pady=10)
Volts2 = StringVar(name=str(V2_set))
v2Entry = Entry(app, textvariable=Volts2)
v2Entry.delete(0, 5)
v2Entry.insert(0, Volts2)
v2Entry["width"] = 5
v2Entry.grid(row=2, column=3, sticky='E', padx=50, pady=0)
#Amps2 = v2Entry.get()
Amps2 = StringVar(name=str(I2_set))
i2Entry = Entry(app, textvariable=Amps2)
i2Entry.delete(0, 5)
i2Entry.insert(0, Amps2)
i2Entry["width"] = 5
i2Entry.grid(row=3, column=3, sticky='E', padx=50, pady=0)
#Amps = iEntry.get()

 #Button Area
#==============================================================================
Op_On_Button = Button(app)
Op_On_Button.configure(text='On/Off')
Op_On_Button.grid(row=5, column=1, sticky='N')
Op_On_Button.configure(command=lambda: ToggleOP())


#Op_Off_Button = Button(app)
#Op_Off_Button.configure(text='Turn OP Off')
#Op_Off_Button.grid(row=6, column=1, sticky='N')
#Op_Off_Button.configure(command=lambda: SetOP('0'))


Set_Button = Button(app)
Set_Button.configure(text='Set V & I')
Set_Button.grid(row=5, column=2, sticky='N')
Set_Button.configure(command=lambda: SetVA())


OVP_Button = Button(app)
OVP_Button.configure(text='OVP')
OVP_Button.grid(row=5, column=0, sticky='W')
OVP_Button.configure(command=lambda: ToggleOVP())


#OVP_Button = Button(app)
#OVP_Button.configure(text='OVP OFF')
#OVP_Button.grid(row=6, column=0, sticky='W')
#OVP_Button.configure(command=lambda: SetOVP(b'0'))


OCP_Button = Button(app)
OCP_Button.configure(text='OCP')
OCP_Button.grid(row=7, column=0, sticky='W')
OCP_Button.configure(command=lambda: ToggleOCP())


#OCP_Button = Button(app)
#OCP_Button.configure(text='OCP OFF')
#OCP_Button.grid(row=8, column=0, sticky='W')
#OCP_Button.configure(command=lambda: SetOCP(b'0'))


#==============================================================================
# Loop
#==============================================================================
# Update_VandI()
Application_Loop()
app.mainloop()

Lock_Device(0)

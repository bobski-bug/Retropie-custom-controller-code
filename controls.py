#!/usr/bin/python3

import time
import RPi.GPIO as GPIO
import spidev
import uinput

GPIO.setwarnings(False)

# Pins associated with corresponding button
DPadUp = 2
DPadDown = 13
DPadLeft = 17
DPadRight = 3
Select = 27
Start = 22
AButton = 23
BButton = 24
XButton = 25
YButton = 16
LeftBumper = 5
LeftTrigger = 6
RightBumper = 26
RightTrigger = 12

#set up GPIO Pins for buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(DPadUp, GPIO.IN, pull_up_down=GPIO.PUD_UP) #D-pad up
GPIO.setup(DPadDown, GPIO.IN, pull_up_down=GPIO.PUD_UP) #D-pad down
GPIO.setup(DPadLeft, GPIO.IN, pull_up_down=GPIO.PUD_UP) #D-pad left
GPIO.setup(DPadRight, GPIO.IN, pull_up_down=GPIO.PUD_UP) #D-pad right
GPIO.setup(Select, GPIO.IN, pull_up_down=GPIO.PUD_UP) #select
GPIO.setup(Start, GPIO.IN, pull_up_down=GPIO.PUD_UP) #start
GPIO.setup(AButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) #a
GPIO.setup(BButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) #b
GPIO.setup(XButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) #x
GPIO.setup(YButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) #y
GPIO.setup(LeftBumper, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Left bumper
GPIO.setup(LeftTrigger, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Left trigger
GPIO.setup(RightBumper, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Right bumper
GPIO.setup(RightTrigger, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Right trigger

#set up SPI for analog joystick
# Define Axis Channels (channel 3 to 7 can be assigned for more buttons / joysticks)
LX_channel = 1
LY_channel = 2
RX_channel = 4
RY_channel = 5

#Time delay, which tells how many seconds the value is read out
delay = 0.5
 
# Spi oeffnen
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
# Function for reading the MCP3008 channel between 0 and 7
def readChannel(channel):
  val = spi.xfer2([1,(8+channel)<<4,0])
  data = ((val[1]&3) << 8) + val[2]
#  print (channel, data )
  return data

# Creating the virtual gamepad
events = (
	uinput.BTN_DPAD_UP,
	uinput.BTN_DPAD_DOWN,
	uinput.BTN_DPAD_LEFT,
	uinput.BTN_DPAD_RIGHT,
	uinput.BTN_SELECT,
	uinput.BTN_START,
	uinput.BTN_A,
	uinput.BTN_B,
	uinput.BTN_X,
	uinput.BTN_Y,
	uinput.BTN_TL,
	uinput.BTN_TL2,
	uinput.BTN_TR,
	uinput.BTN_TR2,
	uinput.ABS_X  + (0, 255, 0, 0),
	uinput.ABS_Y  + (0, 255, 0, 0),
	uinput.ABS_RX + (0, 255, 0, 0),
	uinput.ABS_RY + (0, 255, 0, 0)	
)

device = uinput.Device(events)

#x_max = 740 #empirically determined maximum 10 bit x value
#x_mid_high = 465 #empirically determined upper center 10 bit x value
#x_mid_low = 435 #empirically determined lower center 10 bit x value
#x_min = 140 #empirically determined minimum 10 bit x value
#x_read = 450 #start x at center 
x_max = 900 #empirically determined maximum 10 bit x value
x_mid_high = 520 #empirically determined upper center 10 bit x value
x_mid_low = 480 #empirically determined lower center 10 bit x value
x_min = 100 #empirically determined minimum 10 bit x value
x_read = 500 #start x at center 

#y_max = 740 #empirically determined maximum 10 bit y value
#y_mid_high = 465 #empirically determined lower center 10 bit y value
#y_mid_low = 435 #empirically determined lower center 10 bit y value
#y_min = 140 #empirically determined minimum 10 bit y value
#y_read = 450 #start y at center

y_max = 900 #empirically determined maximum 10 bit y value
y_mid_high = 520 #empirically determined lower center 10 bit y value
y_mid_low = 480 #empirically determined lower center 10 bit y value
y_min = 100 #empirically determined minimum 10 bit y value
y_read = 500 #start y at center

# Center joystick output 
# syn=False to emit an "atomic" (128, 128) event.
x_value = 128 #8 bit center
y_value = 128 #8 bit center
device.emit(uinput.ABS_X, x_value, syn=False)
device.emit(uinput.ABS_Y, y_value)
device.emit(uinput.ABS_RX, x_value, syn=False)
device.emit(uinput.ABS_RY, y_value)

try:
	while True:
		xl_read = readChannel(LX_channel)
		if x_mid_low <= xl_read and xl_read <= x_mid_high:	#x_read between x_mid_low and x_mid_high is automatically centered
			xl_value = 128
		elif xl_read < x_min:	#x_read below x_min is autmatically minimum
			xl_value = 255
		elif xl_read < x_mid_low:	#x_read less than x_mid_low scaled between 0-127:x_min-x_mid_low
			xl_value = 255-(xl_read-x_min)*127/(x_mid_low-x_min)
		elif xl_read > x_max:	#x_read above x_max is autmatically maximum
			xl_value = 0
		elif xl_read > x_mid_high:	#x_read greater than x_mid_high scaled between 128-255:x_mid_high-x_max
			xl_value = 127-(xl_read-x_mid_high)*127/(x_max-x_mid_high)
		device.emit(uinput.ABS_X, int(xl_value), syn=False)

		yl_read = readChannel(LY_channel)
		if y_mid_low <= yl_read and yl_read <= y_mid_high:	#y_read between y_mid_low and y_mid_high is automatically centered
			yl_value = 128 
		if yl_read < y_mid_low:	#y_read less than y_mid_low scaled between 0-127:y_min-y_mid_low
			yl_value = (yl_read-y_min)*127/(y_mid_low-y_min)
		if yl_read < y_min:	#y_read below y_min is autmatically minimum
			yl_value = 0
		if yl_read > y_mid_high:	#y_read greater than y_mid_high scaled between 128-255:y_mid_high-y_max
			yl_value = 128+(yl_read-y_mid_high)*127/(y_max-y_mid_high)
		if yl_read > y_max:	#x_read above y_max is autmatically maximum
			yl_value = 255
		device.emit(uinput.ABS_Y, int(yl_value))

		xr_read = readChannel(RX_channel)
		if x_mid_low <= xr_read and xr_read <= x_mid_high:	#x_read between x_mid_low and x_mid_high is automatically centered
		 	xr_value = 128
		if xr_read < x_mid_low:	#x_read less than x_mid_low scaled between 0-127:x_min-x_mid_low
		 	xr_value = 255-(xr_read-x_min)*127/(x_mid_low-x_min)
		if xr_read < x_min:	#x_read below x_min is autmatically minimum
		 	xr_value = 255
		if xr_read > x_mid_high:	#x_read greater than x_mid_high scaled between 128-255:x_mid_high-x_max
		 	xr_value = 127-(xr_read-x_mid_high)*127/(x_max-x_mid_high)
		if xr_read > x_max:	#x_read above x_max is autmatically maximum
		 	xr_value = 0
		device.emit(uinput.ABS_RX, int(xr_value), syn=False)

		yr_read = readChannel(RY_channel)
		if y_mid_low <= yr_read and yr_read <= y_mid_high:	#y_read between y_mid_low and y_mid_high is automatically centered
		 	yr_value = 128 
		if yr_read < y_mid_low:	#y_read less than y_mid_low scaled between 0-127:y_min-y_mid_low
		 	yr_value = (yr_read-y_min)*127/(y_mid_low-y_min)
		if yr_read < y_min:	#y_read below y_min is autmatically minimum
		 	yr_value = 0
		if yr_read > y_mid_high:	#y_read greater than y_mid_high scaled between 128-255:y_mid_high-y_max
		 	yr_value = 128+(yr_read-y_mid_high)*127/(y_max-y_mid_high)
		if yr_read > y_max:	#x_read above y_max is autmatically maximum
		 	yr_value = 255
		device.emit(uinput.ABS_RY, int(yr_value))

		#print("Left  X axis: {}  Y axis : {}".format(int(xl_value),int(yl_value)),"Right X axis: {}  Y axis : {}".format(int(xr_value),int(yr_value)))

		if GPIO.input(DPadUp) == GPIO.LOW:
			#print("D-pad up pressed")
			device.emit(uinput.BTN_DPAD_UP, 1)
		else:
			device.emit(uinput.BTN_DPAD_UP, 0)
		
		if GPIO.input(DPadDown) == GPIO.LOW:
			#print("D-pad down pressed")
			device.emit(uinput.BTN_DPAD_DOWN, 1)
		else:
			device.emit(uinput.BTN_DPAD_DOWN, 0)

		if GPIO.input(DPadLeft) == GPIO.LOW:
			#print("D-pad left pressed")
			device.emit(uinput.BTN_DPAD_LEFT, 1)
		else:
			device.emit(uinput.BTN_DPAD_LEFT, 0)

		if GPIO.input(DPadRight) == GPIO.LOW:
			#print("D-pad right pressed")
			device.emit(uinput.BTN_DPAD_RIGHT, 1)
		else:
			device.emit(uinput.BTN_DPAD_RIGHT, 0)

		if GPIO.input(Select) == GPIO.LOW:
			#print("Select button pressed")
			device.emit(uinput.BTN_SELECT, 1)
		else:
			device.emit(uinput.BTN_SELECT, 0)

		if GPIO.input(Start) == GPIO.LOW:
			#print("Start button pressed")
			device.emit(uinput.BTN_START, 1)
		else:
			device.emit(uinput.BTN_START, 0)

		if GPIO.input(AButton) == GPIO.LOW:
			#print("A button pressed")
			device.emit(uinput.BTN_A, 1)
		else:
			device.emit(uinput.BTN_A, 0)

		if GPIO.input(BButton) == GPIO.LOW:
			#print("B button pressed")
			device.emit(uinput.BTN_B, 1)
		else:
			device.emit(uinput.BTN_B, 0)

		if GPIO.input(XButton) == GPIO.LOW:
			#print("X button pressed")
			device.emit(uinput.BTN_X, 1)
		else:
			device.emit(uinput.BTN_X, 0)

		if GPIO.input(YButton) == GPIO.LOW:
			#print("Y button pressed")
			device.emit(uinput.BTN_Y, 1)
		else:
			device.emit(uinput.BTN_Y, 0)

		if GPIO.input(LeftBumper) == GPIO.LOW:
			#print("Left bumper up pressed")
			device.emit(uinput.BTN_TL, 1)
		else:
			device.emit(uinput.BTN_TL, 0)

		if GPIO.input(LeftTrigger) == GPIO.LOW:
			#print("Left trigger up pressed")
			device.emit(uinput.BTN_TL2, 1)
		else:
			device.emit(uinput.BTN_TL2, 0)

		if GPIO.input(RightBumper) == GPIO.LOW:
			#print("Right bumper up pressed")
			device.emit(uinput.BTN_TR, 1)
		else:
			device.emit(uinput.BTN_TR, 0)

		if GPIO.input(RightTrigger) == GPIO.LOW:
			#print("Right trigger pressed")
			device.emit(uinput.BTN_TR2, 1)
		else:
			device.emit(uinput.BTN_TR2, 0)
		
		time.sleep(0.1)
except KeyboardInterrupt:
	GPIO.cleanup()
	device.destroy()

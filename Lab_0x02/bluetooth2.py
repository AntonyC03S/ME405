from pyb import UART, Pin

# Make a serial port object from the UART class
BT_ser = UART(1, 115200)

# Deconfigure default pins
Pin(Pin.B6,  mode=Pin.ANALOG)     # Set pin modes back to default
Pin(Pin.B7,  mode=Pin.ANALOG)

# Configure the selected pins in coordination with the alternate function table
Pin(Pin.A9,  mode=Pin.ALT, alt=7) # Set pin modes to UART matching column 7 in alt. fcn. table
Pin(Pin.A10, mode=Pin.ALT, alt=7)

while True:
    if BT_ser.any():               # Check if any data is available
        data = BT_ser.read()       # Read all available data
        BT_ser.write(data)         # Echo the data back
    else:
        pass                          # Do nothing and loop
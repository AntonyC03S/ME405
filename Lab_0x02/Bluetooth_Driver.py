from pyb import Pin, UART 

class Bluetooth:
    "''A Bluetooth communication interface encapsulated in a Python class'''"

    def __init__(self, uart_num: int, tx_pin: Pin, rx_pin: Pin, def_1: Pin, def_2: Pin, baudrate: int = 115200):
        '''Initializes a Bluetooth object'''
        self._uart = UART(uart_num, baudrate=baudrate)

        # Deconfigure default pins
        self._def_1 = Pin(def_1,  mode=Pin.ANALOG)     # Set pin modes back to default
        self._def_2 = Pin(def_2,  mode=Pin.ANALOG)

        # Configure the selected pins in coordination with the alternate function table
        self._rx_pin = Pin(rx_pin,  mode=Pin.ALT, alt=7) # Set pin modes to UART matching column 7 in alt. fcn. table
        self._tx_pin = Pin(tx_pin, mode=Pin.ALT, alt=7)

    def send_line(self,s):
        # ensure CRLF termination
        if not s.endswith('\\n'):
            s = s + '\\r\\n'
        self._uart.write(s)
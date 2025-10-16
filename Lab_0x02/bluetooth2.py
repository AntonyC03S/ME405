# bluetooth2.py  (MicroPython on Nucleo / Pyboard-like board)
from pyb import UART, Pin
from time import sleep_ms, ticks_ms, ticks_diff

# Configure UART1 pins per your board's layout (adjust if needed)
# NOTE: On some Nucleo boards, UART pin names differ; adapt to your board.
# Deconfigure default pins if using Pyboard-style Pin API (may be board-specific)
try:
    Pin(Pin.cpu.B6, mode=Pin.ANALOG)
    Pin(Pin.cpu.B7, mode=Pin.ANALOG)
except Exception:
    pass

# Initialize UART1 at 115200
BT_ser = UART(1, 115200)

# Helper to send a line
def send_line(s):
    # ensure CRLF termination
    if not s.endswith('\\n'):
        s = s + '\\r\\n'
    BT_ser.write(s)

print('UART ready, waiting for command')

while True:
    # Wait for command line (non-blocking polling)
    if BT_ser.any():
        line = BT_ser.readline()
        if not line:
            sleep_ms(10)
            continue
        try:
            cmd = line.decode().strip()
        except Exception:
            cmd = ''
        if cmd.lower() == 'c':
            # Start streaming data
            send_line('time,value')   # header
            t0 = ticks_ms()
            # stream for a while (or until another command received)
            while True:
                # If PC sent any data, check if it requested stop
                if BT_ser.any():
                    try:
                        r = BT_ser.readline().decode().strip()
                    except Exception:
                        r = ''
                    if r.lower() == 's':  # stop command (optional)
                        send_line('stopped')
                        break

                # produce a sample (example uses millis and a simple sine or counter)
                t = ticks_diff(ticks_ms(), t0) / 1000.0  # seconds
                # Replace the value below with your measurement (encoder count, etc.)
                value = 0.0
                send_line('{:.6f},{:.6f}'.format(t, value))

                # small sleep so the UART buffer and CPU are not overwhelmed
                sleep_ms(50)

        else:
            # Unexpected command; echo or ignore
            send_line('unknown command: {}'.format(cmd))
    else:
        # Nothing received, yield CPU a bit
        sleep_ms(50)
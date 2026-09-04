import struct
import time
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('127.0.0.1', port=5020)
if not client.connect():
    print("[ERROR] Brak polaczenia!")
    exit(1)

SAMPLE_TIME = 0.5
valve_open = False

try:
    next_tick = time.monotonic()
    while True:
        # Odczyt poziomu (IR 0)
        rr_level = client.read_input_registers(address=0, count=1)
        if rr_level.isError():
            continue
        level = rr_level.registers[0]

        # Bonus 2: Dekodowanie Float32 cisnienia z dwoch Holding Registers (1 i 2)
        rr_press = client.read_holding_registers(address=1, count=2)
        pressure = 0.0
        if not rr_press.isError():
            raw = struct.pack('>HH', rr_press.registers[0], rr_press.registers[1])
            pressure = struct.unpack('>f', raw)[0]

        # Logika histerezy
        if level > 800 and not valve_open:
            client.write_coil(0, True)
            valve_open = True
        elif level < 300 and valve_open:
            client.write_coil(0, False)
            valve_open = False

        # Bonus 1: Terminalowy pasek dynamiki
        bar = "#" * (level // 40)
        v_tag = "[OPEN]" if valve_open else "[----]"
        print(f"[{level:4d} l] |{bar:<25}| P={pressure:.2f} bar {v_tag}")

        next_tick += SAMPLE_TIME
        time.sleep(max(0.0, next_tick - time.monotonic()))

except KeyboardInterrupt:
    print("\n[STOP] Zatrzymano.")
finally:
    client.write_coil(0, False)
    client.close()

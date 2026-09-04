import time
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('127.0.0.1', port=5020)

if not client.connect():
    print("[ERROR] Brak polaczenia ze sterownikiem!")
    exit(1)

SAMPLE_TIME = 0.5
valve_open = False

try:
    next_tick = time.monotonic()
    print("[RUN] Pętla regulacji aktywna. Ctrl+C, aby przerwac.\n")

    while True:
        rr = client.read_input_registers(address=0, count=1)
        if rr.isError():
            print(f"[WARN] Blad odczytu: {rr}")
            continue

        level = rr.registers[0]

        # Logika histerezy z pamiecia stanu
        if level > 800 and not valve_open:
            client.write_coil(address=0, value=True)
            valve_open = True
        elif level < 300 and valve_open:
            client.write_coil(address=0, value=False)
            valve_open = False

        status = "OTWARTY" if valve_open else "ZAMKNIETY"
        print(f"Poziom: {level:4d} l | Zawor: {status:<9}")

        next_tick += SAMPLE_TIME
        time.sleep(max(0.0, next_tick - time.monotonic()))

except KeyboardInterrupt:
    print("\n[STOP] Zatrzymano pętlę regulacji.")

finally:
    # Fail-Safe: zamykamy zawor spustowy
    client.write_coil(address=0, value=False)
    client.close()
    print("[CLEANUP] Zawor zamkniety. Polaczenie zakonczone.")

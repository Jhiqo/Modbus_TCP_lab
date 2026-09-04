import time
from pymodbus.client import ModbusTcpClient

# Konfiguracja polaczenia z wezlem Modbus TCP
TARGET_IP = '127.0.0.1'  # Zmien na IP laptopa prowadzacej/kolegi przy zadaniach sieciowych
TARGET_PORT = 5020
SAMPLE_TIME = 0.5        # Krok dyskretyzacji Ts = 500 ms

client = ModbusTcpClient(TARGET_IP, port=TARGET_PORT)

if not client.connect():
    print(f"[ERROR] Brak komunikacji ze sterownikiem pod adresem {TARGET_IP}:{TARGET_PORT}!")
    exit(1)

print(f"[OK] Polaczono ze sterownikiem {TARGET_IP}:{TARGET_PORT}")
valve_open = False  # Pamiec stanu zaworu w regulatorze
is_running = True

try:
    next_tick = time.monotonic()

    while is_running:
        # -------------------------------------------------------------
        # TODO 1: Odczytaj biezacy poziom cieczy z Input Register 0
        # Wskazowka: 
        # rr = client.read_input_registers(address=0, count=1)
        # if not rr.isError():
        #     level = rr.registers[0]
        # -------------------------------------------------------------
        level = 0  # Zamien na wlasciwy odczyt

        # -------------------------------------------------------------
        # TODO 2: Zaimplementuj automat regulacji dwupołożeniowej z histereza:
        #   - Jesli poziom > 800 i zawor jest zamkniety -> otworz zawor (Coil 0 -> True)
        #   - Jesli poziom < 300 i zawor jest otwarty   -> zamknij zawor (Coil 0 -> False)
        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        # TODO 3: Wypisz biezacy stan procesu w konsoli:
        # print(f"Poziom: {level:4d} l | Zawor: {valve_open}")
        # -------------------------------------------------------------

        # Kompensacja opoznien magistrali sieciowej (staly okres Ts):
        next_tick += SAMPLE_TIME
        time.sleep(max(0.0, next_tick - time.monotonic()))

except KeyboardInterrupt:
    print("\n[STOP] Zatrzymano petle regulacji przez operatora.")

finally:
    # -----------------------------------------------------------------
    # TODO 4 (FAIL-SAFE): Wymus stan bezpieczny obiektu (zamkniecie zaworu)
    # przed zamknieciem polaczenia TCP!
    # client.write_coil(address=0, value=False)
    # -----------------------------------------------------------------
    client.close()
    print("[CLEANUP] Polaczenie Modbus zamkniete bezpiecznie.")

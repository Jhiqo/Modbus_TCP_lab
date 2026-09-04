import struct
from pymodbus.client import ModbusTcpClient

# Polaczenie z wezlem Modbus
client = ModbusTcpClient('127.0.0.1', port=5020)

if not client.connect():
    print("[ERROR] Brak polaczenia ze sterownikiem!")
    exit(1)

# -------------------------------------------------------------------------
# ZADANIE BONUSOWE: Dekodowanie Float32 (IEEE 754) z dwoch rejestrow 16-bit
# -------------------------------------------------------------------------
# Serwer tankuje cisnienie hydrostatyczne [bar] do dwoch kolejnych rejestrow:
# Holding Register 1 oraz Holding Register 2.
#
# Twoim zadaniem jest:
# 1. Odczytanie 2 rejestrow poczawszy od adresu 1 (client.read_holding_registers).
# 2. Spakowanie dwoch liczb int16 w 4 surowe bajty (struct.pack).
# 3. Zinterpretowanie tych 4 bajtow jako float32 (struct.unpack).
# -------------------------------------------------------------------------

# TODO 1: Odczytaj 2 Holding Registers od adresu 1
# res = client.read_holding_registers(address=..., count=...)

# TODO 2: Pobierz wartosci rejestrow z listy res.registers:
# reg1 = res.registers[0]
# reg2 = res.registers[1]
# print(f"[RAW] Pobrane rejestry 16-bit: reg1={reg1}, reg2={reg2}")

# TODO 3: Zbuduj 4-bajtowy bufor pamieci (format: Big-Endian '>HH')
# raw_bytes = struct.pack('>HH', reg1, reg2)

# TODO 4: Zrekonstruuj liczbe zmiennoprzecinkowa (format: Big-Endian '>f')
# pressure = struct.unpack('>f', raw_bytes)[0]

# print(f"[ODCZYT] Cisnienie hydrostatyczne: {pressure:.2f} bar")

client.close()

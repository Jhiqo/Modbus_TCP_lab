import struct
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('127.0.0.1', port=5020)

if not client.connect():
    print("[ERROR] Brak polaczenia ze sterownikiem!")
    exit(1)

# 1. Odczyt dwoch rejestrow Holding (adres 1 i 2)
rr = client.read_holding_registers(address=1, count=2)

if rr.isError():
    print(f"[BLAD] Nie udalo sie odczytac rejestrow: {rr}")
    client.close()
    exit(1)

reg1, reg2 = rr.registers[0], rr.registers[1]
print(f"[RAW] Odczytane slowa 16-bit: HR1 = {reg1}, HR2 = {reg2}")

# 2. Pakowanie dwoch uint16 do ciagu 4 bajtow (Big-Endian: '>')
raw_bytes = struct.pack('>HH', reg1, reg2)
print(f"[HEX] Surowe bajty w buforze: {raw_bytes.hex(' ')}")

# 3. Reinterpretacja 4 bajtow jako IEEE 754 float32
pressure = struct.unpack('>f', raw_bytes)[0]

print(f"[WYNIK] Cisnienie hydrostatyczne w zbiorniku: {pressure:.3f} bar")

client.close()

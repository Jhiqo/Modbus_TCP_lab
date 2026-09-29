from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('127.0.0.1', port=5020)

if not client.connect():
    print("[ERROR] Nie mozna polaczyc sie z wezlem!")
    exit(1)

# 1. Odczyt poziomu (Input Register 0)
res_ir = client.read_input_registers(address=0, count=1)
if not res_ir.isError():
    print(f"[ODCZYT] Input Register 0 (Poziom): {res_ir.registers[0]} l")
else:
    print(f"[BLAD] Odczyt IR 0: {res_ir}")

# 2. Odczyt nastawy (Holding Register 0)
res_hr = client.read_holding_registers(address=0, count=1)
if not res_hr.isError():
    print(f"[ODCZYT] Holding Register 0 (Nastawa): {res_hr.registers[0]}")

# 3. Zapis nowej nastawy (Holding Register 0 = 65)
write_res = client.write_register(address=0, value=65)
if not write_res.isError():
    print("[ZAPIS] Zapisano nowa wartosc 65 do HR 0.")

# Weryfikacja zapisu
verify = client.read_holding_registers(address=0, count=1)
print(f"[WERYFIKACJA] Nowa wartosc w HR 0: {verify.registers[0]}")

client.close()

import asyncio
import struct
import pymodbus
import logging

# Wyłączenie ostrzeżeń o deprecjacji (żeby nie śmieciły w konsoli ucznia w v3.15+)
logging.getLogger("pymodbus").setLevel(logging.ERROR)

print(f"[INIT] Wykryto bibliotekę pymodbus w wersji: {pymodbus.__version__}")

# -----------------------------------------------------------------------------
# 1. HYBRYDOWY IMPORT I WYKRYWANIE WERSJI API
# -----------------------------------------------------------------------------
try:
    from pymodbus.server import StartAsyncTcpServer
    from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
    IS_LEGACY_V2 = False
except ImportError:
    from pymodbus.server.async_io import StartTcpServer as StartAsyncTcpServer
    from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
    IS_LEGACY_V2 = True

try:
    from pymodbus.datastore import ModbusDeviceContext
    USES_DEVICE_CONTEXT = True
except ImportError:
    from pymodbus.datastore import ModbusSlaveContext
    USES_DEVICE_CONTEXT = False


# -----------------------------------------------------------------------------
# 2. WARSTWA ABSTRAKCJI DANYCH (Omija zmieniające się metody kontekstu API)
# -----------------------------------------------------------------------------
class DataStore:
    def __init__(self):
        # Próba inicjalizacji z nowym silnikiem (odejmuje 1 od adresu startowego)
        try:
            self.base = 1
            self.di = ModbusSequentialDataBlock(1, [0] * 10)
            self.co = ModbusSequentialDataBlock(1, [0] * 10)
            self.ir = ModbusSequentialDataBlock(1, [150] * 10)
            self.hr = ModbusSequentialDataBlock(1, [500] * 10)
        except (TypeError, ValueError):
            # Fallback dla starszych silników (adres bazowy wprost 0)
            self.base = 0
            self.di = ModbusSequentialDataBlock(0, [0] * 10)
            self.co = ModbusSequentialDataBlock(0, [0] * 10)
            self.ir = ModbusSequentialDataBlock(0, [150] * 10)
            self.hr = ModbusSequentialDataBlock(0, [500] * 10)

    # Bezpieczne metody odczytu/zapisu radzące sobie z każdą wersją (getValues / get_values)
    def _get_val(self, block, offset):
        addr = self.base + offset
        if hasattr(block, "getValues"): return block.getValues(addr, 1)[0]
        elif hasattr(block, "get_values"): return block.get_values(addr, 1)[0]
        else: return block.values[offset]

    def _set_val(self, block, offset, values):
        addr = self.base + offset
        if hasattr(block, "setValues"): block.setValues(addr, values)
        elif hasattr(block, "set_values"): block.set_values(addr, values)
        else:
            for i, v in enumerate(values): block.values[offset + i] = v

    def get_coil(self, offset): return self._get_val(self.co, offset)
    def set_ir(self, offset, vals): self._set_val(self.ir, offset, vals)
    def set_di(self, offset, vals): self._set_val(self.di, offset, vals)
    def set_hr(self, offset, vals): self._set_val(self.hr, offset, vals)


def build_server_context():
    store = DataStore()
    
    if USES_DEVICE_CONTEXT:
        device = ModbusDeviceContext(di=store.di, co=store.co, ir=store.ir, hr=store.hr)
        context = ModbusServerContext(devices=device, single=True)
    else:
        slave = ModbusSlaveContext(di=store.di, co=store.co, ir=store.ir, hr=store.hr)
        context = ModbusServerContext(slaves=slave, single=True)
        
    return context, store


# -----------------------------------------------------------------------------
# 3. PĘTLA MODELU FIZYCZNEGO (DYNAMIKA ZBIORNIKA)
# -----------------------------------------------------------------------------
async def physics_loop(store):
    level = 150.0  # Poziom początkowy cieczy [l]

    while True:
        await asyncio.sleep(0.1)  # Krok dyskretyzacji dt = 100 ms

        # 1. Odczyt stanu elektrozaworu XV-101 (Coil pod adresem 0)
        valve_open = store.get_coil(0)

        # 2. Równanie różnicowe bilansu masy cieczy
        inflow = 0.35
        outflow = 0.7 if valve_open else 0.0
        level = max(0.0, min(1000.0, level + inflow - outflow))

        # 3. Zapis zmiennych procesowych do rejestrów obiektu
        store.set_ir(0, [int(level)])                  # LT-101 (Poziom)
        store.set_di(0, [1 if level >= 900 else 0])    # LSH-101 (Alarm)

        # Holding Register 1 i 2: Ciśnienie [bar] jako Float32
        p_bytes = struct.pack(">f", float(level / 200.0))
        store.set_hr(1, list(struct.unpack(">HH", p_bytes)))


# -----------------------------------------------------------------------------
# 4. GŁÓWNA PĘTLA SERWERA
# -----------------------------------------------------------------------------
async def main():
    context, store = build_server_context()
    print("[SERVER] Obiekt fizyczny aktywny na porcie 5020...")

    # Zamiast głupiejącego z wersjami contextu, wrzucamy tu wprost nasz hermetyczny `store`
    asyncio.create_task(physics_loop(store))

    if IS_LEGACY_V2:
        await StartAsyncTcpServer(context=context, address=("0.0.0.0", 5020), defer_start=False)
    else:
        await StartAsyncTcpServer(context=context, address=("0.0.0.0", 5020))


if __name__ == "__main__":
    asyncio.run(main())

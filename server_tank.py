import asyncio
import struct
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)

async def physics_loop(context):
    slave = context[0]
    level = 150.0  # Poziom poczatkowy [l]

    while True:
        await asyncio.sleep(0.1)  # Krok dyskretyzacji dt = 100 ms
        
        # Coil 0: Stan zaworu spustowego
        valve_open = slave.getValues(1, 0, count=1)[0]

        # Bilans masy: doplyw staly 1.8 l/s, odplyw 3.5 l/s po otwarciu zaworu
        inflow = 0.18
        outflow = 0.35 if valve_open else 0.0
        level = max(0.0, min(1000.0, level + inflow - outflow))

        # Input Register 0: Poziom cieczy [0 - 1000 l] (LT-101)
        slave.setValues(4, 0, [int(level)])

        # Discrete Input 0: Sprzetowy alarm przelania >= 900 l (LSH-101)
        slave.setValues(2, 0, [1 if level >= 900.0 else 0])

        # Holding Register 1 i 2: Cisnienie hydrostatyczne [bar] jako Float32 (IEEE 754)
        pressure = float(level / 200.0)
        p_bytes = struct.pack('>f', pressure)
        slave.setValues(3, 1, list(struct.unpack('>HH', p_bytes)))

async def main():
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 10),
        co=ModbusSequentialDataBlock(0, [0] * 10),
        ir=ModbusSequentialDataBlock(0, [150] * 10),
        hr=ModbusSequentialDataBlock(0, [500] * 10),
    )
    context = ModbusServerContext(slaves=store, single=True)
    print("=" * 60)
    print("[SERVER] Obiekt fizyczny aktywny na 0.0.0.0:5020")
    print("[SERVER] Wcisnij Ctrl+C, aby zatrzymac proces.")
    print("=" * 60)

    asyncio.create_task(physics_loop(context))
    await StartAsyncTcpServer(context=context, address=("0.0.0.0", 5020))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SERVER] Zatrzymano symulacje obiektu.")

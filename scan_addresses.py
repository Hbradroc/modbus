from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException

import time

# ================= USER SETTINGS =================

PORT = "COM5"
BAUD = 4800
PARITY = "N"
STOPBITS = 1
BYTESIZE = 8
TIMEOUT = 1

# ================================================

print("\n" + "="*50)
print("Modbus Address Scanner")
print("="*50 + "\n")

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUD,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=BYTESIZE,
    timeout=TIMEOUT,
    rtscts=False
)

if not client.connect():
    print("❌ Cannot open COM port")
    print("   Check if device is connected and drivers are installed")
    exit()

print(f"✅ Connected to {PORT} @ {BAUD} baud\n")
print("Scanning addresses 1-254...\n")

found_devices = []

for addr in range(1, 255):
    try:
        # Try to read register 0x0000 (channel 1 analog value)
        response = client.read_holding_registers(
            address=0,
            count=1,
            device_id=addr
        )
        
        if response and not response.isError():
            value = response.registers[0]
            found_devices.append((addr, value))
            print(f"✅ Found device at address {addr:3d} - Register 0: {value}")
    
    except ModbusIOException:
        pass
    except:
        pass
    
    # Progress indicator every 50 addresses
    if addr % 50 == 0 and not found_devices:
        print(f"   Scanned up to address {addr}...")

print("\n" + "="*50)
if found_devices:
    print(f"Found {len(found_devices)} device(s):")
    for addr, value in found_devices:
        print(f"  - Address {addr}: Value = {value}")
else:
    print("❌ No devices found")
    print("\nPossible causes:")
    print("  1. Device not powered on")
    print("  2. A+ and B- wires not connected or reversed")
    print("  3. Baud rate mismatch (try 9600 instead of 4800)")
    print("  4. USB driver not installed")
    print("  5. COM port is incorrect (check Device Manager)")

print("="*50 + "\n")

client.close()

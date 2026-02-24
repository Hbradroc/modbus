import serial
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
import time

print("=" * 50)
print("RS485 Modbus Diagnostic Tool")
print("=" * 50)

# List available COM ports
print("\n[1] Available COM Ports:")
ports = serial.tools.list_ports.comports()
if not ports:
    print("❌ No COM ports found!")
else:
    for port in ports:
        print(f"  - {port.device}: {port.description}")

# Test each port with different settings
test_configs = [
    {"baud": 4800, "parity": "N"},
    {"baud": 4800, "parity": "E"},
    {"baud": 9600, "parity": "N"},
    {"baud": 9600, "parity": "E"},
]

print("\n[2] Testing Modbus communication on each port:")

for port_info in ports:
    port = port_info.device
    print(f"\n  Testing {port}:")
    
    for config in test_configs:
        print(f"    Trying {config['baud']} baud, {config['parity']} parity...", end=" ")
        
        try:
            client = ModbusSerialClient(
                port=port,
                baudrate=config['baud'],
                parity=config['parity'],
                stopbits=1,
                bytesize=8,
                timeout=1
            )
            
            if client.connect():
                # Try to read device address (register 0x07D0)
                response = client.read_holding_registers(
                    address=0x07D0,
                    count=1,
                    device_id=1
                )
                
                if response and not response.isError():
                    device_address = response.registers[0]
                    print(f"✅ FOUND! Device address: {device_address}")
                else:
                    # Try to read channel 1 (register 0x0000)
                    response = client.read_holding_registers(
                        address=0x0000,
                        count=1,
                        device_id=1
                    )
                    
                    if response and not response.isError():
                        print(f"✅ FOUND! Channel 1 value: {response.registers[0]}")
                    else:
                        print("❌ Connected but no response")
                
                client.close()
            else:
                print("❌ Cannot open port")
        
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")

print("\n" + "=" * 50)
print("Diagnostic complete!")
print("=" * 50)

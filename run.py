

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException

import time

# ================= USER SETTINGS =================

PORT = "COM5"
BAUD = 4800          # Per manual default (section 1.3)
OLD_ID = 1
NEW_ID = 21

PARITY = "N"         # No parity (per manual section 4.1)
STOPBITS = 1
BYTESIZE = 8
TIMEOUT = 1

ADDRESS_REGISTER = 0x07D0  # Device address register (per manual section 4.3)

# ================================================


def main():

    print("\n====================================")
    print(" ZTS-3000 Address Configuration Tool")
    print("====================================\n")

    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUD,
        parity=PARITY,
        stopbits=STOPBITS,
        bytesize=BYTESIZE,
        timeout=TIMEOUT
    )

    if not client.connect():
        print("❌ Cannot open COM port")
        print("   Retrying in 2 seconds...")
        time.sleep(2)
        if not client.connect():
            print("❌ Still cannot open COM port - it may be in use by another application")
            print("   Try closing configuration software or other terminal programs")
            return

    print(f"✅ Connected to {PORT} @ {BAUD} baud")


    # ---------- RAW READ TEST ----------
    print("\n[1] Testing communication...")

    try:
        response = client.read_holding_registers(
            address=0,
            count=1,
            device_id=OLD_ID
        )

        if not response or response.isError():
            print("❌ No response from device")
            print("   Check wiring / parity / baud / address")
            client.close()
            return

        print("✅ Device responded:", response.registers)
    
    except ModbusIOException as e:
        print("❌ No response from device at address", OLD_ID)
        print("   Possible causes:")
        print("   1. Device not powered on")
        print("   2. A+ and B- wires reversed or not connected")
        print("   3. Device address is not 1 (try scanning below)")
        print("   4. RS485 bus needs termination resistor (120Ω)")
        print(f"   Error: {e}")
        
        # Try to scan for devices
        print("\n   Scanning for devices on the bus...")
        found = False
        for addr in [1, 2, 3, 21, 254]:
            try:
                response = client.read_holding_registers(
                    address=0,
                    count=1,
                    device_id=addr
                )
                if response and not response.isError():
                    print(f"   ✅ Found device at address {addr}!")
                    found = True
            except:
                pass
        
        if not found:
            print("   ❌ No devices found on any address")
        
        client.close()
        return


    # ---------- WRITE NEW ADDRESS ----------
    print("\n[2] Writing new address...")

    try:
        response = client.write_register(
            address=ADDRESS_REGISTER,
            value=NEW_ID,
            device_id=OLD_ID
        )

        if not response or response.isError():

            print("⚠ No ACK — trying broadcast")

            client.write_register(
                address=ADDRESS_REGISTER,
                value=NEW_ID,
                device_id=0
            )

            print("⚠ Broadcast sent")

        else:
            print("✅ Write acknowledged")
    
    except ModbusIOException as e:
        print(f"⚠ Write failed: {e}")


    # ---------- POWER CYCLE ----------
    input("\nPower OFF/ON device, then press Enter...")


    # ---------- VERIFY ----------
    print("\n[3] Verifying new address...")

    try:
        response = client.read_holding_registers(
            address=0,
            count=1,
            device_id=NEW_ID
        )

        if not response or response.isError():
            print("❌ No response on new address")
            print("   Address change may have failed")
        else:
            print("✅ New address confirmed:", response.registers)
    
    except ModbusIOException as e:
        print(f"❌ Verification failed: {e}")


    client.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
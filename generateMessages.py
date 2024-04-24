import can
from time import sleep

def send_can_messages(file_path):
    # Set up the CAN bus
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')

    # Open the file containing CAN messages
    with open(file_path, 'r') as file:
        for line in file:
            # Parse each line to extract the CAN ID and data
            parts = line.strip().split()
            print(parts)
            can_id = int(parts[3], 16)  # Adjusted index for CAN ID
            data = bytes.fromhex(''.join(parts[8:16]))
            

            # Create a CAN message
            msg = can.Message(arbitration_id=can_id, data=data, extended_id=False)

            # Send the CAN message
            bus.send(msg)
            print("Sent:", msg)
            #sleep(0.01)

if __name__ == "__main__":
    file_path = "bacau.txt"  # Change this to your file path
    send_can_messages(file_path)

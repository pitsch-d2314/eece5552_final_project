import serial
import sys
import csv
import datetime
import time 

def main():
    # Default serial port and baud rate
    port = '/dev/cu.usbserial-110'
    baudrate = 9600

    # Check for command-line arguments to override defaults
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        print(f"Usage: python {sys.argv[0]} [port] [baudrate]")
        print(f"Using default port: {port}")

    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])

    # Open CSV file in write mode
    csv_filename = 'serial_data.csv'
    try:
        # Open the serial port
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Connected to {port} at {baudrate} baud.")

        # Wait for Arduino to reset
        time.sleep(2)

        # Flush input buffer to clear any existing data
        ser.flushInput()

        with open(csv_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header row
            csv_writer.writerow(['Timestamp', 'Message'])

            # Read data from the serial port
            while True:
                # Read a line from the serial port
                line = ser.readline().decode('utf-8', errors='replace').rstrip()
                if line:
                    print(line)
                    # Write the line to CSV file with timestamp
                    timestamp = datetime.datetime.now().isoformat()
                    csv_writer.writerow([timestamp, line])
                    # Flush the buffer to ensure data is written to disk
                    csvfile.flush()
                else:
                    
                    # Optional: Handle the case where no data is received
                    pass
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        # Close the serial port if it's open
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == '__main__':
    main()

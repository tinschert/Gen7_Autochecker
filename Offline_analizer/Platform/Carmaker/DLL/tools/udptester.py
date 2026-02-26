import socket
import struct

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 12345)

# Expose the values to be adjustable
magic_number = 0x55555555  # You can adjust this
counter = 100  # Adjust this value
length = 50  # Adjust this value
constant_value = 1  # This should always be 1
data_value = 0  # This should always be 0

# Pack the values into a bytestream using network byte order (big-endian)
message = struct.pack('5I', magic_number, counter, length, constant_value, data_value)

try:
    print(f'Sending {message} to {server_address}')
    sent = sock.sendto(message, server_address)
finally:
    sock.close()

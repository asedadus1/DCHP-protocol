import socket

# DHCP Client Configuration
admin_ip = '10.0.0.30'
admin_port = 9000
server_ip = '10.0.0.100'
server_port = 9000


client_address = (admin_ip, admin_port)


def initialize_admin_socket(admin_ip, admin_port):
    admin_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    admin_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    admin_socket.bind((admin_ip, admin_port))
    return admin_socket

def main():
    admin_socket = initialize_admin_socket(admin_ip, admin_port)
    message = "LIST"
    message_decoded = message.encode('utf-8')
    admin_socket.sendto(message_decoded, (server_ip, server_port))
    data, addr = admin_socket.recvfrom(2480)
    message = data.decode('utf-8')
    print(message)


if __name__ == "__main__":
    main()

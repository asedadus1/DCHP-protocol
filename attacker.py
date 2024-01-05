import socket
import datetime
import sys
import random

# DHCP Client Configuration
client_ip = '10.0.0.40'
client_port = 9000
server_ip = '10.0.0.100'
server_port = 9000

client_address = (client_ip, client_port)

#generate random mac addresses
def generate_random_mac_addresses(num_addresses):
    mac_addresses = []
    for _ in range(num_addresses):
        mac = ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])
        mac_addresses.append(mac.upper())

    return mac_addresses




# Create and send DHCP Discover
def create_dhcp_discover(MAC):
    dhcp_discover = "DISCOVER " + MAC
    return dhcp_discover


def handle_replay(message, MAC):
    dhcp_replay = ""
    message_parts = message.split()
    command = message_parts[0]
    if command == 'DECLINE':
        print("DECLNE")
        sys.exit()  # Force terminate the program
    offered_ip = message_parts[2]
    time_stamp = message_parts[3]


    if command == 'OFFER':
        mac_address_recieved = message_parts[1]
        current_time_stamp = datetime.datetime.now()
        record_time_stamp = datetime.datetime.fromisoformat(time_stamp)
        if MAC.lower() == mac_address_recieved.lower():
            if current_time_stamp < record_time_stamp:
                dhcp_replay = f"REQUEST {MAC} {offered_ip} {time_stamp}"
                return dhcp_replay

    elif command == 'ACKNOWLEDGE':
        mac_address_recieved = message_parts[1]
        if MAC.lower() == mac_address_recieved.lower():
            expiration_time = time_stamp
            print(f"ACKNOWLEDGE received. Assigned IP address: {offered_ip}. Expires at: {expiration_time}\n")
            return f'SUCCESS {offered_ip} {expiration_time}'
        else:
            print("Error: Received MAC address does not match client's MAC address. Terminating.")
            sys.exit()  # Force terminate the program
    else:
        pass


                     

def initialize_client_socket(client_ip, client_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.bind((client_ip, client_port))
    return client_socket


def RENEW_message(IP, TS, MAC):
    return f"RENEW {MAC} {IP} {TS}"


def RELEASE_message(IP, TS, MAC):
    return f"RELEASE {MAC} {IP} {TS}"

def main():
    client_socket = initialize_client_socket(client_ip, client_port)

    random_mac_addresses = generate_random_mac_addresses(14)



    for mac_address in random_mac_addresses:
        dhcp_discover = create_dhcp_discover(mac_address)
        message = dhcp_discover.encode('utf-8')
        client_socket.sendto(message, (server_ip, server_port))
        print(f"DHCP Client sending Discover to {server_ip}:{server_port}")
        print(dhcp_discover)
        while True:
            data, addr = client_socket.recvfrom(1024)
            if data:
                message = data.decode('utf-8')
                message_part = message.split()
                dhcp_replay = handle_replay(message, mac_address)
                replay_part = dhcp_replay.split()
                if replay_part[0] == "SUCCESS":
                    print(f"\nACKNOWLEDGE received. Assigned IP address: {replay_part[1]}. Expires at: {replay_part[2]}\n")
                    break
                else:
                    replay = dhcp_replay.encode('utf-8')
                    client_socket.sendto(replay, (server_ip, server_port))



if __name__ == "__main__":
    main()

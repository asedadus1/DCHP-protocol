import socket
import datetime
import uuid
import sys


# DHCP Client Configuration
client_ip = '10.0.0.10'
client_port = 9000
server_ip = '10.0.0.100'
server_port = 9000


client_address = (client_ip, client_port)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()




# Create and send DHCP Discover
def create_dhcp_discover():
    dhcp_discover = "DISCOVER " + MAC
    return dhcp_discover


def handle_replay(message):
    dhcp_replay = ""
    message_parts = message.split()
    command = message_parts[0]
    if command == 'DECLINE':
        print("DECLNE")
        sys.exit()  # Force terminate the program
    offered_ip = message_parts[2]
    time_stamp = message_parts[3]

    if command == 'DECLINE':
        print("DECLNE")
        sys.exit()  # Force terminate the program
    elif command == 'OFFER':
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


def RENEW_message(IP, TS):
    return f"RENEW {MAC} {IP} {TS}"


def RELEASE_message(IP, TS):
    return f"RELEASE {MAC} {IP} {TS}"

    


def main():
    client_socket = initialize_client_socket(client_ip, client_port)

    dhcp_discover = create_dhcp_discover()
    message = dhcp_discover.encode('utf-8')
    client_socket.sendto(message, (server_ip, server_port))
    print(f"DHCP Client sending Discover to {server_ip}:{server_port}")
    print(dhcp_discover)

    message = ""
    while True:
        data, addr = client_socket.recvfrom(1024)
        if data:
            message = data.decode('utf-8')
            message_part = message.split()
            dhcp_replay = handle_replay(message)
            replay_part = dhcp_replay.split()
            if replay_part[0] == "SUCCESS":
                print(f"\nACKNOWLEDGE received. Assigned IP address: {replay_part[1]}. Expires at: {replay_part[2]}")
                break
            else:
                replay = dhcp_replay.encode('utf-8')
                client_socket.sendto(replay, (server_ip, server_port))
   
    message_part = message.split()
    ip = message_part[2]
    ts = message_part[3]

    while True:
        print('\nDHCP configuration has been completed. Select the next option:')
        print('1. Send RELEASE message to the server')
        print('2. Send RENEW message to the server')
        print('3. Terminate the client\'s program')

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            print('Sending RELEASE message to the server...')
            # Add your RELEASE message sending logic here
            release = RELEASE_message(ip, ts)
            print ( release )
            release_encoded = release.encode('utf-8')
            client_socket.sendto(release_encoded, (server_ip, server_port))

        elif choice == '2':
            # Code for sending RENEW message
            print('Sending RENEW message to the server...')
            renew = RENEW_message(ip, ts)
            print(renew)
            renew_encoded = renew.encode('utf-8')
            client_socket.sendto(renew_encoded, (server_ip, server_port))
            data, addr = client_socket.recvfrom(1024)
            if data:
                message = data.decode('utf-8')
                message_part = message.split()
                dhcp_replay = handle_replay(message)
                replay_part = dhcp_replay.split()
                if replay_part[0] == "SUCCESS":
                    ip = replay_part[1]
                    ts = replay_part[2]
                    print(f"\nACKNOWLEDGE received. Assigned IP address: {ip}. Expires at: {ts}")
                    pass
                else:
                    replay = dhcp_replay.encode('utf-8')
                    client_socket.sendto(replay, (server_ip, server_port))
            

        elif choice == '3':
            # Terminate the program
            client_socket.close()
            print('Terminating the client\'s program.')
            sys.exit()  # Force terminate the program
        else:
            print('Invalid choice. Please enter 1, 2, or 3.')


            



if __name__ == "__main__":
    main()

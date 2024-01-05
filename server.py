import socket
import datetime
import json
from ipaddress import IPv4Interface


# Constants
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000
server_address = (SERVER_IP, SERVER_PORT)


# DHCP Server State
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]
client_records = {}

def get_next_record_number():
    return len(client_records) + 1

def is_expired(Time_Stamp):
    current_time = datetime.datetime.now()
    expiration_time = datetime.datetime.fromisoformat(Time_Stamp)
    if current_time > expiration_time:
        return True
    else:
        return False


# Function to handle DHCP requests
def handle_request(request):
    global ip_addresses, client_records
    request_parts = request.split()
    command = request_parts[0]

    if command == 'LIST':
        acked_records = {mac: record for mac, record in client_records.items() if record['Acked']}
        return json.dumps(acked_records, indent=4)

    elif command == 'DISCOVER':
        mac_address = request_parts[1]
        if mac_address not in client_records:
            #check if there is an avalable IP address to offer
            if ip_addresses:
                record_number = get_next_record_number()
                offer_ip = ip_addresses.pop(0)
                time_stamp = datetime.datetime.now() + datetime.timedelta(seconds=60)
                time_stamp_iso = time_stamp.isoformat()
                client_records[mac_address] = {
                'Record number' : record_number,
                'IP': offer_ip,
                'Timestamp': time_stamp_iso,
                'Acked': False
                }
                return 'OFFER {} {} {}'.format(mac_address, offer_ip, time_stamp_iso)
            else:
                ip_address_to_assign = ""
                for mac_address_in_record, record in client_records.items():
                    expiration_time = record['Timestamp']
                    expired_D11 = is_expired(expiration_time)
                    if expired_D11 == True: #MESSAGE is DESCOVER, MAC address is not in the record, we found expired TS on the recored
                        ip_address_to_assign = record['IP']
                        record = client_records.pop(mac_address_in_record)
                        break
                if ip_address_to_assign == "": #MESSAGE: DESCOVER MAC address is not in the record, if we do not found expired TS on the recored
                    return "DECLINE 1"
                else:     #MESSAGE: is DESCOVER MAC address is not in the record, if we found expired TS on the recored
                    record_number = get_next_record_number()
                    new_time_stamp = datetime.datetime.now() + datetime.timedelta(seconds=60)
                    new_time_stamp_iso = new_time_stamp.isoformat()
                    client_records[mac_address] = {
                    'Record number' : record_number,
                    'IP': ip_address_to_assign,
                    'Timestamp': new_time_stamp_iso,
                    'Acked': False
                    }
                    return 'OFFER {} {} {}'.format(mac_address, ip_address_to_assign, new_time_stamp_iso)
        else:
            requested_ip_D= client_records[mac_address]['IP']
            timestamp = client_records[mac_address]['Timestamp']
            expired_D1 = is_expired(client_records[mac_address]['Timestamp'])
            if expired_D1 == True: #TIME STAMP HAS EXPIRED
                client_records[mac_address]['Acked'] = False
                new_time_stamp = datetime.datetime.now() + datetime.timedelta(seconds=60)
                new_time_stamp_iso = new_time_stamp.isoformat()
                client_records[mac_address]['Timestamp'] = new_time_stamp_iso
                return 'OFFER {} {} {}'.format(mac_address, requested_ip_D, new_time_stamp_iso)
            else: #TIME STAMP HAS NOT EXPIRED
                client_records[mac_address]['Acked'] = True
                time_stam  = client_records[mac_address]['Timestamp']
                return 'ACKNOWLEDGE {} {} {}'.format(mac_address, requested_ip_D, time_stam)

    elif command == 'REQUEST':
        mac_address = request_parts[1]
        requested_ip = request_parts[2]
        timestamp = request_parts[3]
        if mac_address not in client_records and requested_ip != client_records[mac_address]['IP']:
            return 'DECLINE'
        else:
            expiration_time = datetime.datetime.fromisoformat(client_records[mac_address]['Timestamp'])
            current_time = datetime.datetime.now()
            time_difference = current_time - expiration_time
            if time_difference.total_seconds() >= 0: #TIME STAMP HAS EXPIRED
                return 'DECLINE'
            else:
                client_records[mac_address]['IP'] = requested_ip
                client_records[mac_address]['Timestamp'] = timestamp
                client_records[mac_address]['Acked'] = True
                return 'ACKNOWLEDGE {} {} {}'.format(mac_address, requested_ip, timestamp)
            
    elif command == 'RELEASE':
        mac_address = request_parts[1]
        
        if mac_address in client_records and client_records[mac_address]['Acked'] == True:
            client_records[mac_address]['Acked'] = False
            released_record = client_records[mac_address]
            return f"RELEASE IP = {client_records[mac_address]['IP']}"
        else:
            print(f"No record found for {mac_address}")
            return "RELEASE"

    elif command == 'RENEW':
        mac_address = request_parts[1]
        requested_ip = request_parts[2]
        timestamp = request_parts[3]
        expiredR1 = is_expired(timestamp) #return true if the time has expired
        if mac_address in client_records and expiredR1 == False:
            new_time_stamp = datetime.datetime.now() + datetime.timedelta(seconds=60)
            new_time_stamp_iso = new_time_stamp.isoformat()
            client_records[mac_address]['Acked'] = True
            client_records[mac_address]['Timestamp'] = new_time_stamp_iso
            return 'ACKNOWLEDGE {} {} {}'.format(mac_address, requested_ip, new_time_stamp_iso)
        elif mac_address in client_records and expiredR1 == True:
            new_time_stamp = datetime.datetime.now() + datetime.timedelta(seconds=60)
            new_time_stamp_iso = new_time_stamp.isoformat()
            client_records[mac_address]['Acked'] = False
            client_records[mac_address]['Timestamp'] = new_time_stamp_iso
            return 'OFFER {} {} {}'.format(mac_address, requested_ip, new_time_stamp_iso)
        else: 
            if ip_addresses:
                record_number = get_next_record_number()
                offer_ip = ip_addresses.pop(0)
                time_stamp = datetime.datetime.now() + datetime.timedelta(seconds=60)
                time_stamp_iso = time_stamp.isoformat()
                client_records[mac_address] = {
                'Record number' : record_number,
                'IP': offer_ip,
                'Timestamp': time_stamp_iso,
                'Acked': False
                }
                return 'OFFER {} {} {}'.format(mac_address, offer_ip, time_stamp_iso)
            else:
                ip_address_to = ""
                for mac_address_in_record, record in client_records.items():
                    expiration_time = record['Timestamp']
                    expired_R2 = is_expired(expiration_time)
                    if expired_R2 == True: #TIME STAMP HAS EXPIRED
                        ip_address_to_assign = record['IP']
                        record = client_records.pop(mac_address_in_record)
                        break
                if ip_address_to_assign == "":
                    return "DECLINE"
                else:
                    record_number = get_next_record_number()
                    new_time_stamp = datetime.datetime.now() + datetime.timedelta(seconds=60)
                    new_time_stamp_iso = new_time_stamp.isoformat()
                    client_records[mac_address] = {
                    'Record number' : record_number,
                    'IP': ip_address_to_assign,
                    'Timestamp': new_time_stamp_iso,
                    'Acked': False
                    }
                    return 'OFFER {} {} {}'.format(mac_address, ip_address_to_assign, new_time_stamp_iso)
    else:
        return f'INVALID COMMAND  {request}'

# Main server loop
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)

    print('DHCP Server listening on {}:{}'.format(SERVER_IP, SERVER_PORT))
    try:
        while True:
            data, addr = server_socket.recvfrom(1024)
            if data:
                request = data.decode('utf-8')
                print(f"Client message = {request}")
                response = handle_request(request)
                response_parts = response.split()
                if response_parts[0] == "RENEWED" or response_parts[0] == "RELEASE" or response_parts[0] == "ACKNOWLEDGE" or response_parts[0] == "OFFER" or response_parts[0] == "DECLINE":
                    print(f"Server message = {response}")
                if response_parts[0] == "RENEWED"  or response_parts[0] == "RELEASE":
                    pass
                else:
                    server_socket.sendto(response.encode('utf-8'), addr)
    except KeyboardInterrupt:
        pass

        

    

if __name__ == "__main__":
    main()

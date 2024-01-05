DHCP Protocol Implementation
Overview
This project involves the implementation of the DHCP (Dynamic Host Configuration Protocol) protocol using UDP for the transport layer. The server program listens to client requests and follows the four steps of the DHCP protocol: DISCOVER, OFFER, REQUEST, and ACKNOWLEDGE. Clients, initially without an IP address, aim to discover the DHCP server and obtain an IP address from the server.

IP Address Range
The server manages a block of 16 IP addresses in the range 192.168.45.0/28, including Net ID and Broadcast IP address. However, Net ID and Broadcast IP addresses cannot be assigned to any node in the network, leaving 14 available IP addresses (192.168.45.1 to 192.168.45.14). The lease time for an assigned IP address is set to 60 seconds from the time the server sends an ACKNOWLEDGE message.

Client Identification
Clients are identified by their MAC addresses, and the server maintains a list of clients' MAC addresses, associated IP addresses, and timestamps indicating when the assigned IP address will expire.

DHCP Protocol Steps
DISCOVER: Client sends a DISCOVER message to the server.
OFFER: Server replies with an OFFER message.
REQUEST: Client sends a REQUEST message to the server.
ACKNOWLEDGE: Server assigns an IP address and replies with an ACKNOWLEDGE message.
Message Format
All communication between the client and server must follow a specific message format, with messages in all uppercase and separated by spaces.

Client Requests
Clients can send the following requests to the server:

LIST: Request a list of assigned IP addresses.
DISCOVER [MAC_ADDRESS]: Initiate the DHCP discovery process.
REQUEST [MAC_ADDRESS] [IP_ADDRESS] [TIMESTAMP]: Request a specific IP address with a timestamp.
RELEASE [MAC_ADDRESS] [IP_ADDRESS] [TIMESTAMP]: Release a previously assigned IP address.
RENEW [MAC_ADDRESS] [IP_ADDRESS] [TIMESTAMP]: Renew the lease for a specific IP address.
Server Record Format
The server maintains a record for every client with the following elements:

Record number: A unique identifier.
MAC address: Client's MAC address.
IP address: Assigned IP address.
Timestamp: Datetime object in ISO format indicating the expiration time.
Acked: Boolean indicating whether the assigned IP address has been acknowledged.
Example Requests
LIST
DISCOVER A1:30:9B:D3:CE:18
REQUEST A1:30:9B:D3:CE:18 192.168.45.1 2022-02-02T11:42:08.761340
RELEASE A1:30:9B:D3:CE:18 192.168.45.1 2022-02-02T11:42:08.761340
RENEW A1:30:9B:D3:CE:18 192.168.45.1 2022-02-02T11:42:08.761340

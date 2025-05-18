#!/usr/bin/env python3
import socket
import threading
import subprocess
import time

# Configuration
LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 8001
USAGE_THRESHOLD = 5  # Usage difference threshold for server selection
PING_THRESHOLD = 100  # ms, ping threshold for server selection
SERVERS = [
    {'host': '192.168.2.2', 'port': 8000, 'usage': 0, 'ping': 9999},
    {'host': '192.168.2.3', 'port': 8000, 'usage': 0, 'ping': 9999},
]

PING_INTERVAL = 10  # seconds

# Ping helper
def get_ping(host):
    try:
        output = subprocess.check_output(['ping', '-c', '1', '-W', '1', host], stderr=subprocess.DEVNULL).decode()
        for line in output.split('\n'):
            if 'time=' in line:
                return float(line.split('time=')[1].split(' ')[0])
    except:
        return 9999
    return 9999

# Ping updater thread
def update_ping_loop():
    while True:
        for s in SERVERS:
            s['ping'] = get_ping(s['host'])
        print("Ping results:", [(s['host'], s['ping']) for s in SERVERS])
        time.sleep(PING_INTERVAL)

# Server selection logic
def select_best_server():
    print("Selecting best server...")
    # print server usage and ping
    for s in SERVERS:
        print(f"Server {s['host']} usage: {s['usage']}, ping: {s['ping']}")
    
    if (SERVERS[0]['usage'] > SERVERS[1]['usage'] + USAGE_THRESHOLD):
        if SERVERS[1]['ping'] < PING_THRESHOLD:
            return SERVERS[1]
        else:
            return SERVERS[0]
    elif (SERVERS[1]['usage'] > SERVERS[0]['usage'] + USAGE_THRESHOLD):
        if SERVERS[0]['ping'] < PING_THRESHOLD:
            return SERVERS[0]
        else:
            return SERVERS[1]
    else:
        # If usage is similar, select the one with the lowest ping
        return min(SERVERS, key=lambda s: s['ping'])
        

# Forward a request to the best server
def handle_client(client_socket):
    try:
        server = select_best_server()
        server['usage'] += 1

        print(f"Forwarding to {server['host']}:{server['port']} (usage: {server['usage']})")

        backend_socket = socket.create_connection((server['host'], server['port']))
        
        # Relay client -> backend
        request = client_socket.recv(4096)
        backend_socket.sendall(request)

        # Relay backend -> client
        while True:
            response = backend_socket.recv(4096)
            if not response:
                break
            client_socket.sendall(response)

    except Exception as e:
        print(f"[!] Error forwarding: {e}")
    finally:
        client_socket.close()
        try: backend_socket.close()
        except: pass

# Main loop
def start_load_balancer():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((LISTEN_HOST, LISTEN_PORT))
    server_socket.listen(50)
    print(f"Load balancer listening on {LISTEN_HOST}:{LISTEN_PORT}")

    while True:
        client_sock, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

# Run everything
if __name__ == "__main__":
    threading.Thread(target=update_ping_loop, daemon=True).start()
    start_load_balancer()

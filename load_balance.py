import socket
import threading
import subprocess
import time

# Configuration
BACKENDS = [
    {"host": "192.168.2.2", "port": 8000, "ping": 9999, "count": 0},
    {"host": "192.168.2.3", "port": 8000, "ping": 9999, "count": 0}
]
LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 8001
CHECK_INTERVAL = 10

def get_ping(host):
    try:
        output = subprocess.check_output(["ping", "-c", "1", "-W", "1", host],
                                         stderr=subprocess.DEVNULL).decode()
        line = output.split("\n")[-2]
        avg = float(line.split('/')[4])
        return avg
    except Exception:
        return 9999

def monitor_backends():
    while True:
        for server in BACKENDS:
            server["ping"] = get_ping(server["host"])
        print("Ping results:", [(s["host"], s["ping"]) for s in BACKENDS])
        time.sleep(CHECK_INTERVAL)

def select_backend():
    return sorted(BACKENDS, key=lambda s: (s["ping"], s["count"]))[0]

def handle_client(client_socket):
    backend = select_backend()
    backend["count"] += 1
    print(f"Forwarding to {backend['host']}:{backend['port']} (ping={backend['ping']}, count={backend['count']})")

    try:
        with socket.create_connection((backend["host"], backend["port"])) as backend_socket:
            # Start two threads to pipe data in both directions
            threading.Thread(target=pipe, args=(client_socket, backend_socket)).start()
            pipe(backend_socket, client_socket)
    except Exception as e:
        print(f"Connection to backend failed: {e}")
        client_socket.close()

def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass

def start_load_balancer():
    threading.Thread(target=monitor_backends, daemon=True).start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((LISTEN_HOST, LISTEN_PORT))
        server.listen(5)
        print(f"Load balancer listening on {LISTEN_HOST}:{LISTEN_PORT}")
        while True:
            client_sock, _ = server.accept()
            threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    start_load_balancer()

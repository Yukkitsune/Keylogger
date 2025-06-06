import socket
import threading
import datetime
import signal
import sys
import queue

HOST = "127.0.0.1"
PORT = 65432

shutdown_flg = threading.Event()
log_queue = queue.Queue()


def start_server(host=HOST, port=PORT):
    def handle_sigint(sig, frame):
        print("\nShutting down the server")
        shutdown_flg.set()
        sys.exit(0)
    signal.signal(signal.SIGINT, handler=handle_sigint)
    log_thread = threading.Thread(target=log_writer, daemon=True)
    log_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"Server started at {host}:{port}")

        while not shutdown_flg.is_set():
            try:
                s.settimeout(1.0)
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                t = threading.Thread(target=hold_server, args=(conn, addr))
                t.start()
            except socket.timeout:
                continue
            except OSError as e:
                print(f"Socket error: {e}")
                break


def hold_server(conn, addr):
    try:
        with conn:
            conn.settimeout(1.0)
            while True:
                try:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    timestamp = datetime.datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S'
                        )
                    log_queue.put((timestamp, addr[0], data))
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Exception with {addr}: {e}")
                    break
    except Exception as e:
        print(f"Server error with {addr}: {e}")


def log_writer():
    open_files = {}
    try:
        while not shutdown_flg.is_set():
            try:
                timestamp, ip, message = log_queue.get(timeout=1)
                today = datetime.datetime.now().strftime(
                    '%Y-%m-%d'
                    )
                filename = f"log_{today}_{ip}.txt"
                if ip not in open_files:
                    open_files[ip] = open(
                        filename, "a",
                        encoding="utf-8"
                        )
                log_line = f"{timestamp} - {ip}: {message}\n"
                open_files[ip].write(log_line)
                open_files[ip].flush()
            except queue.Empty:
                continue
    finally:
        for f in open_files.values():
            f.close()


if __name__ == "__main__":
    start_server()

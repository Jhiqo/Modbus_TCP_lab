import socket
import sys

def check_python():
    v = sys.version_info
    print(f"[*] Wersja Pythona: {v.major}.{v.minor}.{v.micro} ... ", end="")
    if v.major == 3 and v.minor >= 8:
        print("[OK]")
        return True
    print("[BLAD] Wymagany Python >= 3.8!")
    return False

def check_pymodbus():
    print("[*] Sprawdzanie biblioteki pymodbus ... ", end="")
    try:
        import pymodbus
        ver = getattr(pymodbus, "__version__", "nieznana")
        print(f"[OK] (wersja {ver})")
        return True
    except ImportError:
        print("[BLAD]")
        print("    -> Brak pakietu pymodbus. Wykonaj w terminalu: pip install -r requirements.txt")
        return False

def check_port(port=5020):
    print(f"[*] Sprawdzanie dostepnosci portu {port} ... ", end="")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", port))
        s.close()
        print("[OK]")
        return True
    except OSError:
        print("[OSTRZEZENIE]")
        print(f"    -> Port {port} jest juz zajety! Prawdopodobnie masz uruchomiony proces serwera w tle.")
        return False

def check_loopback():
    print("[*] Sprawdzanie gniazda loopback (127.0.0.1) ... ", end="")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))
        conn, _ = s.accept()
        
        client.close()
        conn.close()
        s.close()
        print("[OK]")
        return True
    except Exception as e:
        print(f"[BLAD] {e}")
        return False

def main():
    print("=" * 60)
    print("  TEST SRODOWISKA LABORATORYJNEGO: MODBUS TCP")
    print("=" * 60)

    results = [
        check_python(),
        check_pymodbus(),
        check_loopback(),
        check_port(),
    ]

    print("=" * 60)
    if all(results):
        print("[SUKCES] Stanowisko w pelni gotowe do laboratorium!")
    else:
        print("[UWAGA] Wykryto problemy konfiguracyjne. Popraw powyzsze bledy przed startem.")
    print("=" * 60)

if __name__ == "__main__":
    main()

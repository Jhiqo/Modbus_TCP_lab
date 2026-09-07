# 🏭 Laboratorium: wprowadzenie do Sieci Przemysłowych (Modbus TCP w Pythonie)

Warsztaty laboratoryjne z komunikacji w warstwie automatyki przemysłowej (OT) i cyberbezpieczeństwa systemów SCADA dla profilu mat-fiz-inf.

---

## ⚡ Szybki start (Krok po kroku)

### 1. Pobranie i instalacja zależności
Otwórz terminal w folderze projektu i uruchom:
```bash
pip install "pymodbus==3.12.0"
```

### 2. Weryfikacja stanowiska komputerowego
Uruchom skrypt diagnostyczny, aby sprawdzić wersję Pythona, pakiety i uprawnienia do portu `5020`:
```bash
python check_environment.py
```
> Jeżeli skrypt zwróci `[SUKCES]`, stanowisko jest w 100% gotowe do pracy.

### 3. Start wirtualnego obiektu technologicznego (Terminal 1)
W osobnym oknie konsoli uruchom symulator zbiornika i wirtualny sterownik PLC:
```bash
python server_tank.py
```
> ⚠️ **Ważne:** To okno symuluje fizykę procesu (dopływ, odpływ, czujniki). **Pozostaw je otwarte w tle przez cały czas trwania laboratorium!**[cite: 1]

### 4. Implementacja regulatora i realizacja zadań (Terminal 2)
W drugim oknie terminala edytujesz i uruchamiasz kod klienta Modbus:
```bash
python controller_template.py
```

---

## 🗺️ Mapa Rejestrów Obiektu (I/O Tag Table)

Komunikacja z procesem technologicznym opiera się na poniższych przestrzeniach adresowych:

| Adres ramki | Przestrzeń Modbus | Typ danych | Symbol ISA-5.1 | Rola inżynierska zmiennej |
| :---: | :--- | :---: | :---: | :--- |
| `0` | **Input Register** | `int16` | **LT-101** | Ciągły pomiar poziomu cieczy $L \in [0, 1000]\text{ l}$ |
| `0` | **Discrete Input** | `bool` | **LSH-101** | Sprzętowy alarm przelania ($1 = \text{stan krytyczny } L \ge 900\text{ l}$) |
| `0` | **Coil** | `bool` | **XV-101** | Elektrozawór spustowy ($0 = \text{zamknięty}, 1 = \text{otwarty}$) |
| `1–2` | **Holding Register**| `float32`| **PT-101** | Ciśnienie hydrostatyczne [bar] w standardzie IEEE 754 (2 rejestry 16-bit) |

---

## 📁 Struktura repozytorium

```text
.
├── check_environment.py     # Narzędzie sprawdzające gotowość systemu i portów
├── server_tank.py           # Symulator procesu technologicznego (serwer Modbus TCP)
├── controller_template.py   # Główny szablon: Zadanie 1 (rozgrzewka) i Zadanie 2 (histereza)
├── bonus_zad2_template.py   # Szablon do zadania dodatkowego z dekodowaniem Float32 (struct)
├── LICENSE                  # Licencja repozytorium
│
└── solutions/               # Wzorcowe kody rozwiązań (do wglądu po ćwiczeniach)
    ├── zad1_hello.py        # Rozwiązanie Zadania 1: odczyt rejestrów i zapis nastawy
    ├── zad2_regulator.py    # Rozwiązanie Zadania 2: dyskretny regulator histerezowy + Fail-Safe
    ├── zad_bonus_float.py   # Rozwiązanie Zadania 5.2: dekodowanie IEEE 754 modułem struct
    ├── bonus_zad1.py        # Rozwiązanie Zadania 5.1: terminalowy wskaźnik ASCII dynamiki
    └── bonus_zad3.py        # Rozwiązanie Zadania 5.3: skrypt ataku na węzeł Modbus sąsiada
```

---

## 🎯 Program ćwiczeń laboratoryjnych

### Część I: Rozgrzewka z magistralą (`controller_template.py`)
* Nawiązanie sesji TCP na porcie `5020`[cite: 1].
* Odczyt rejestru wejściowego (`read_input_registers`) oraz rejestru trzymanego (`read_holding_registers`).
* Modyfikacja nastawy progu w węźle (`write_register`)
  
### Część II: Algorytm sterowania dwupołożeniowego z histerezą (`controller_template.py`)
* Pętla czasu rzeczywistego z kompensacją dryftu zegara (`time.monotonic()`).
* Implementacja nieliniowej pętli histerezy chroniącej zawór przed migotaniem styków (*chattering*):
  * $L > 800\text{ l} \implies$ otwórz odpływ (`Coil 0 -> True`),
  * $L < 300\text{ l} \implies$ zamknij odpływ (`Coil 0 -> False`).
* Zabezpieczenie instalacji przed niekontrolowanym zatrzymaniem skryptu (blok `finally` i zasada *Fail-Safe*).

### Część III: Wyzwania inżynierskie i zadania bonusowe
1. **Wizualizacja ASCII:** Rysowanie poziomu cieczy i progów załączenia bezpośrednio w terminalu[cite: 1].
2. **Reinterpretacja pamięci (`zad_bonus_float_template.py`):** Dekodowanie 32-bitowej liczby zmiennoprzecinkowej (`float32`) z dwóch słów 16-bitowych za pomocą modułu `struct`.
3. **Cyberbezpieczeństwo magistrali (`extra/attack_mitm.py`):** Wstrzykiwanie fałszywych ramek do węzła sąsiada w sieci LAN (dowód na brak szyfrowania i autoryzacji w architekturze protokołu Modbus).
4. **Aliasing czasowy:** Destabilizacja pętli regulacji poprzez celowe zwiększanie okresu próbkowania $T_s$.

---

## 🛠️ Najczęstsze problemy techniczne (FAQ)

* **Błąd `Address already in use` (port 5020 zajęty):** Masz już uruchomiony w tle inny proces `server_tank.py`. Zamknij zbędne terminale lub zakończ proces Pythona w Menedżerze Zadań.
* **Błąd `Connection refused`:** Klient nie może odnaleźć serwera. Upewnij się, że okno z `server_tank.py` wystartowało jako pierwsze i nadal działa.
* **Brak reakcji na wpisywanie `python`:** W systemie Windows spróbuj użyć polecenia `py server_tank.py`.

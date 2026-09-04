# 🏭 Laboratorium: Wprowadzenie do Sieci Przemysłowych (Modbus TCP w Pythonie)

Warsztaty laboratoryjne z komunikacji w warstwie automatyki przemysłowej (OT) i cyberbezpieczeństwa systemów SCADA dla profilu mat-fiz-inf[cite: 1].

---

## ⚡ Szybki start (Krok po kroku)

### 1. Pobranie i instalacja zależności
Otwórz terminal w folderze projektu i uruchom:
```bash
pip install -r requirements.txt
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
> ⚠️ **Ważne:** To okno symuluje fizykę procesu (dopływ, odpływ, czujniki)[cite: 1]. **Pozostaw je otwarte w tle przez cały czas trwania laboratorium!**[cite: 1]

### 4. Implementacja regulatora i realizacja zadań (Terminal 2)
W drugim oknie terminala edytujesz i uruchamiasz kod klienta Modbus[cite: 1]:
```bash
python controller_template.py
```

---

## 🗺️ Mapa Rejestrów Obiektu (I/O Tag Table)

Komunikacja z procesem technologicznym opiera się na poniższych przestrzeniach adresowych[cite: 1]:

| Adres ramki | Przestrzeń Modbus | Typ danych | Symbol ISA-5.1 | Rola inżynierska zmiennej |
| :---: | :--- | :---: | :---: | :--- |
| `0` | **Input Register** | `int16` | **LT-101** | Ciągły pomiar poziomu cieczy $L \in [0, 1000]\text{ l}$[cite: 1] |
| `0` | **Discrete Input** | `bool` | **LSH-101** | Sprzętowy alarm przelania ($1 = \text{stan krytyczny } L \ge 900\text{ l}$)[cite: 1] |
| `0` | **Coil** | `bool` | **XV-101** | Elektrozawór spustowy ($0 = \text{zamknięty}, 1 = \text{otwarty}$)[cite: 1] |
| `1–2` | **Holding Register**| `float32`| **PT-101** | Ciśnienie hydrostatyczne [bar] w standardzie IEEE 754 (2 rejestry 16-bit)[cite: 1] |

---

## 📁 Struktura repozytorium

```text
.
├── check_environment.py          # Automatyczny test środowiska przed labem
├── requirements.txt              # Zależności (przypięta biblioteka pymodbus)
├── server_tank.py                # Emulacja procesu fizycznego i serwer Modbus TCP
├── controller_template.py        # Główny szablon z zadaniami TODO (Zadanie 1 i 2)
├── zad_bonus_float_template.py   # Szablon do odczytu i dekodowania rejestrów Float32
│
├── extra/
│   └── attack_mitm.py            # Skrypt demonstracyjny do ataku na magistralę (Zadanie 5.3)
│
├── solutions/                    # Wzorcowe rozwiązania (do wglądu po ćwiczeniach)
│   ├── zad1_hello.py             # Rozwiązanie: odczyt i zapis rejestrów
│   ├── zad2_regulator.py         # Rozwiązanie: pętla histerezy i obsługa Fail-Safe
│   ├── zad_bonus_float.py        # Rozwiązanie: dekodowanie struct IEEE 754
│   └── zad5_bonus_all.py         # Wszystkie zadania połączone w jednej pętli
│
└── docs/
    └── Modbus_TCP.pdf            # Pełny konspekt teoretyczny i karty pracy[cite: 1]
```

---

## 🎯 Ścieżka ćwiczeń laboratoryjnych

### Część I: Rozgrzewka z magistralą (`controller_template.py`)
* Nawiązanie sesji TCP na porcie `5020`[cite: 1].
* Odczyt rejestru wejściowego (`read_input_registers`) oraz rejestru trzymanego (`read_holding_registers`)[cite: 1].
* Modyfikacja nastawy progu w węźle (`write_register`)[cite: 1].

### Część II: Algorytm sterowania dwupołożeniowego z histerezą (`controller_template.py`)
* Pętla czasu rzeczywistego z kompensacją dryftu zegara (`time.monotonic()`)[cite: 1].
* Implementacja nieliniowej pętli histerezy chroniącej zawór przed migotaniem styków (*chattering*):
  * $L > 800\text{ l} \implies$ otwórz odpływ (`Coil 0 -> True`)[cite: 1],
  * $L < 300\text{ l} \implies$ zamknij odpływ (`Coil 0 -> False`)[cite: 1].
* Zabezpieczenie instalacji przed niekontrolowanym zatrzymaniem skryptu (blok `finally` i zasada *Fail-Safe*)[cite: 1].

### Część III: Wyzwania inżynierskie i zadania bonusowe
1. **Wizualizacja ASCII:** Rysowanie poziomu cieczy i progów załączenia bezpośrednio w terminalu[cite: 1].
2. **Reinterpretacja pamięci (`zad_bonus_float_template.py`):** Dekodowanie 32-bitowej liczby zmiennoprzecinkowej (`float32`) z dwóch słów 16-bitowych za pomocą modułu `struct`[cite: 1].
3. **Cyberbezpieczeństwo magistrali (`extra/attack_mitm.py`):** Wstrzykiwanie fałszywych ramek do węzła sąsiada w sieci LAN (dowód na brak szyfrowania i autoryzacji w architekturze protokołu Modbus)[cite: 1].
4. **Aliasing czasowy:** Destabilizacja pętli regulacji poprzez celowe zwiększanie okresu próbkowania $T_s$[cite: 1].

---

## 🛠️ Najczęstsze problemy techniczne (FAQ)

* **Błąd `Address already in use` (port 5020 zajęty):** Masz już uruchomiony w tle inny proces `server_tank.py`[cite: 1]. Zamknij zbędne terminale lub zakończ proces Pythona w Menedżerze Zadań[cite: 1].
* **Błąd `Connection refused`:** Klient nie może odnaleźć serwera[cite: 1]. Upewnij się, że okno z `server_tank.py` wystartowało jako pierwsze i nadal działa[cite: 1].
* **Brak reakcji na wpisywanie `python`:** W systemie Windows spróbuj użyć polecenia `py server_tank.py`.

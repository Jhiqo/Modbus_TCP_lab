import tkinter as tk
from pymodbus.client import ModbusTcpClient

class TankHMI:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel Operatorski HMI - Zbiornik Buforowy")
        self.root.geometry("460x540")
        self.root.resizable(False, False)
        self.root.configure(bg="#F5F7FA")

        # Klient Modbus do odpytywania serwera
        self.client = ModbusTcpClient("127.0.0.1", port=5020)
        self.connected = False

        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        # Nagłówek
        title = tk.Label(
            self.root, 
            text="MONITORING PROCESU (MODBUS TCP)", 
            font=("Segoe UI", 12, "bold"), 
            fg="#142D55", 
            bg="#F5F7FA"
        )
        title.pack(pady=10)

        # Obszar roboczy grafiki
        self.canvas = tk.Canvas(self.root, width=420, height=440, bg="#FFFFFF", highlightthickness=1, highlightbackground="#DAE0E9")
        self.canvas.pack()

        # Geometria zbiornika na Canvas:
        # X: 110 do 290 (szerokosc 180 px), Y: 80 do 340 (wysokosc 260 px)
        self.tank_x1, self.tank_y1 = 110, 80
        self.tank_x2, self.tank_y2 = 290, 340
        self.max_px = self.tank_y2 - self.tank_y1  # 260 px odpowiada 1000 litrom

        # Rurociąg dopływowy (Góra z lewej)
        self.canvas.create_line([30, 60, 150, 60, 150, 95], width=6, fill="#142D55", arrow=tk.LAST)
        self.canvas.create_text(80, 50, text="Qin (dopływ)", font=("Segoe UI", 9, "bold"), fill="#142D55")

        # Rurociąg odpływowy (Dół w prawo)
        self.canvas.create_line([240, 340, 240, 390, 390, 390], width=6, fill="#142D55", arrow=tk.LAST)
        self.canvas.create_text(340, 375, text="Qout (spust)", font=("Segoe UI", 9, "bold"), fill="#142D55")

        # Obrys zbiornika
        self.canvas.create_rectangle(self.tank_x1, self.tank_y1, self.tank_x2, self.tank_y2, width=3, outline="#142D55", fill="#F8F9FB")

        # Słup cieczy (prostokąt wypełnienia)
        self.liquid_rect = self.canvas.create_rectangle(
            self.tank_x1 + 2, self.tank_y2, self.tank_x2 - 2, self.tank_y2,
            fill="#0077B6", outline=""
        )

        # Podziałka progów (Lmin = 300, Lmax = 800)
        y_800 = self.tank_y2 - (800 / 1000.0) * self.max_px
        y_300 = self.tank_y2 - (300 / 1000.0) * self.max_px
        self.canvas.create_line(self.tank_x1, y_800, self.tank_x2, y_800, dash=(4, 2), fill="#D90429")
        self.canvas.create_text(self.tank_x1 - 35, y_800, text="MAX 800 l", fill="#D90429", font=("Segoe UI", 8, "bold"))
        self.canvas.create_line(self.tank_x1, y_300, self.tank_x2, y_300, dash=(4, 2), fill="#0077B6")
        self.canvas.create_text(self.tank_x1 - 35, y_300, text="MIN 300 l", fill="#0077B6", font=("Segoe UI", 8, "bold"))

        # Cyfrowy odczyt poziomu (tekst na zbiorniku)
        self.txt_level = self.canvas.create_text(200, 210, text="--- l", font=("Segoe UI", 16, "bold"), fill="#142D55")

        # Kontrolka alarmu przelania LSH-101
        self.alarm_indicator = self.canvas.create_oval(320, 90, 355, 125, fill="#E0E0E0", outline="#142D55", width=2)
        self.canvas.create_text(385, 108, text="LSH-101\n(≥900 l)", font=("Segoe UI", 8), fill="#142D55")

        # Kontrolka zaworu XV-101 (symbol na rurociągu spustowym)
        self.valve_box = self.canvas.create_rectangle(270, 375, 305, 405, fill="#6C757D", outline="#142D55", width=2)
        self.txt_valve = self.canvas.create_text(287, 420, text="XV-101: ZAMK", font=("Segoe UI", 8, "bold"), fill="#142D55")

        # Pasek statusu połączenia
        self.status_bar = tk.Label(self.root, text="Status: Brak połączenia", bg="#F5F7FA", fg="#D90429", font=("Segoe UI", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=4)

    def update_loop(self):
        if not self.connected:
            self.connected = self.client.connect()
            if self.connected:
                self.status_bar.config(text="Status: Połączono z 127.0.0.1:5020 [PLC OK]", fg="#2B9348")
            else:
                self.status_bar.config(text="Status: Oczekiwanie na serwer Modbus...", fg="#D90429")

        if self.connected:
            try:
                # 1. Odczyt poziomu cieczy (Input Register 0)
                rr = self.client.read_input_registers(address=0, count=1)
                # 2. Odczyt czujnika przelania (Discrete Input 0)
                r_di = self.client.read_discrete_inputs(address=0, count=1)
                # 3. Odczyt stanu elektrozaworu (Coil 0)
                r_co = self.client.read_coils(address=0, count=1)

                if not (rr.isError() or r_di.isError() or r_co.isError()):
                    level = rr.registers[0]
                    lsh_alarm = r_di.bits[0]
                    valve_open = r_co.bits[0]

                    # Odświeżenie słupa cieczy
                    h_px = (min(1000, max(0, level)) / 1000.0) * self.max_px
                    new_y = self.tank_y2 - h_px
                    self.canvas.coords(self.liquid_rect, self.tank_x1 + 2, new_y, self.tank_x2 - 2, self.tank_y2)

                    # Odświeżenie tekstu poziomu
                    self.canvas.itemconfig(self.txt_level, text=f"{level} l")

                    # Odświeżenie czujnika przelania (LSH)
                    self.canvas.itemconfig(self.alarm_indicator, fill="#D90429" if lsh_alarm else "#E0E0E0")

                    # Odświeżenie zaworu (XV-101)
                    if valve_open:
                        self.canvas.itemconfig(self.valve_box, fill="#2B9348")
                        self.canvas.itemconfig(self.txt_valve, text="XV-101: OTW", fill="#2B9348")
                    else:
                        self.canvas.itemconfig(self.valve_box, fill="#6C757D")
                        self.canvas.itemconfig(self.txt_valve, text="XV-101: ZAMK", fill="#142D55")

            except Exception:
                self.connected = False
                self.status_bar.config(text="Status: Utracono połączenie z magistralą", fg="#D90429")

        # Kolejne odświeżenie za 100 ms (10 Hz)
        self.root.after(100, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = TankHMI(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
import pandas as pd
import datetime
import json
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BolsaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Bolsa - Finmarkets")
        self.root.geometry("900x700")

        # --- CARGA DE NOMBRES DESDE JSON ---
        self.archivo_json = "nombres.json"
        self.nombres_conocidos = self.cargar_nombres()

        # --- PANEL SUPERIOR: CONTROLES ---
        control_frame = ttk.LabelFrame(root, text="Configuración de Consulta", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        # ID Input
        ttk.Label(control_frame, text="ID Notación:").grid(row=0, column=0, padx=5)
        self.entry_id = ttk.Entry(control_frame, width=15)
        self.entry_id.insert(0, "77447") 
        self.entry_id.grid(row=0, column=1, padx=5)

        # Time Span Input
        ttk.Label(control_frame, text="Periodo:").grid(row=0, column=2, padx=5)
        self.entry_span = ttk.Combobox(control_frame, values=["1D", "5D", "1M", "3M", "6M", "1Y"], width=10)
        self.entry_span.current(0) 
        self.entry_span.grid(row=0, column=3, padx=5)

        # Botón Ejecutar
        self.btn_run = ttk.Button(control_frame, text="Consultar Datos", command=self.fetch_data)
        self.btn_run.grid(row=0, column=4, padx=15)

        # --- PANEL MEDIO: ESTADÍSTICAS ---
        stats_frame = ttk.LabelFrame(root, text="Estadísticas Clave", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_precio = ttk.Label(stats_frame, text="Precio: ---", font=("Arial", 14, "bold"))
        self.lbl_precio.pack(side="left", padx=20)
        
        self.lbl_minmax = ttk.Label(stats_frame, text="Min/Max: --- / ---", font=("Arial", 10))
        self.lbl_minmax.pack(side="left", padx=20)

        self.lbl_vol = ttk.Label(stats_frame, text="Volumen Total: ---", font=("Arial", 10))
        self.lbl_vol.pack(side="left", padx=20)

        # --- PANEL INFERIOR: GRÁFICO ---
        self.plot_frame = tk.Frame(root)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def cargar_nombres(self):
        """Carga el diccionario desde el archivo JSON si existe"""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showwarning("Aviso", f"Error leyendo nombres.json: {e}")
                return {}
        else:
            # Si no existe, retorna diccionario vacío (o podrías crearlo aquí)
            return {}

    def fetch_data(self):
        id_nota = self.entry_id.get()
        time_span = self.entry_span.get()
        
        if not id_nota or not time_span:
            messagebox.showerror("Error", "Por favor ingresa ID y Periodo")
            return

        url = f"https://bancoestado.finmarketslive.cl/www/chart/datachart.php?ID_NOTATION={id_nota}&TIME_SPAN={time_span}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Error servidor: {response.status_code}")
            
            raw_data = response.text
            pattern = r"\{date:new Date\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\),close:([\d\.]+)(?:,volume:(\d+))?\}"
            matches = re.findall(pattern, raw_data)

            if not matches:
                messagebox.showwarning("Sin datos", "No se encontraron datos. Verifica el ID.")
                return

            data = []
            for m in matches:
                year, month, day, hour, minute, second, close, volume = m
                dt = datetime.datetime(int(year), int(month) + 1, int(day), int(hour), int(minute), int(second))
                data.append({
                    'fecha': dt,
                    'valor': float(close),
                    'volumen': int(volume) if volume else 0
                })

            df = pd.DataFrame(data)

            self.update_stats(df)
            self.update_chart(df, id_nota)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_stats(self, df):
        ultimo = df.iloc[-1]['valor']
        maximo = df['valor'].max()
        minimo = df['valor'].min()
        volumen_total = df['volumen'].sum()

        self.lbl_precio.config(text=f"Precio: ${ultimo:,.2f}")
        self.lbl_minmax.config(text=f"Min: ${minimo:,.2f}  |  Max: ${maximo:,.2f}")
        self.lbl_vol.config(text=f"Volumen Acum: {volumen_total:,}")

    def update_chart(self, df, title_id):
        self.ax.clear()
        
        # Busca el nombre en el diccionario cargado desde JSON
        nombre_mostrar = self.nombres_conocidos.get(title_id, f"ID: {title_id}")

        self.ax.plot(df['fecha'], df['valor'], color='#17375e', linewidth=1.5)
        self.ax.set_title(f"Instrumento: {nombre_mostrar}", fontsize=12, fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.tick_params(axis='x', rotation=45, labelsize=8)
        
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = BolsaApp(root)
    root.mainloop()
import customtkinter as ctk
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np

# Colores para el tema oscuro
BG_COLOR = "#2b2b2b"  # Fondo del gráfico
TEXT_COLOR = "white"  # Texto de ejes y títulos
LINE_COLOR = "#3B8ED0" # Azul CustomTkinter

class BolsaChart:
    def __init__(self, parent_frame):
        # Configuración inicial del gráfico con colores oscuros
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor=BG_COLOR)
        self.ax = self.figure.add_subplot(111)
        
        # Configurar colores iniciales del eje
        self.ax.set_facecolor(BG_COLOR)
        self.ax.tick_params(axis='x', colors=TEXT_COLOR)
        self.ax.tick_params(axis='y', colors=TEXT_COLOR)
        self.ax.yaxis.label.set_color(TEXT_COLOR)
        self.ax.xaxis.label.set_color(TEXT_COLOR)
        
        # Bordes (spines) blancos
        for spine in self.ax.spines.values():
            spine.set_color(TEXT_COLOR)

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Conectamos el evento hover
        self.canvas.mpl_connect("motion_notify_event", self.hover)
        
        self.df = None
        self.annot = None

    def draw_chart(self, df, title, compra_point=None):
        self.df = df
        if self.df is None: return

        self.ax.clear()
        
        # Re-aplicar estilos oscuros tras el clear()
        self.ax.set_facecolor(BG_COLOR)
        self.ax.grid(True, linestyle='--', alpha=0.3, color="gray") # Grid más sutil

        # Dibujar línea
        self.ax.plot(self.df['fecha'], self.df['valor'], color=LINE_COLOR, linewidth=2)
        
        # Formato Fechas
        if self.df['fecha'].iloc[-1].date() == self.df['fecha'].iloc[0].date():
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        else:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        
        self.figure.autofmt_xdate(rotation=45)
        
        # Título y etiquetas en blanco
        self.ax.set_title(f"Instrumento: {title}", fontweight='bold', color=TEXT_COLOR)
        self.ax.tick_params(axis='both', colors=TEXT_COLOR)
        for spine in self.ax.spines.values(): spine.set_color(TEXT_COLOR)

        # Punto de compra
        if compra_point:
            fecha, precio = compra_point
            self.ax.plot(fecha, precio, 'o', color="#ff4d4d", label='Compra', markersize=8)
            # Leyenda con texto blanco
            legend = self.ax.legend(facecolor=BG_COLOR, edgecolor=TEXT_COLOR)
            for text in legend.get_texts(): text.set_color(TEXT_COLOR)

        # Tooltip oculto
        self.annot = self.ax.annotate(
            "", 
            xy=(0,0), 
            xytext=(15,15), 
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="#1f1f1f", ec="white", alpha=0.9), # Fondo oscuro, borde blanco
            arrowprops=dict(arrowstyle="->", color="white"),
            color="white" # Texto blanco
        )
        self.annot.set_visible(False)

        self.canvas.draw()

    def hover(self, event):
        if self.df is None or self.annot is None: return
        
        if event.inaxes != self.ax:
            if self.annot.get_visible():
                self.annot.set_visible(False)
                self.canvas.draw_idle()
            return

        lines = self.ax.get_lines()
        if not lines: return
        line = lines[0]
        x_data = line.get_xdata()

        try:
            x_data_nums = mdates.date2num(x_data)
            idx = np.abs(x_data_nums - event.xdata).argmin()
        except Exception:
            return 

        fila = self.df.iloc[idx]
        fecha = fila['fecha']
        valor = fila['valor']

        self.annot.xy = (x_data[idx], valor)

        if self.df['fecha'].iloc[-1].date() == self.df['fecha'].iloc[0].date():
            fecha_str = fecha.strftime("%H:%M")
        else:
            fecha_str = fecha.strftime("%d/%m/%Y %H:%M")

        text = f"{fecha_str}\n${valor:,.2f}"
        self.annot.set_text(text)
        self.annot.set_visible(True)
        
        self.canvas.draw_idle()
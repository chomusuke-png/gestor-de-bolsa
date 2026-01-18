import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np

class BolsaChart:
    def __init__(self, parent_frame):
        # Configuración inicial del gráfico
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Conectamos el evento hover
        self.canvas.mpl_connect("motion_notify_event", self.hover)
        
        # Variables de estado
        self.df = None
        self.annot = None

    def draw_chart(self, df, title, compra_point=None):
        """Dibuja el gráfico principal y configura la anotación oculta"""
        self.df = df
        if self.df is None: return

        self.ax.clear()

        # Dibujar línea
        self.ax.plot(self.df['fecha'], self.df['valor'], color='#17375e', linewidth=1.5)
        
        # Formato Fechas (Eje X)
        if self.df['fecha'].iloc[-1].date() == self.df['fecha'].iloc[0].date():
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        else:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        
        self.figure.autofmt_xdate(rotation=45)
        self.ax.set_title(f"Instrumento: {title}", fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.6)

        # Dibujar punto de compra (si existe)
        if compra_point:
            fecha, precio = compra_point
            self.ax.plot(fecha, precio, 'ro', label='Compra')
            self.ax.legend()

        # Crear la anotación (tooltip) oculta inicial
        self.annot = self.ax.annotate(
            "", 
            xy=(0,0), 
            xytext=(15,15), 
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", ec="gray", alpha=0.9),
            arrowprops=dict(arrowstyle="->")
        )
        self.annot.set_visible(False)

        self.canvas.draw()

    def hover(self, event):
        """Maneja el evento del mouse para mostrar el tooltip"""
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

        # --- CORRECCIÓN CRÍTICA DE FECHAS ---
        try:
            # Convertimos fechas a números para poder restar con event.xdata
            x_data_nums = mdates.date2num(x_data)
            idx = np.abs(x_data_nums - event.xdata).argmin()
        except Exception:
            return 
        # ------------------------------------

        fila = self.df.iloc[idx]
        fecha = fila['fecha']
        valor = fila['valor']

        # Actualizamos posición del tooltip
        # Usamos x_data[idx] (fecha original) porque annotate lo entiende
        self.annot.xy = (x_data[idx], valor)

        if self.df['fecha'].iloc[-1].date() == self.df['fecha'].iloc[0].date():
            fecha_str = fecha.strftime("%H:%M")
        else:
            fecha_str = fecha.strftime("%d/%m/%Y %H:%M")

        text = f"{fecha_str}\n${valor:,.2f}"
        self.annot.set_text(text)
        self.annot.set_visible(True)
        
        self.canvas.draw_idle()
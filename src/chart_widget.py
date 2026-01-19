import customtkinter as ctk
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np

class BolsaChart:
    def __init__(self, parent_frame, theme):
        self.theme = theme
        self.parent_frame = parent_frame
        
        bg_color = self._get_color("frame_bg")
        
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor=bg_color)
        self.ax = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.canvas.mpl_connect("motion_notify_event", self.hover)
        
        self.df = None
        self.annot = None

    def _get_color(self, key):
        mode = ctk.get_appearance_mode() # "Light" o "Dark"
        colors = self.theme.get(key, ("#ffffff", "#000000"))
        return colors[0] if mode == "Light" else colors[1]

    def draw_chart(self, df, title, compra_point=None):
        self.df = df
        if self.df is None: return

        # Obtenemos colores actuales
        bg_color = self._get_color("frame_bg")
        text_color = self._get_color("text_main")
        line_color = self._get_color("chart_line")
        grid_color = self._get_color("chart_grid")

        self.ax.clear()
        
        # Aplicar estilos
        self.figure.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)

        # Dibujar línea
        self.ax.plot(self.df['fecha'], self.df['valor'], color=line_color, linewidth=2)
        
        # Ejes y textos
        if self.df['fecha'].iloc[-1].date() == self.df['fecha'].iloc[0].date():
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        else:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        
        self.figure.autofmt_xdate(rotation=45)
        
        self.ax.set_title(f"Instrumento: {title}", fontweight='bold', color=text_color)
        self.ax.tick_params(axis='both', colors=text_color)
        self.ax.yaxis.label.set_color(text_color)
        self.ax.xaxis.label.set_color(text_color)
        
        for spine in self.ax.spines.values(): 
            spine.set_color(text_color)

        # Punto de compra
        if compra_point:
            fecha, precio = compra_point
            c_marker = self._get_color("chart_buy_marker")
            self.ax.plot(fecha, precio, 'o', color=c_marker, label='Compra', markersize=8)
            legend = self.ax.legend(facecolor=bg_color, edgecolor=text_color)
            for text in legend.get_texts(): text.set_color(text_color)

        # Tooltip
        self.annot = self.ax.annotate(
            "", 
            xy=(0,0), 
            xytext=(15,15), 
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc=self._get_color("list_hover"), ec=text_color, alpha=0.9),
            arrowprops=dict(arrowstyle="->", color=text_color),
            color=text_color
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

        self.annot.set_text(f"{fecha_str}\n${valor:,.2f}")
        self.annot.set_visible(True)
        self.canvas.draw_idle()
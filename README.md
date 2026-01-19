### Para compilar y crear el .exe
```shortcode
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "nombres.json;." main.py
```

### ¿Cómo usarlo?

* Ingresa el ID (ej. 77447).

* Elige el periodo que cubra tu fecha de compra (si compraste hace 2 meses, elige 3M o 1Y, no 1D).

* Dale a "Consultar Datos".

* Abajo, pon cuánto invertiste (ej. 100000).

* Pon la fecha (ej. 2025-12-20 14:00).

* Dale a "Calcular Ganancia".
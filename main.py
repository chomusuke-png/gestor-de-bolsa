import customtkinter as ctk
from src.gui import BolsaApp

# Configuración global del tema
ctk.set_appearance_mode("System")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"

if __name__ == "__main__":
    root = ctk.CTk()
    app = BolsaApp(root)
    root.mainloop()
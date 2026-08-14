import datetime
import customtkinter as ctk
from PIL import Image, ImageTk
from database_kiosco import inicializar_bd
from login_kiosco import LoginWindow
from modulo_ventas import VentasFrame
from modulo_productos import ProductosFrame
from modulo_reportes import ReportesFrame

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Paleta Cálida y Limpia para la App Principal
COLORES = {
    "sidebar": "#EFECE6",         # Tono madera clara / gris arena para la barra lateral
    "fondo_principal": "#F4F1EA", # Fondo general cálido
    "fondo_card": "#FFFFFF",      # Paneles blancos impecables
    "acento": "#D35400",          # Naranja terracota principal
    "acento_hover": "#BA4A00",
    "texto_principal": "#2C3E50", # Texto oscuro muy legible
    "texto_secundario": "#7F8C8D",# Texto secundario gris
    "eliminar": "#C0392B",
    "eliminar_hover": "#962D22"
}

FONT_TITULO = ("Roboto", 22, "bold")
FONT_SUBTITULO = ("Roboto", 16, "bold")
FONT_ESTANDAR = ("Roboto", 13)
FONT_BOTON = ("Roboto", 13, "bold")

class KioscoMainApp(ctk.CTk):
    def __init__(self, username, rol):
        super().__init__()
        
        self.username = username
        self.rol = rol

        self.title("Universum - Sistema de Kiosco PRO")
        self.geometry("1150x680")
        self.minsize(1000, 600)
        self.configure(fg_color=COLORES["fondo_principal"])

        # Forzar actualización y centrar perfectamente en la pantalla
        self.update_idletasks()
        self.centrar_ventana(1150, 680)

        # Configurar grilla principal (Sidebar / Contenido)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_sidebar()
        self.crear_panel_principal()

        self.mostrar_ventas()

    def centrar_ventana(self, ancho, alto):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width // 2) - (ancho // 2)
        # Le restamos 40 o 50 píxeles para subirla un poco y que no la tape la barra de tareas
        y = ((screen_height // 2) - (alto // 2)) - 45 
        
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=COLORES["sidebar"], corner_radius=0, width=230)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

       # Logo superior en el Sidebar (Más grande y centrado)
        try:
            img_pil = Image.open("universum.jpg").resize((80, 80))
            self.logo_sidebar_img = ImageTk.PhotoImage(img_pil)
            lbl_logo = ctk.CTkLabel(self.sidebar_frame, text="", image=self.logo_sidebar_img)
        except Exception:
            lbl_logo = ctk.CTkLabel(self.sidebar_frame, text="✨", font=("Roboto", 24), text_color=COLORES["texto_principal"])
        
        # Al quitar el "sticky='w'", se centra automáticamente en el ancho del sidebar
        lbl_logo.grid(row=0, column=0, padx=0, pady=(25, 20), sticky="")

        # Botones de navegación
        self.btn_nav_ventas = self.crear_boton_nav("🛒   Ventas (POS)", self.mostrar_ventas, 1)
        self.btn_nav_productos = self.crear_boton_nav("📦   Productos", self.mostrar_productos, 2)
        self.btn_nav_reportes = self.crear_boton_nav("📊   Reportes & Caja", self.mostrar_reportes, 3)

        # --- TARJETA DE SESIÓN PRO (Diseño limpio y ordenado) ---
        user_card = ctk.CTkFrame(self.sidebar_frame, fg_color="#E4DFD5", corner_radius=8)
        user_card.grid(row=6, column=0, padx=15, pady=10, sticky="ew")
        
        lbl_user_icon = ctk.CTkLabel(user_card, text=f"👤   {self.username.capitalize()}", font=("Roboto", 13, "bold"), text_color=COLORES["texto_principal"])
        lbl_user_icon.pack(anchor="w", padx=12, pady=(8, 2))
        
        lbl_rol_info = ctk.CTkLabel(user_card, text=f"Rol: {self.rol.upper()}", font=("Roboto", 11), text_color=COLORES["texto_secundario"])
        lbl_rol_info.pack(anchor="w", padx=12, pady=(0, 8))
        # --------------------------------------------------------

        # Botón Cerrar Sesión
        btn_salir = ctk.CTkButton(
            self.sidebar_frame, text="Cerrar Sesión", font=FONT_BOTON, height=38,
            fg_color=COLORES["eliminar"], hover_color=COLORES["eliminar_hover"], text_color="#FFFFFF",
            command=self.cerrar_sesion
        )
        btn_salir.grid(row=7, column=0, padx=15, pady=(10, 20), sticky="ew")

    def crear_boton_nav(self, texto, comando, fila):
        btn = ctk.CTkButton(
            self.sidebar_frame, text=texto, font=FONT_BOTON, height=42,
            fg_color="transparent", text_color=COLORES["texto_principal"],
            hover_color="#E4DFD5", anchor="w", command=comando
        )
        btn.grid(row=fila, column=0, padx=15, pady=6, sticky="ew")
        return btn

    def crear_panel_principal(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Header Superior compacto y ordenado por grilla
        header_frame = ctk.CTkFrame(self.main_container, fg_color=COLORES["fondo_card"], height=55, corner_radius=10, border_width=1, border_color="#E0DCD0")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        lbl_user = ctk.CTkLabel(header_frame, text=f"👤 Usuario: {self.username}", font=FONT_BOTON, text_color=COLORES["texto_principal"])
        lbl_user.grid(row=0, column=0, sticky="w", padx=20, pady=12)

        self.lbl_reloj = ctk.CTkLabel(header_frame, text="", font=FONT_ESTANDAR, text_color=COLORES["texto_secundario"])
        self.lbl_reloj.grid(row=0, column=1, sticky="e", padx=20, pady=12)
        self.actualizar_reloj()

        # Contenedor Dinámico
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew")

    def actualizar_reloj(self):
        ahora = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        self.lbl_reloj.configure(text=ahora)
        self.after(1000, self.actualizar_reloj)

    def limpiar_contenido(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def mostrar_ventas(self):
        self.limpiar_contenido()
        self.vista_ventas = VentasFrame(self.content_frame, COLORES, username=self.username)
        self.vista_ventas.pack(fill="both", expand=True)
        
    def mostrar_productos(self):
        self.limpiar_contenido()
        self.vista_productos = ProductosFrame(self.content_frame, COLORES)
        self.vista_productos.pack(fill="both", expand=True)
   
    def mostrar_reportes(self):
        self.limpiar_contenido()
        self.vista_reportes = ReportesFrame(self.content_frame, COLORES)
        self.vista_reportes.pack(fill="both", expand=True)

    def cerrar_sesion(self):
        self.destroy()
        lanzar_login()


def lanzar_login():
    inicializar_bd()
    
    def on_success(username, rol):
        app_principal = KioscoMainApp(username, rol)
        app_principal.mainloop()

    login = LoginWindow(on_login_success=on_success)
    login.mainloop()

if __name__ == "__main__":
    lanzar_login()
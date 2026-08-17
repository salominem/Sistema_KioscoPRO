import datetime
import customtkinter as ctk
from PIL import Image, ImageTk
from database_kiosco import inicializar_bd
from modulo_ventas import VentasFrame
from modulo_productos import ProductosFrame
from modulo_reportes import ReportesFrame
from tkinter import messagebox

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


class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        
        self.on_login_success = on_login_success
        
        self.title("Universum - Iniciar Sesión")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Cargar el ícono en la ventana de Login
        try:
            self.iconbitmap("universum.ico")
        except Exception:
            pass
        
        # Colores originales del Kiosco aplicados al login
        self.colores = {
            "fondo_ventana": "#F4F1EA", 
            "fondo_card": "#FFFFFF",
            "texto_principal": "#2C3E50",
            "texto_secundario": "#7F8C8D",
            "acento": "#D35400",
            "acento_hover": "#BA4A00"
        }
        
        self.configure(fg_color=self.colores["fondo_ventana"])

        # Centrar ventana de login
        self.update_idletasks()
        w = 400
        h = 500
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Contenedor principal estilo tarjeta
        card = ctk.CTkFrame(self, fg_color=self.colores["fondo_card"], corner_radius=15, border_width=1, border_color="#E0DCD0")
        card.pack(fill="both", expand=True, padx=25, pady=25)

        # --- ZONA SUPERIOR: LOGO Y TÍTULOS ---
        try:
            self.logo_img = ctk.CTkImage(light_image=Image.open("universum.jpg"), size=(60, 60))
            lbl_logo = ctk.CTkLabel(card, image=self.logo_img, text="")
            lbl_logo.pack(pady=(25, 5))
        except Exception:
            lbl_logo_txt = ctk.CTkLabel(card, text="✦ Universum", font=("Roboto", 16, "bold"), text_color=self.colores["acento"])
            lbl_logo_txt.pack(pady=(25, 5))

        lbl_titulo = ctk.CTkLabel(card, text="Sistema Kiosco PRO", font=("Roboto", 20, "bold"), text_color=self.colores["texto_principal"])
        lbl_titulo.pack(pady=(0, 2))

        lbl_sub = ctk.CTkLabel(card, text="Acceso al Sistema", font=("Roboto", 12), text_color=self.colores["texto_secundario"])
        lbl_sub.pack(pady=(0, 20))

        # --- CAMPOS DE ENTRADA ---
        self.entry_usuario = ctk.CTkEntry(
            card, placeholder_text="Usuario", font=("Roboto", 13), width=280, height=40,
            fg_color="#F9F9F9", border_color="#CBD5E1", text_color=self.colores["texto_principal"]
        )
        self.entry_usuario.pack(pady=10)
        self.entry_usuario.focus()

        self.entry_password = ctk.CTkEntry(
            card, placeholder_text="Contraseña", font=("Roboto", 13), width=280, height=40,
            show="*", fg_color="#F9F9F9", border_color="#CBD5E1", text_color=self.colores["texto_principal"]
        )
        self.entry_password.pack(pady=(10, 20))
        self.entry_password.bind("<Return>", lambda event: self.verificar_login())

        # --- BOTÓN INGRESAR ---
        btn_ingresar = ctk.CTkButton(
            card, text="Ingresar", font=("Roboto", 14, "bold"), width=280, height=42,
            fg_color=self.colores["acento"], hover_color=self.colores["acento_hover"],
            text_color="#FFFFFF", corner_radius=6,
            command=self.verificar_login
        )
        btn_ingresar.pack(pady=(10, 25))

    def verificar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        
        if usuario != "" and password != "":
            self.destroy()
            self.on_login_success(usuario, "administrador")
        else:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña", parent=self)


class KioscoMainApp(ctk.CTk):
    def __init__(self, username, rol):
        super().__init__()
        
        self.username = username
        self.rol = rol

        self.title("Universum - Sistema de Kiosco PRO")
        self.geometry("1150x680")
        self.minsize(1000, 600)
        self.configure(fg_color=COLORES["fondo_principal"])

        # Intentar cargar el ícono de la ventana (esquina superior izquierda)
        try:
            self.iconbitmap("universum.ico")
        except Exception:
            pass

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
        y = ((screen_height // 2) - (alto // 2)) - 45 
        
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=COLORES["sidebar"], corner_radius=0, width=230)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo superior en el Sidebar
        try:
            img_pil = Image.open("universum.jpg").resize((80, 80))
            self.logo_sidebar_img = ImageTk.PhotoImage(img_pil)
            lbl_logo = ctk.CTkLabel(self.sidebar_frame, text="", image=self.logo_sidebar_img)
        except Exception:
            lbl_logo = ctk.CTkLabel(self.sidebar_frame, text="✨", font=("Roboto", 24), text_color=COLORES["texto_principal"])
        
        lbl_logo.grid(row=0, column=0, padx=0, pady=(25, 20), sticky="")

        # Botones de navegación
        self.btn_nav_ventas = self.crear_boton_nav("🛒   Ventas (POS)", self.mostrar_ventas, 1)
        self.btn_nav_productos = self.crear_boton_nav("📦   Productos", self.mostrar_productos, 2)
        self.btn_nav_reportes = self.crear_boton_nav("📊   Reportes & Caja", self.mostrar_reportes, 3)

        # --- TARJETA DE SESIÓN PRO ---
        user_card = ctk.CTkFrame(self.sidebar_frame, fg_color="#E4DFD5", corner_radius=8)
        user_card.grid(row=6, column=0, padx=15, pady=10, sticky="ew")
        
        lbl_user_icon = ctk.CTkLabel(user_card, text=f"👤   {self.username.capitalize()}", font=("Roboto", 13, "bold"), text_color=COLORES["texto_principal"])
        lbl_user_icon.pack(anchor="w", padx=12, pady=(8, 2))
        
        lbl_rol_info = ctk.CTkLabel(user_card, text=f"Rol: {self.rol.upper()}", font=("Roboto", 11), text_color=COLORES["texto_secundario"])
        lbl_rol_info.pack(anchor="w", padx=12, pady=(0, 8))

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

        header_frame = ctk.CTkFrame(self.main_container, fg_color=COLORES["fondo_card"], height=55, corner_radius=10, border_width=1, border_color="#E0DCD0")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        lbl_user = ctk.CTkLabel(header_frame, text=f"👤 Usuario: {self.username}", font=FONT_BOTON, text_color=COLORES["texto_principal"])
        lbl_user.grid(row=0, column=0, sticky="w", padx=20, pady=12)

        self.lbl_reloj = ctk.CTkLabel(header_frame, text="", font=FONT_ESTANDAR, text_color=COLORES["texto_secundario"])
        self.lbl_reloj.grid(row=0, column=1, sticky="e", padx=20, pady=12)
        self.actualizar_reloj()

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
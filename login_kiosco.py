import customtkinter as ctk
from PIL import Image, ImageTk
from database_kiosco import Usuario, hashear_password, inicializar_bd

# Configuramos apariencia general en modo Light (Claro) o neutro para manejar nuestra paleta cálida
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Paleta Cálida y Elegante (Tonos arena, madera suave, blancos y detalles cálidos)
COLORES = {
    "fondo": "#F4F1EA",         # Blanco cálido / hueso muy suave
    "card": "#FFFFFF",          # Tarjetas blancas puras
    "acento": "#D35400",        # Naranja terracota cálido (Ideal para llamadas a la acción)
    "acento_hover": "#BA4A00",  # Naranja más oscuro para hover
    "texto": "#2C3E50",         # Gris oscuro elegante para leer perfecto
    "secundario": "#7F8C8D",    # Gris suave para subtítulos
    "error": "#C0392B"
}

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        inicializar_bd()

        self.on_login_success = on_login_success
        self.title("Universum - Iniciar Sesión")
        self.geometry("400x520")
        self.resizable(False, False)
        self.configure(fg_color=COLORES["fondo"])

        # Centrar ventana perfectamente en el medio de la pantalla
        self.centrar_ventana(400, 520)
        self.crear_interfaz()

    def centrar_ventana(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_interfaz(self):
        # Contenedor central tipo Card (Blanco sobre fondo cálido)
        card = ctk.CTkFrame(self, fg_color=COLORES["card"], corner_radius=15, border_width=1, border_color="#E0DCD0")
        card.pack(fill="both", expand=True, padx=25, pady=25)

        # Cargar y mostrar el logo
        try:
            img_pil = Image.open("universum.png").resize((80, 80))
            self.logo_img = ImageTk.PhotoImage(img_pil)
            lbl_logo = ctk.CTkLabel(card, text="", image=self.logo_img)
            lbl_logo.pack(pady=(25, 10))
        except Exception:
            ctk.CTkLabel(card, text="✨ Universum", font=("Roboto", 20, "bold"), text_color=COLORES["acento"]).pack(pady=(25, 10))

        ctk.CTkLabel(card, text="Sistema Kiosco PRO", font=("Roboto", 18, "bold"), text_color=COLORES["texto"]).pack(pady=(0, 20))

        # Campos de entrada (Fondo blanco/claro)
        self.entry_user = ctk.CTkEntry(card, placeholder_text="Usuario", font=("Roboto", 13), width=260, height=40, fg_color="#F9F9F9", text_color=COLORES["texto"])
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(card, placeholder_text="Contraseña", font=("Roboto", 13), width=260, height=40, show="*", fg_color="#F9F9F9", text_color=COLORES["texto"])
        self.entry_pass.pack(pady=10)

        self.lbl_error = ctk.CTkLabel(card, text="", font=("Roboto", 12), text_color=COLORES["error"])
        self.lbl_error.pack(pady=5)

        # Botón Ingresar
        btn_ingresar = ctk.CTkButton(
            card, text="Ingresar", font=("Roboto", 14, "bold"), width=260, height=40,
            fg_color=COLORES["acento"], hover_color=COLORES["acento_hover"], text_color="#FFFFFF",
            command=self.verificar_credenciales
        )
        btn_ingresar.pack(pady=(10, 25))

        self.bind("<Return>", lambda event: self.verificar_credenciales())

    def verificar_credenciales(self):
        user = self.entry_user.get().strip()
        passw = self.entry_pass.get().strip()

        if not user or not passw:
            self.lbl_error.configure(text="Complete todos los campos.")
            return

        pass_hash = hashear_password(passw)
        
        try:
            usuario_db = Usuario.get((Usuario.username == user) & (Usuario.password == pass_hash))
            self.destroy()
            self.on_login_success(usuario_db.username, usuario_db.rol)
        except Usuario.DoesNotExist:
            self.lbl_error.configure(text="Usuario o contraseña incorrectos.")
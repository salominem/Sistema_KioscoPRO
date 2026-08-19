import customtkinter as ctk
from tkinter import messagebox
from database_kiosco import Usuario, hashear_password

class EmpleadosFrame(ctk.CTkFrame):
    def __init__(self, master, colores, rol_usuario="cajero", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colores = colores
        self.rol_usuario = rol_usuario.lower().strip()
        self.empleado_seleccionado_id = None
        
        # Validar si es administrador real
        es_admin = self.rol_usuario in ["admin", "administrador"]
        
        # Configuración de grilla
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO: FORMULARIO ---
        self.frame_form = ctk.CTkFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10, border_width=1, border_color="#E0DCD0")
        self.frame_form.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        
        ctk.CTkLabel(self.frame_form, text="Gestión de Empleados", font=("Roboto", 16, "bold"), text_color=self.colores["texto_principal"]).pack(pady=20)
        
        # Campos de entrada
        ctk.CTkLabel(self.frame_form, text="Nombre de Usuario:", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(5, 0))
        self.ent_nombre = ctk.CTkEntry(self.frame_form, height=38, fg_color="#F9F9F9", border_color="#D5D0C0")
        self.ent_nombre.pack(pady=(2, 10), padx=20, fill="x")

        ctk.CTkLabel(self.frame_form, text="Contraseña:", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(2, 0))
        self.ent_pass = ctk.CTkEntry(self.frame_form, show="*", height=38, fg_color="#F9F9F9", border_color="#D5D0C0")
        self.ent_pass.pack(pady=(2, 10), padx=20, fill="x")

        ctk.CTkLabel(self.frame_form, text="Rol del Empleado:", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(2, 0))
        self.combo_rol = ctk.CTkComboBox(self.frame_form, values=["cajero"], height=38, state="readonly")
        self.combo_rol.pack(pady=(2, 20), padx=20, fill="x")
        self.combo_rol.set("cajero")
        
        # Botones de acción
        self.btn_guardar = ctk.CTkButton(
            self.frame_form, text="Guardar Empleado", font=("Roboto", 13, "bold"), height=38,
            fg_color=self.colores["acento"], hover_color=self.colores["acento_hover"],
            command=self.guardar_empleado
        )
        self.btn_guardar.pack(pady=(0, 10), padx=20, fill="x")

        self.btn_eliminar = ctk.CTkButton(
            self.frame_form, text="Eliminar Empleado", font=("Roboto", 12, "bold"), height=35,
            fg_color="#C0392B", hover_color="#962D22", text_color="#FFFFFF",
            command=self.eliminar_empleado
        )
        self.btn_eliminar.pack(pady=(0, 10), padx=20, fill="x")

        btn_limpiar = ctk.CTkButton(
            self.frame_form, text="Limpiar Campos", font=("Roboto", 12), height=32,
            fg_color="#7F8C8D", hover_color="#626D6E", text_color="#FFFFFF",
            command=self.limpiar_formulario
        )
        btn_limpiar.pack(pady=(0, 20), padx=20, fill="x")

        # Bloquear formulario si NO es administrador
        if not es_admin:
            self.ent_nombre.configure(state="disabled")
            self.ent_pass.configure(state="disabled")
            self.combo_rol.configure(state="disabled")
            self.btn_guardar.configure(state="disabled", fg_color="#BDC3C7")
            self.btn_eliminar.configure(state="disabled", fg_color="#BDC3C7")
            
            lbl_aviso = ctk.CTkLabel(self.frame_form, text="⚠️ Acceso restringido:\nSolo el administrador puede gestionar personal.", font=("Roboto", 11, "bold"), text_color="#C0392B")
            lbl_aviso.pack(pady=10)

        # --- PANEL DERECHO: LISTA DE EMPLEADOS ---
        self.lista_empleados = ctk.CTkScrollableFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10, border_width=1, border_color="#E0DCD0")
        self.lista_empleados.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        
        ctk.CTkLabel(self.lista_empleados, text="Personal Registrado", font=("Roboto", 16, "bold"), text_color=self.colores["texto_principal"]).pack(pady=15)
        
        self.actualizar_lista()

    def guardar_empleado(self):
        if self.rol_usuario not in ["admin", "administrador"]:
            messagebox.showerror("Acceso Denegado", "No tienes permisos de administrador.")
            return

        usuario = self.ent_nombre.get().strip()
        password = self.ent_pass.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Atención", "El usuario y la contraseña son obligatorios.")
            return

        if self.empleado_seleccionado_id is None:
            try:
                if Usuario.select().where(Usuario.username == usuario).exists():
                    messagebox.showerror("Error", "El nombre de usuario ya existe en el sistema.")
                    return

                password_hasheada = hashear_password(password)
                Usuario.create(username=usuario, password=password_hasheada, rol="cajero")
                messagebox.showinfo("Éxito", f"Usuario '{usuario}' registrado correctamente.")
                self.limpiar_formulario()
                self.actualizar_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
        else:
            try:
                emp = Usuario.get_by_id(self.empleado_seleccionado_id)
                emp.username = usuario
                if password:
                    emp.password = hashear_password(password)
                emp.save()

                messagebox.showinfo("Éxito", "Usuario actualizado correctamente.")
                self.limpiar_formulario()
                self.actualizar_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar:\n{e}")

    def seleccionar_empleado(self, empleado):
        if self.rol_usuario not in ["admin", "administrador"]:
            return

        self.empleado_seleccionado_id = empleado.id
        self.ent_nombre.delete(0, 'end')
        self.ent_nombre.insert(0, empleado.username)
        self.ent_pass.delete(0, 'end')
        self.combo_rol.set(empleado.rol)

        self.btn_guardar.configure(text="Actualizar Empleado", fg_color="#2980B9", hover_color="#1F618D")

    def eliminar_empleado(self):
        if self.rol_usuario not in ["admin", "administrador"]:
            messagebox.showerror("Acceso Denegado", "No tienes permisos de administrador.")
            return

        if self.empleado_seleccionado_id is None:
            messagebox.showwarning("Seleccionar", "Haz clic en un usuario de la lista.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este usuario?"):
            try:
                emp = Usuario.get_by_id(self.empleado_seleccionado_id)
                emp.delete_instance()
                messagebox.showinfo("Eliminado", "El usuario ha sido eliminado.")
                self.limpiar_formulario()
                self.actualizar_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def limpiar_formulario(self):
        self.empleado_seleccionado_id = None
        self.ent_nombre.delete(0, 'end')
        self.ent_pass.delete(0, 'end')
        self.combo_rol.set("cajero")
        self.btn_guardar.configure(text="Guardar Empleado", fg_color=self.colores["acento"], hover_color=self.colores["acento_hover"])

    def actualizar_lista(self):
        for widget in self.lista_empleados.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
        
        try:
            empleados = Usuario.select().where((Usuario.rol != "admin") & (Usuario.rol != "ADMINISTRADOR"))
        except Exception:
            empleados = []

        for emp in empleados:
            frame_item = ctk.CTkFrame(self.lista_empleados, fg_color="#F4F1EA", height=45, corner_radius=6)
            frame_item.pack(fill="x", padx=10, pady=5)
            
            # Formato solicitado: Muestra únicamente "Usuario: [nombre]" sin mencionar roles
            texto_info = f"👤 Usuario: {emp.username}"
            lbl = ctk.CTkLabel(frame_item, text=texto_info, font=("Roboto", 12, "bold"), text_color=self.colores["texto_principal"])
            lbl.pack(side="left", padx=15, pady=10)

            if self.rol_usuario in ["admin", "administrador"]:
                frame_item.bind("<Button-1>", lambda event, e=emp: self.seleccionar_empleado(e))
                lbl.bind("<Button-1>", lambda event, e=emp: self.seleccionar_empleado(e))
import customtkinter as ctk
from tkinter import messagebox
from database_kiosco import Producto

class ProductosFrame(ctk.CTkFrame):
    def __init__(self, parent, colores):
        super().__init__(parent, fg_color="transparent")
        self.colores = colores

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.crear_panel_formulario()
        self.crear_panel_tabla()
        self.cargar_productos()

    def crear_panel_formulario(self):
        form_frame = ctk.CTkFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10, border_width=1, border_color="#E0DCD0")
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        form_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form_frame, text="GESTIÓN DE PRODUCTOS", font=("Roboto", 16, "bold"), text_color=self.colores["texto_principal"]).pack(pady=(20, 15))

        ctk.CTkLabel(form_frame, text="Código de Barras (Opcional):", font=("Roboto", 12, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_codigo = ctk.CTkEntry(form_frame, font=("Roboto", 13), height=35)
        self.entry_codigo.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Nombre del Producto:", font=("Roboto", 12, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_nombre = ctk.CTkEntry(form_frame, font=("Roboto", 13), height=35)
        self.entry_nombre.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Precio de Venta ($):", font=("Roboto", 12, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_precio_venta = ctk.CTkEntry(form_frame, font=("Roboto", 13), height=35)
        self.entry_precio_venta.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Precio de Costo ($):", font=("Roboto", 12, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_precio_costo = ctk.CTkEntry(form_frame, font=("Roboto", 13), height=35)
        self.entry_precio_costo.pack(fill="x", padx=20, pady=(0, 20))

        btn_guardar = ctk.CTkButton(
            form_frame, text="GUARDAR PRODUCTO", font=("Roboto", 13, "bold"), height=40,
            fg_color=self.colores["acento"], hover_color=self.colores["acento_hover"],
            command=self.guardar_producto
        )
        btn_guardar.pack(fill="x", padx=20, pady=(0, 10))

        btn_limpiar = ctk.CTkButton(
            form_frame, text="Limpiar Campos", font=("Roboto", 12), height=35,
            fg_color="#7F8C8D", hover_color="#6C7A89",
            command=self.limpiar_campos
        )
        btn_limpiar.pack(fill="x", padx=20, pady=(0, 20))

    def crear_panel_tabla(self):
        tabla_container = ctk.CTkFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10, border_width=1, border_color="#E0DCD0")
        tabla_container.grid(row=0, column=1, sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tabla_container, text="PRODUCTOS EN INVENTARIO", font=("Roboto", 16, "bold"), text_color=self.colores["texto_principal"]).pack(pady=(20, 15))

        # Encabezado con grid estricto y anchos fijos de columna idénticos
        header = ctk.CTkFrame(tabla_container, fg_color="#EFECE6", height=40, corner_radius=6)
        header.pack(fill="x", padx=20, pady=(0, 5))
        
        header.grid_columnconfigure(0, minsize=140, weight=0) # Código
        header.grid_columnconfigure(1, weight=1)              # Nombre (expansivo)
        header.grid_columnconfigure(2, minsize=110, weight=0) # Precio
        header.grid_columnconfigure(3, minsize=45, weight=0)  # Botón eliminar

        ctk.CTkLabel(header, text="CÓDIGO", font=("Roboto", 12, "bold"), text_color=self.colores["texto_principal"]).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        ctk.CTkLabel(header, text="NOMBRE", font=("Roboto", 12, "bold"), text_color=self.colores["texto_principal"]).grid(row=0, column=1, padx=5, pady=8, sticky="w")
        ctk.CTkLabel(header, text="PRECIO", font=("Roboto", 12, "bold"), text_color=self.colores["texto_principal"]).grid(row=0, column=2, padx=5, pady=8, sticky="w")

        self.tabla_scroll = ctk.CTkScrollableFrame(tabla_container, fg_color="#F9F9F9", corner_radius=6)
        self.tabla_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def cargar_productos(self):
        for widget in self.tabla_scroll.winfo_children():
            widget.destroy()

        try:
            productos = Producto.select()
            for prod in productos:
                fila = ctk.CTkFrame(self.tabla_scroll, fg_color="#FFFFFF", corner_radius=5, border_width=1, border_color="#E0DCD0", height=45)
                fila.pack(fill="x", padx=5, pady=4)
                
                # Sincronización idéntica de anchos de columna con el encabezado
                fila.grid_columnconfigure(0, minsize=140, weight=0)
                fila.grid_columnconfigure(1, weight=1)
                fila.grid_columnconfigure(2, minsize=110, weight=0)
                fila.grid_columnconfigure(3, minsize=45, weight=0)

                codigo_str = prod.codigo_barras if prod.codigo_barras else "Sin Código"
                
                ctk.CTkLabel(fila, text=codigo_str, font=("Roboto", 12), text_color=self.colores["texto_secundario"]).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
                ctk.CTkLabel(fila, text=prod.nombre, font=("Roboto", 12, "bold"), text_color=self.colores["texto_principal"]).grid(row=0, column=1, padx=5, pady=8, sticky="w")
                ctk.CTkLabel(fila, text=f"${prod.precio_venta:.2f}", font=("Roboto", 12, "bold"), text_color="#27AE60").grid(row=0, column=2, padx=5, pady=8, sticky="w")

                btn_eliminar = ctk.CTkButton(
                    fila, text="✕", font=("Roboto", 12, "bold"), width=30, height=30,
                    fg_color="#E74C3C", hover_color="#C0392B",
                    command=lambda p_id=prod.id: self.eliminar_producto(p_id)
                )
                btn_eliminar.grid(row=0, column=3, padx=5, pady=8, sticky="e")
        except Exception as e:
            print("Error al cargar productos:", e)

    def guardar_producto(self):
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        p_venta = self.entry_precio_venta.get().strip()
        p_costo = self.entry_precio_costo.get().strip()

        if not nombre or not p_venta:
            messagebox.showwarning("Campos vacíos", "El nombre y el precio de venta son obligatorios.")
            return

        try:
            precio_v = float(p_venta)
            precio_c = float(p_costo) if p_costo else 0.0
        except ValueError:
            messagebox.showerror("Error de formato", "Los precios deben ser numéricos.")
            return

        if not codigo:
            codigo = self.generar_codigo_automatico()

        try:
            Producto.create(
                codigo_barras=codigo,
                nombre=nombre,
                precio_venta=precio_v,
                precio_costo=precio_c
            )
            messagebox.showinfo("Éxito", f"Producto guardado con código: {codigo}")
            self.limpiar_campos()
            self.cargar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto. Verifique que el código no esté repetido.\nDetalle: {e}")

    def generar_codigo_automatico(self):
        try:
            productos = Producto.select()
            max_num = 0
            for p in productos:
                if p.codigo_barras and p.codigo_barras.isdigit() and len(p.codigo_barras) <= 6:
                    num = int(p.codigo_barras)
                    if num > max_num:
                        max_num = num
            return str(max_num + 1)
        except Exception:
            return "1"

    def limpiar_campos(self):
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_precio_venta.delete(0, "end")
        self.entry_precio_costo.delete(0, "end")
        self.entry_codigo.focus()

    def eliminar_producto(self, prod_id):
        if messagebox.askyesno("Confirmar", "¿Desea eliminar este producto?"):
            try:
                prod = Producto.get_by_id(prod_id)
                prod.delete_instance()
                self.cargar_productos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
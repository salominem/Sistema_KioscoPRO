import customtkinter as ctk
from tkinter import messagebox
from database_kiosco import Producto
import datetime

class ProductosFrame(ctk.CTkFrame):
    def __init__(self, parent, colores):
        super().__init__(parent, fg_color="transparent")
        self.colores = colores
        self.producto_seleccionado_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.crear_formulario()
        self.crear_tabla_inventario()
        self.cargar_productos()

        # Foco automático en el código de barras al entrar
        self.entry_codigo.focus()

    def crear_formulario(self):
        form_frame = ctk.CTkFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10, border_width=1, border_color="#E0DCD0")
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        form_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form_frame, text="GESTIÓN DE PRODUCTOS", font=("Roboto", 16, "bold"), text_color=self.colores["texto_principal"]).pack(pady=(15, 10))

        # Código de barras
        ctk.CTkLabel(form_frame, text="Código de Barras (Opcional):", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(5, 0))
        self.entry_codigo = ctk.CTkEntry(form_frame, font=("Roboto", 12), height=32)
        self.entry_codigo.pack(fill="x", padx=20, pady=(2, 8))

        # Nombre del producto
        ctk.CTkLabel(form_frame, text="Nombre del Producto:", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_nombre = ctk.CTkEntry(form_frame, font=("Roboto", 12), height=32)
        self.entry_nombre.pack(fill="x", padx=20, pady=(2, 8))

        # Precio de Venta
        ctk.CTkLabel(form_frame, text="Precio de Venta ($):", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_venta = ctk.CTkEntry(form_frame, font=("Roboto", 12), height=32)
        self.entry_venta.pack(fill="x", padx=20, pady=(2, 8))

        # Precio de Costo
        ctk.CTkLabel(form_frame, text="Precio de Costo ($):", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_costo = ctk.CTkEntry(form_frame, font=("Roboto", 12), height=32)
        self.entry_costo.pack(fill="x", padx=20, pady=(2, 8))

        # Stock Inicial
        ctk.CTkLabel(form_frame, text="Stock Inicial (Cantidad):", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_stock = ctk.CTkEntry(form_frame, font=("Roboto", 12), height=32)
        self.entry_stock.pack(fill="x", padx=20, pady=(2, 8))
        self.entry_stock.insert(0, "0")

        # Fecha de Vencimiento
        ctk.CTkLabel(form_frame, text="Fecha de Vencimiento (DD/MM/AAAA):", font=("Roboto", 11, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_vencimiento = ctk.CTkEntry(form_frame, placeholder_text="Ej: 31/12/2026", font=("Roboto", 12), height=32)
        self.entry_vencimiento.pack(fill="x", padx=20, pady=(2, 15))

        # Botones de acción
        self.btn_guardar = ctk.CTkButton(
            form_frame, text="GUARDAR PRODUCTO", font=("Roboto", 13, "bold"), height=38,
            fg_color=self.colores["acento"], hover_color=self.colores["acento_hover"],
            command=self.guardar_producto
        )
        self.btn_guardar.pack(fill="x", padx=20, pady=(0, 8))

        # NUEVO BOTÓN: Eliminar Producto Seleccionado
        self.btn_eliminar = ctk.CTkButton(
            form_frame, text="ELIMINAR PRODUCTO", font=("Roboto", 12, "bold"), height=35,
            fg_color="#E74C3C", hover_color="#C0392B", text_color="#FFFFFF",
            command=self.eliminar_producto
        )
        self.btn_eliminar.pack(fill="x", padx=20, pady=(0, 8))

        btn_limpiar = ctk.CTkButton(
            form_frame, text="Limpiar Campos", font=("Roboto", 12), height=32,
            fg_color="#7F8C8D", hover_color="#626D6E", text_color="#FFFFFF",
            command=self.limpiar_formulario
        )
        btn_limpiar.pack(fill="x", padx=20, pady=(0, 20))

    def crear_tabla_inventario(self):
        inv_frame = ctk.CTkFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10, border_width=1, border_color="#E0DCD0")
        inv_frame.grid(row=0, column=1, sticky="nsew", pady=0)
        inv_frame.grid_columnconfigure(0, weight=1)
        inv_frame.grid_rowconfigure(3, weight=1)

        # Título
        ctk.CTkLabel(inv_frame, text="PRODUCTOS EN INVENTARIO", font=("Roboto", 16, "bold"), text_color=self.colores["texto_principal"]).pack(pady=(15, 8))

        # --- BUSCADOR MANUAL EN TIEMPO REAL ---
        self.entry_buscar = ctk.CTkEntry(inv_frame, placeholder_text="🔍 Buscar producto por nombre o código...", font=("Roboto", 12), height=35)
        self.entry_buscar.pack(fill="x", padx=15, pady=(0, 10))
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.cargar_productos())

        # Cabecera de la tabla
        header_tabla = ctk.CTkFrame(inv_frame, fg_color="#EFECE6", height=35, corner_radius=6)
        header_tabla.pack(fill="x", padx=15, pady=(0, 5))
        
        ctk.CTkLabel(header_tabla, text="CÓDIGO / NOMBRE", font=("Roboto", 11, "bold"), text_color=self.colores["texto_principal"]).pack(side="left", padx=15, pady=6)
        ctk.CTkLabel(header_tabla, text="PRECIO", font=("Roboto", 11, "bold"), text_color=self.colores["texto_principal"]).pack(side="right", padx=15, pady=6)
        ctk.CTkLabel(header_tabla, text="STOCK", font=("Roboto", 11, "bold"), text_color=self.colores["texto_principal"]).pack(side="right", padx=10, pady=6)
        ctk.CTkLabel(header_tabla, text="VENCIMIENTO", font=("Roboto", 11, "bold"), text_color=self.colores["texto_principal"]).pack(side="right", padx=15, pady=6)

        # Contenedor desplazable de productos
        self.tabla_scroll = ctk.CTkScrollableFrame(inv_frame, fg_color="#F9F9F9", corner_radius=6)
        self.tabla_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def cargar_productos(self):
        for widget in self.tabla_scroll.winfo_children():
            widget.destroy()

        texto_busqueda = self.entry_buscar.get().strip().lower() if hasattr(self, 'entry_buscar') else ""

        try:
            if texto_busqueda:
                # Filtra si coincide con el nombre o el código de barras
                productos = Producto.select().where(
                    (Producto.nombre.ilike(f"%{texto_busqueda}%")) | 
                    (Producto.codigo_barras.ilike(f"%{texto_busqueda}%"))
                ).order_by(Producto.nombre)
            else:
                productos = Producto.select().order_by(Producto.nombre)
        except Exception:
            productos = []

        for prod in productos:
            fila = ctk.CTkFrame(self.tabla_scroll, fg_color="#FFFFFF", corner_radius=5, border_width=1, border_color="#E0DCD0", height=40)
            fila.pack(fill="x", padx=5, pady=3)
            
            txt_info = f"{prod.codigo_barras or 'S/C'} — {prod.nombre}"
            ctk.CTkLabel(fila, text=txt_info, font=("Roboto", 12), text_color=self.colores["texto_principal"]).pack(side="left", padx=10, pady=8)
            
            ctk.CTkLabel(fila, text=f"${prod.precio_venta:.2f}", font=("Roboto", 12, "bold"), text_color=self.colores["acento"]).pack(side="right", padx=10, pady=8)
            
            color_stock = "#C0392B" if prod.stock <= 5 else "#27AE60"
            ctk.CTkLabel(fila, text=str(prod.stock), font=("Roboto", 12, "bold"), text_color=color_stock).pack(side="right", padx=15, pady=8)

            venc = prod.fecha_vencimiento if prod.fecha_vencimiento else "Sin fecha"
            ctk.CTkLabel(fila, text=venc, font=("Roboto", 11), text_color=self.colores["texto_secundario"]).pack(side="right", padx=15, pady=8)

            fila.bind("<Button-1>", lambda event, p=prod: self.seleccionar_producto(p))
            for child in fila.winfo_children():
                child.bind("<Button-1>", lambda event, p=prod: self.seleccionar_producto(p))

    def seleccionar_producto(self, producto):
        self.producto_seleccionado_id = producto.id
        self.entry_codigo.delete(0, "end")
        if producto.codigo_barras:
            self.entry_codigo.insert(0, producto.codigo_barras)
            
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, producto.nombre)
        
        self.entry_venta.delete(0, "end")
        self.entry_venta.insert(0, str(producto.precio_venta))
        
        self.entry_costo.delete(0, "end")
        if producto.precio_costo:
            self.entry_costo.insert(0, str(producto.precio_costo))
            
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, str(producto.stock))
        
        self.entry_vencimiento.delete(0, "end")
        if producto.fecha_vencimiento:
            self.entry_vencimiento.insert(0, producto.fecha_vencimiento)

        self.btn_guardar.configure(text="ACTUALIZAR PRODUCTO", fg_color="#2980B9", hover_color="#1F618D")

    def guardar_producto(self):
        nombre = self.entry_nombre.get().strip()
        codigo = self.entry_codigo.get().strip()
        vencimiento = self.entry_vencimiento.get().strip()

        if not nombre:
            messagebox.showwarning("Campo requerido", "El nombre del producto es obligatorio.")
            return

        try:
            precio_venta = float(self.entry_venta.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un precio de venta válido.")
            return

        try:
            precio_costo = float(self.entry_costo.get().strip()) if self.entry_costo.get().strip() else 0.0
        except ValueError:
            precio_costo = 0.0

        try:
            stock = int(self.entry_stock.get().strip()) if self.entry_stock.get().strip() else 0
        except ValueError:
            stock = 0

        if self.producto_seleccionado_id is None:
            try:
                Producto.create(
                    codigo_barras=codigo if codigo else None,
                    nombre=nombre,
                    precio_venta=precio_venta,
                    precio_costo=precio_costo,
                    stock=stock,
                    fecha_vencimiento=vencimiento if vencimiento else None
                )
                messagebox.showinfo("Éxito", "Producto guardado correctamente.")
                self.limpiar_formulario()
                self.cargar_productos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el producto. ¿El código de barras ya existe?\nDetalle: {e}")
        else:
            try:
                prod = Producto.get_by_id(self.producto_seleccionado_id)
                prod.codigo_barras = codigo if codigo else None
                prod.nombre = nombre
                prod.precio_venta = precio_venta
                prod.precio_costo = precio_costo
                prod.stock = stock
                prod.fecha_vencimiento = vencimiento if vencimiento else None
                prod.save()

                messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
                self.limpiar_formulario()
                self.cargar_productos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")

    def eliminar_producto(self):
        if self.producto_seleccionado_id is None:
            messagebox.showwarning("Seleccionar Producto", "Haga clic primero en un producto de la tabla de inventario para seleccionarlo y poder eliminarlo.")
            return

        respuesta = messagebox.askyesno(
            "Confirmar Eliminación", 
            "¿Estás seguro de que deseas eliminar este producto del inventario?\nEsta acción lo borrará permanentemente de la base de datos.",
            icon="warning"
        )

        if respuesta:
            try:
                prod = Producto.get_by_id(self.producto_seleccionado_id)
                nombre_prod = prod.nombre
                prod.delete_instance()

                messagebox.showinfo("Eliminado", f"El producto '{nombre_prod}' ha sido eliminado correctamente.")
                self.limpiar_formulario()
                self.cargar_productos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

    def limpiar_formulario(self):
        self.producto_seleccionado_id = None
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_venta.delete(0, "end")
        self.entry_costo.delete(0, "end")
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, "0")
        self.entry_vencimiento.delete(0, "end")
        self.btn_guardar.configure(text="GUARDAR PRODUCTO", fg_color=self.colores["acento"], hover_color=self.colores["acento_hover"])
        self.entry_codigo.focus()
import customtkinter as ctk
from tkinter import messagebox
from database_kiosco import Producto, Venta, DetalleVenta

class VentasFrame(ctk.CTkFrame):
    def __init__(self, parent, colores, username="admin"):
        super().__init__(parent, fg_color="transparent")
        self.colores = colores
        self.username = username

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.carrito = []
        self.indice_seleccionado = None

        self.crear_panel_izquierdo()
        self.crear_panel_derecho()

        # Enfoque inicial y configuración de ATAJOS DE TECLADO GLOBALES
        self.after(100, lambda: self.entry_codigo.focus())
        self.configurar_atajos()

    def configurar_atajos(self):
        # F2 para ir directo al buscador
        self.winfo_toplevel().bind("<F2>", lambda event: self.enfocar_buscador())
        # F4 para cobrar directo
        self.winfo_toplevel().bind("<F4>", lambda event: self.procesar_cobro())
        # Supr (Delete) para eliminar el ítem seleccionado
        self.winfo_toplevel().bind("<Delete>", lambda event: self.eliminar_item_seleccionado())

    def enfocar_buscador(self):
        self.sugerencias_frame.place_forget()
        self.entry_codigo.focus()
        self.entry_codigo.select_range(0, 'end')

    def crear_panel_izquierdo(self):
        self.left_frame = ctk.CTkFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10, border_width=1, border_color="#E0DCD0")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)

        top_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        top_bar.grid_columnconfigure(1, weight=1)

        lbl_codigo = ctk.CTkLabel(top_bar, text="CÓDIGO / PRODUCTO:", font=("Roboto", 12, "bold"), text_color=self.colores["texto_principal"])
        lbl_codigo.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", self.actualizar_sugerencias)

        self.entry_codigo = ctk.CTkEntry(
            top_bar, 
            textvariable=self.busqueda_var,
            placeholder_text="Escribir nombre o pasar lector (F2)...", 
            font=("Roboto", 13), 
            height=35
        )
        self.entry_codigo.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.entry_codigo.bind("<Return>", lambda event: self.procesar_busqueda_o_ingreso())

        btn_buscar = ctk.CTkButton(
            top_bar, text="BUSCAR", font=("Roboto", 12, "bold"), width=90, height=35,
            fg_color=self.colores["acento"], hover_color=self.colores["acento_hover"],
            command=self.procesar_busqueda_o_ingreso
        )
        btn_buscar.grid(row=0, column=2, sticky="e")

        self.sugerencias_frame = ctk.CTkFrame(self.left_frame, fg_color="#FFFFFF", border_width=1, border_color="#3498DB", corner_radius=6)

        header_tabla = ctk.CTkFrame(self.left_frame, fg_color="#EFECE6", height=35, corner_radius=6)
        header_tabla.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 5))
        
        ctk.CTkLabel(header_tabla, text="NOMBRE DEL PRODUCTO / CANTIDAD / PRECIO", font=("Roboto", 12, "bold"), text_color=self.colores["texto_principal"]).pack(side="left", padx=15, pady=6)

        self.tabla_frame = ctk.CTkScrollableFrame(self.left_frame, fg_color="#F9F9F9", corner_radius=6)
        self.tabla_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))

    def crear_panel_derecho(self):
        right_frame = ctk.CTkFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10, border_width=1, border_color="#E0DCD0")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_rowconfigure(2, weight=0)
        right_frame.grid_rowconfigure(3, weight=0)

        total_container = ctk.CTkFrame(right_frame, fg_color="#EFECE6", corner_radius=8)
        total_container.grid(row=1, column=0, sticky="ew", padx=15, pady=(10, 10))

        ctk.CTkLabel(total_container, text="TOTAL A PAGAR", font=("Roboto", 12, "bold"), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=15, pady=(8, 0))
        
        self.lbl_total = ctk.CTkLabel(total_container, text="$ 0.00", font=("Roboto", 24, "bold"), text_color=self.colores["acento"])
        self.lbl_total.pack(anchor="w", padx=15, pady=(0, 10))

        btn_eliminar = ctk.CTkButton(
            right_frame, text="ELIMINAR (Supr)", font=("Roboto", 12, "bold"), height=34,
            fg_color="#E74C3C", hover_color="#C0392B", text_color="#FFFFFF",
            corner_radius=6,
            command=self.eliminar_item_seleccionado
        )
        btn_eliminar.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 8))

        btn_cobrar = ctk.CTkButton(
            right_frame, text="COBRAR (F4)", font=("Roboto", 14, "bold"), height=42,
            fg_color="#27AE60", hover_color="#219653", text_color="#FFFFFF",
            corner_radius=6,
            command=self.procesar_cobro
        )
        btn_cobrar.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))

    def actualizar_sugerencias(self, *args):
        texto = self.busqueda_var.get().strip()
        
        for widget in self.sugerencias_frame.winfo_children():
            widget.destroy()

        if len(texto) < 1:
            self.sugerencias_frame.place_forget()
            return

        texto_lower = texto.lower()
        try:
            todos = list(Producto.select())
            productos_encontrados = [
                p for p in todos 
                if texto_lower in p.nombre.lower() or (p.codigo_barras and texto_lower in p.codigo_barras.lower())
            ][:5]
        except Exception as e:
            print("Error al buscar sugerencias:", e)
            productos_encontrados = []

        if not productos_encontrados:
            self.sugerencias_frame.place_forget()
            return

        for prod in productos_encontrados:
            # Indicamos visualmente en la sugerencia si no hay stock
            aviso_stock = f" (SIN STOCK)" if prod.stock <= 0 else f" — Stock: {prod.stock}"
            btn_sug = ctk.CTkButton(
                self.sugerencias_frame, 
                text=f"{prod.nombre}  —  Precio: ${prod.precio_venta:.2f}{aviso_stock}", 
                font=("Roboto", 12),
                fg_color="transparent", 
                text_color="#C0392B" if prod.stock <= 0 else self.colores["texto_principal"],
                hover_color="#E8F4FD",
                anchor="w",
                command=lambda p=prod: self.seleccionar_producto_sugerido(p)
            )
            btn_sug.pack(fill="x", padx=2, pady=2)

        self.sugerencias_frame.place(x=155, y=56, relwidth=0.62)
        self.sugerencias_frame.lift()

    def seleccionar_producto_sugerido(self, producto):
        self.sugerencias_frame.place_forget()
        for widget in self.sugerencias_frame.winfo_children():
            widget.destroy()
            
        self.busqueda_var.set("")
        self.agregar_producto_al_carrito(producto)

    def procesar_busqueda_o_ingreso(self):
        self.sugerencias_frame.place_forget()
        for widget in self.sugerencias_frame.winfo_children():
            widget.destroy()

        texto = self.busqueda_var.get().strip()
        if not texto:
            return

        texto_lower = texto.lower()

        try:
            producto = Producto.get((Producto.codigo_barras == texto) | (Producto.nombre ** f"%{texto}%"))
            self.agregar_producto_al_carrito(producto)
            return
        except Producto.DoesNotExist:
            pass

        try:
            todos = list(Producto.select())
            coincidencias = [
                p for p in todos 
                if texto_lower in p.nombre.lower() or (p.codigo_barras and texto_lower in p.codigo_barras.lower())
            ]
            if coincidencias:
                self.agregar_producto_al_carrito(coincidencias[0])
                return
        except Exception as e:
            print("Error en procesamiento de búsqueda:", e)

        messagebox.showerror("No encontrado", f"No existe un producto con el código o nombre: {texto}")
        self.busqueda_var.set("")
        self.entry_codigo.focus()

    def agregar_producto_al_carrito(self, producto):
        # --- VALIDACIÓN DE STOCK ---
        if producto.stock <= 0:
            messagebox.showwarning(
                "Sin Stock", 
                f"⚠️ El producto '{producto.nombre}' no tiene stock disponible (Stock: 0)."
            )
            self.busqueda_var.set("")
            self.entry_codigo.focus()
            return
        # ---------------------------

        cantidad = 1
        encontrado = False
        
        for item in self.carrito:
            if item["producto"].id == producto.id:
                nueva_cantidad = item["cantidad"] + cantidad
                # Validar que al sumar más unidades no superemos el stock disponible en inventario
                if nueva_cantidad > producto.stock:
                    messagebox.showwarning(
                        "Stock Insuficiente", 
                        f"Solo hay {producto.stock} unidades disponibles de '{producto.nombre}'."
                    )
                    self.entry_codigo.focus()
                    return

                item["cantidad"] = nueva_cantidad
                item["subtotal"] = producto.precio_venta * nueva_cantidad
                encontrado = True
                break

        if not encontrado:
            subtotal = producto.precio_venta * cantidad
            self.carrito.append({
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal
            })

        self.busqueda_var.set("")
        self.entry_codigo.focus()
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        total_general = 0.0

        for index, item in enumerate(self.carrito):
            prod = item["producto"]
            cant = item["cantidad"]
            sub = item["subtotal"]
            total_general += sub

            if index == self.indice_seleccionado:
                bg_color = "#E8F4FD"
                border_col = "#3498DB"
            else:
                bg_color = "#FFFFFF"
                border_col = "#E0DCD0"

            fila = ctk.CTkFrame(self.tabla_frame, fg_color=bg_color, corner_radius=5, border_width=1, border_color=border_col)
            fila.pack(fill="x", padx=5, pady=4)
            fila.grid_columnconfigure(0, weight=3)
            fila.grid_columnconfigure(1, weight=1)
            fila.grid_columnconfigure(2, weight=1)

            lbl_nombre = ctk.CTkLabel(fila, text=prod.nombre, font=("Roboto", 13), text_color=self.colores["texto_principal"])
            lbl_nombre.grid(row=0, column=0, sticky="w", padx=12, pady=8)

            entry_cant_row = ctk.CTkEntry(fila, font=("Roboto", 12, "bold"), width=55, height=28)
            entry_cant_row.insert(0, str(cant))
            entry_cant_row.grid(row=0, column=1, padx=5, pady=8)
            entry_cant_row.bind("<Return>", lambda event, idx=index, entry=entry_cant_row: self.cambiar_cantidad_desde_tabla(idx, entry))

            lbl_sub = ctk.CTkLabel(fila, text=f"${sub:.2f}", font=("Roboto", 13, "bold"), text_color=self.colores["texto_principal"])
            lbl_sub.grid(row=0, column=2, sticky="e", padx=12, pady=8)

            elementos = [fila, lbl_nombre, lbl_sub]
            for elem in elementos:
                elem.bind("<Button-1>", lambda event, idx=index: self.seleccionar_fila(idx))
                elem.bind("<Enter>", lambda event, f=fila, idx=index: f.configure(fg_color="#E8F4FD") if idx != self.indice_seleccionado else None)
                elem.bind("<Leave>", lambda event, f=fila, idx=index: f.configure(fg_color="#FFFFFF") if idx != self.indice_seleccionado else None)

        self.lbl_total.configure(text=f"$ {total_general:.2f}")

    def seleccionar_fila(self, index):
        self.sugerencias_frame.place_forget()
        self.indice_seleccionado = index
        self.actualizar_tabla()
        self.entry_codigo.focus()

    def cambiar_cantidad_desde_tabla(self, index, entry_widget):
        try:
            nueva_cant = int(entry_widget.get().strip())
            if nueva_cant <= 0:
                messagebox.showwarning("Cantidad inválida", "La cantidad debe ser mayor a 0.")
                self.actualizar_tabla()
                self.entry_codigo.focus()
                return

            prod = self.carrito[index]["producto"]

            # Validar stock disponible al modificar cantidad manualmente en la tabla
            if nueva_cant > prod.stock:
                messagebox.showwarning("Stock Insuficiente", f"Solo hay {prod.stock} unidades disponibles en inventario.")
                self.actualizar_tabla()
                self.entry_codigo.focus()
                return

            self.indice_seleccionado = index
            self.carrito[index]["cantidad"] = nueva_cant
            self.carrito[index]["subtotal"] = prod.precio_venta * nueva_cant
            self.actualizar_tabla()
            self.entry_codigo.focus()

        except ValueError:
            messagebox.showerror("Error de formato", "Ingrese un número entero válido para la cantidad.")
            self.actualizar_tabla()
            self.entry_codigo.focus()

    def eliminar_item_seleccionado(self):
        self.sugerencias_frame.place_forget()

        if not self.carrito:
            messagebox.showinfo("Vacío", "No hay productos en el ticket actual.")
            self.entry_codigo.focus()
            return

        if self.indice_seleccionado is not None and 0 <= self.indice_seleccionado < len(self.carrito):
            self.carrito.pop(self.indice_seleccionado)
            self.indice_seleccionado = None
            self.actualizar_tabla()
        else:
            messagebox.showwarning("Seleccione un producto", "Haga clic sobre el producto en la tabla que desea eliminar.")
        
        self.entry_codigo.focus()

    def procesar_cobro(self):
        self.sugerencias_frame.place_forget()

        if not self.carrito:
            messagebox.showwarning("Ticket Vacío", "Agregue productos antes de cobrar.")
            self.entry_codigo.focus()
            return

        total_venta = sum(item["subtotal"] for item in self.carrito)

        modal_cobro = ctk.CTkToplevel(self)
        modal_cobro.title("Universum - Cobrar")
        modal_cobro.geometry("360x420")
        modal_cobro.resizable(False, False)
        modal_cobro.configure(fg_color=self.colores["fondo_card"])
        modal_cobro.grab_set()

        modal_cobro.update_idletasks()
        w = modal_cobro.winfo_width()
        h = modal_cobro.winfo_height()
        x = (modal_cobro.winfo_screenwidth() // 2) - (w // 2)
        y = (modal_cobro.winfo_screenheight() // 2) - (h // 2)
        modal_cobro.geometry(f"{w}x{h}+{x}+{y}")

        ctk.CTkLabel(modal_cobro, text="FINALIZAR VENTA", font=("Roboto", 18, "bold"), text_color=self.colores["texto_principal"]).pack(pady=(25, 10))
        
        lbl_total_cobro = ctk.CTkLabel(modal_cobro, text=f"Total a Pagar: ${total_venta:.2f}", font=("Roboto", 15, "bold"), text_color=self.colores["acento"])
        lbl_total_cobro.pack(pady=5)

        ctk.CTkLabel(modal_cobro, text="Efectivo Recibido:", font=("Roboto", 13), text_color=self.colores["texto_secundario"]).pack(anchor="w", padx=30, pady=(15, 5))
        
        entry_efectivo = ctk.CTkEntry(modal_cobro, font=("Roboto", 15, "bold"), width=300, height=40)
        entry_efectivo.pack(padx=30, pady=5)
        entry_efectivo.focus()

        lbl_vuelto = ctk.CTkLabel(modal_cobro, text="Vuelto: $0.00", font=("Roboto", 16, "bold"), text_color="#27AE60")
        lbl_vuelto.pack(pady=15)

        def calcular_vuelto(event=None):
            try:
                efectivo = float(entry_efectivo.get().strip())
                vuelto = efectivo - total_venta
                if vuelto >= 0:
                    lbl_vuelto.configure(text=f"Vuelto: ${vuelto:.2f}", text_color="#27AE60")
                else:
                    lbl_vuelto.configure(text=f"Falta dinero: ${abs(vuelto):.2f}", text_color="#C0392B")
            except ValueError:
                lbl_vuelto.configure(text="Vuelto: $0.00", text_color="#27AE60")

        entry_efectivo.bind("<KeyRelease>", calcular_vuelto)

        def confirmar_venta_definitiva():
            try:
                efectivo = float(entry_efectivo.get().strip())
                if efectivo < total_venta:
                    messagebox.showwarning("Dinero Insuficiente", "El efectivo recibido es menor al total de la venta.", parent=modal_cobro)
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto en efectivo válido.", parent=modal_cobro)
                return

            nueva_venta = Venta.create(total_venta=total_venta, cajero=self.username)

            for item in self.carrito:
                prod = item["producto"]
                cant = item["cantidad"]
                sub = item["subtotal"]

                # Descontar stock en la base de datos
                prod.stock -= cant
                prod.save()

                DetalleVenta.create(
                    venta=nueva_venta,
                    nombre_producto=prod.nombre,
                    cantidad=cant,
                    precio_unitario=prod.precio_venta,
                    subtotal=sub
                )

            messagebox.showinfo("¡Éxito!", f"Venta cobrada correctamente.\nVuelto a entregar: ${(efectivo - total_venta):.2f}", parent=modal_cobro)
            
            self.carrito.clear()
            self.indice_seleccionado = None
            self.actualizar_tabla()
            modal_cobro.destroy()
            self.entry_codigo.focus()

        btn_confirmar = ctk.CTkButton(
            modal_cobro, text="CONFIRMAR PAGO", font=("Roboto", 14, "bold"), width=300, height=45,
            fg_color="#27AE60", hover_color="#219653", text_color="#FFFFFF",
            command=confirmar_venta_definitiva
        )
        btn_confirmar.pack(pady=(10, 25))

        modal_cobro.bind("<Return>", lambda event: confirmar_venta_definitiva())
import customtkinter as ctk
from database_kiosco import Venta, Gasto
import datetime
from tkcalendar import DateEntry
from collections import defaultdict

class ReportesFrame(ctk.CTkFrame):
    def __init__(self, parent, colores):
        super().__init__(parent, fg_color="transparent")
        self.colores = colores
        self.fecha_seleccionada = datetime.date.today()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.crear_panel_filtros()
        
        self.tabla_ventas = ctk.CTkScrollableFrame(self, fg_color=self.colores["fondo_card"], corner_radius=10)
        self.tabla_ventas.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.cargar_datos_turno("hoy")

    def crear_panel_filtros(self):
        filtro_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtro_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))

        # Selector de Fecha en Español
        self.calendario = DateEntry(
            filtro_frame, width=12, background='#D35400', foreground='white', 
            borderwidth=2, locale='es_ES', date_pattern='dd/mm/yyyy'
        )
        self.calendario.pack(side="left", padx=5)
        
        btn_buscar = ctk.CTkButton(
            filtro_frame, text="BUSCAR", width=80, font=("Roboto", 11, "bold"),
            fg_color="#D35400", hover_color="#BA4A00", command=self.buscar_fecha
        )
        btn_buscar.pack(side="left", padx=5)

        # Botón para registrar gastos
        btn_gasto = ctk.CTkButton(
            filtro_frame, text="GASTOS", width=90, font=("Roboto", 11, "bold"),
            fg_color="#C0392B", hover_color="#962D22", command=self.abrir_ventana_gasto
        )
        btn_gasto.pack(side="left", padx=15)

        # Botones de Turnos
        turnos = [
            ("Noche", "noche"), 
            ("Tarde", "tarde"), 
            ("Mañana", "manana"), 
            ("Todo el Día", "hoy")
        ]
        
        for texto, comando in turnos:
            ctk.CTkButton(
                filtro_frame, text=texto, width=95, font=("Roboto", 11, "bold"),
                fg_color="#D35400", hover_color="#BA4A00", 
                command=lambda c=comando: self.cargar_datos_turno(c)
            ).pack(side="right", padx=3)

    def buscar_fecha(self):
        self.fecha_seleccionada = self.calendario.get_date()
        self.cargar_datos_turno("hoy")

    def abrir_ventana_gasto(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Registrar Nuevo Gasto")
        
        ancho, alto = 350, 250
        
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        ventana.grab_set()

        ctk.CTkLabel(ventana, text="REGISTRAR EGRESO DE CAJA", font=("Roboto", 14, "bold")).pack(pady=(20, 10))
        
        ent_desc = ctk.CTkEntry(ventana, placeholder_text="Descripción (ej: Panadero, Luz)", width=280, height=35)
        ent_desc.pack(pady=5)
        
        ent_monto = ctk.CTkEntry(ventana, placeholder_text="Monto ($)", width=280, height=35)
        ent_monto.pack(pady=5)
        
        def guardar_gasto():
            try:
                monto_val = float(ent_monto.get())
                desc_val = ent_desc.get().strip()
                if not desc_val:
                    return
                Gasto.create(descripcion=desc_val, monto=monto_val)
                ventana.destroy()
                self.cargar_datos_turno("hoy")
            except ValueError:
                pass

        ctk.CTkButton(
            ventana, text="GUARDAR GASTO", width=280, height=35,
            fg_color="#C0392B", hover_color="#962D22", command=guardar_gasto
        ).pack(pady=15)

    def filtrar_por_horario(self, hora, tipo_turno):
        if tipo_turno == "manana" and (8 <= hora < 16): return True
        if tipo_turno == "tarde" and (16 <= hora < 23): return True
        if tipo_turno == "noche" and (hora >= 23 or hora < 8): return True
        if tipo_turno == "hoy": return True
        return False

    def cargar_datos_turno(self, tipo_turno):
        for widget in self.tabla_ventas.winfo_children(): 
            widget.destroy()

        ventas_dia = Venta.select().where(
            Venta.fecha_hora.year == self.fecha_seleccionada.year, 
            Venta.fecha_hora.month == self.fecha_seleccionada.month, 
            Venta.fecha_hora.day == self.fecha_seleccionada.day
        )
        
        ventas_filtradas = [v for v in ventas_dia if self.filtrar_por_horario(v.fecha_hora.hour, tipo_turno)]
        total_ventas = sum(v.total_venta for v in ventas_filtradas)

        gastos_dia = Gasto.select().where(
            Gasto.fecha_hora.year == self.fecha_seleccionada.year, 
            Gasto.fecha_hora.month == self.fecha_seleccionada.month, 
            Gasto.fecha_hora.day == self.fecha_seleccionada.day
        )
        
        gastos_filtrados = [g for g in gastos_dia if self.filtrar_por_horario(g.fecha_hora.hour, tipo_turno)]
        total_gastos = sum(g.monto for g in gastos_filtrados)

        dinero_en_caja = total_ventas - total_gastos

        # --- AGRUPAR VENTAS POR CADA CAJERO ---
        ventas_por_cajero = defaultdict(float)
        for v in ventas_filtradas:
            cajero_nombre = getattr(v, 'cajero', 'admin')
            ventas_por_cajero[cajero_nombre.capitalize()] += v.total_venta

        nombres_turnos = {"hoy": "TODOS LOS TURNOS", "manana": "TURNO MAÑANA", "tarde": "TURNO TARDE", "noche": "TURNO NOCHE"}
        
        ctk.CTkLabel(self.tabla_ventas, text=f"--- REPORTE: {self.fecha_seleccionada.strftime('%d/%m/%Y')} ({nombres_turnos[tipo_turno]}) ---", font=("Roboto", 15, "bold"), text_color=self.colores["texto_secundario"]).pack(pady=(10, 5))

        resumen_frame = ctk.CTkFrame(self.tabla_ventas, fg_color="#F2F3F4", corner_radius=8)
        resumen_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(resumen_frame, text=f"Total Vendido (Ingresos): ${total_ventas:.2f}", font=("Roboto", 13, "bold"), text_color="#27AE60").pack(anchor="w", padx=15, pady=(8, 2))
        ctk.CTkLabel(resumen_frame, text=f"Total Gastos (Egresos): ${total_gastos:.2f}", font=("Roboto", 13, "bold"), text_color="#C0392B").pack(anchor="w", padx=15, pady=2)
        ctk.CTkFrame(resumen_frame, height=2, fg_color="#BDC3C7").pack(fill="x", padx=15, pady=5)
        
        # --- DESGLOSE POR CAJERO DENTRO DEL RESUMEN ---
        ctk.CTkLabel(resumen_frame, text="Desglose de Ventas por Cajero:", font=("Roboto", 12, "bold"), text_color="#2C3E50").pack(anchor="w", padx=15, pady=(2, 2))
        
        if ventas_por_cajero:
            for cajero, monto in ventas_por_cajero.items():
                ctk.CTkLabel(resumen_frame, text=f"   • {cajero}: ${monto:.2f}", font=("Roboto", 12), text_color="#34495E").pack(anchor="w", padx=20, pady=1)
        else:
            ctk.CTkLabel(resumen_frame, text="   • Sin ventas registradas", font=("Roboto", 11, "italic"), text_color="#7F8C8D").pack(anchor="w", padx=20, pady=1)

        ctk.CTkFrame(resumen_frame, height=2, fg_color="#BDC3C7").pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(resumen_frame, text=f"DINERO REAL EN CAJA: ${dinero_en_caja:.2f}", font=("Roboto", 17, "bold"), text_color="#D35400").pack(anchor="w", padx=15, pady=(2, 8))

        # --- EGRESOS / GASTOS ---
        ctk.CTkLabel(self.tabla_ventas, text="--- EGRESOS / GASTOS ---", font=("Roboto", 13, "bold"), text_color="#C0392B").pack(pady=(15, 5))
        
        if gastos_filtrados:
            for g in gastos_filtrados:
                txt_gasto = f"🕒 {g.fecha_hora.strftime('%H:%M:%S')} | {g.descripcion} (-${g.monto:.2f})"
                ctk.CTkLabel(self.tabla_ventas, text=txt_gasto, font=("Roboto", 12), fg_color="#FADBD8", text_color="#78281F", corner_radius=5, pady=6).pack(fill="x", padx=10, pady=2)
        else:
            ctk.CTkLabel(self.tabla_ventas, text="No hay gastos registrados en este turno.", font=("Roboto", 12), text_color=self.colores["texto_secundario"]).pack(pady=5)

        # --- VENTAS REALIZADAS ---
        ctk.CTkLabel(self.tabla_ventas, text="--- VENTAS REALIZADAS ---", font=("Roboto", 13, "bold"), text_color="#27AE60").pack(pady=(15, 5))

        if ventas_filtradas:
            for venta in ventas_filtradas:
                cajero = getattr(venta, 'cajero', 'admin')
                texto = f"Venta #{venta.id} | 🕒 {venta.fecha_hora.strftime('%H:%M:%S')} | Cajero: {cajero.capitalize()} | +${venta.total_venta:.2f}"
                ctk.CTkLabel(self.tabla_ventas, text=texto, font=("Roboto", 12), fg_color="#EAFAF1", text_color="#145A32", corner_radius=5, pady=6).pack(fill="x", padx=10, pady=2)
        else:
            ctk.CTkLabel(self.tabla_ventas, text="No hay ventas registradas en este turno.", font=("Roboto", 12), text_color=self.colores["texto_secundario"]).pack(pady=5)
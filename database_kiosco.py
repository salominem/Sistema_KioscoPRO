from peewee import *
import datetime
import hashlib

db = SqliteDatabase('kiosco.db')

class BaseModel(Model):
    class Meta:
        database = db

class Usuario(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    rol = CharField(default="cajero")

class Producto(BaseModel):
    codigo_barras = CharField(unique=True, null=True)
    nombre = CharField()
    precio_venta = FloatField()
    precio_costo = FloatField(null=True)

class Venta(BaseModel):
    fecha_hora = DateTimeField(default=datetime.datetime.now)
    total_venta = FloatField()
    cajero = CharField(default="admin")

class DetalleVenta(BaseModel):
    venta = ForeignKeyField(Venta, backref='detalles')
    nombre_producto = CharField()
    cantidad = IntegerField()
    precio_unitario = FloatField()
    subtotal = FloatField()

class Gasto(BaseModel):
    fecha_hora = DateTimeField(default=datetime.datetime.now)
    descripcion = CharField()
    monto = FloatField()
    cajero = CharField(default="admin")

def hashear_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def inicializar_bd():
    db.connect(reuse_if_open=True)
    db.create_tables([Usuario, Producto, Venta, DetalleVenta, Gasto], safe=True)
    
    if not Usuario.select().exists():
        Usuario.create(
            username="admin",
            password=hashear_password("admin123"),
            rol="admin"
        )
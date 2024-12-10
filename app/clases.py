from datetime import datetime
from db_extensiones import db

# Modelo único para usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Tabla única para todos los usuarios
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), nullable=False)
    apellido = db.Column(db.String(45), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)  # Contraseña hasheada
    dni = db.Column(db.String(12), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # Puede ser 'cliente', 'empleado', 'administrador'

    # Relación con reservas (solo para clientes)
    reservas = db.relationship('Reserva', backref='usuario_reserva', lazy=True, foreign_keys="Reserva.cliente_id")

# Modelo de habitaciones
class Habitacion(db.Model):
    __tablename__ = 'habitaciones'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), default='disponible')
    precio = db.Column(db.Numeric(10, 2), nullable=False)  # Precio por día

    # Relación con reservas
    reservas = db.relationship('Reserva', backref='habitacion', lazy=True)

# Modelo de reservas
class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Usuario que realiza la reserva
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'), nullable=False)  # Habitación reservada
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    fecha_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='activa')  # Puede ser 'activa', 'cancelada', 'finalizada'
    metodo_pago = db.Column(db.String(20), default='efectivo', nullable=False)  
    paypal_payment_id = db.Column(db.String(255), nullable=True)

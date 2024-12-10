from flask import session
from clases import Usuario
from clases import Usuario, Habitacion, Reserva
from db_extensiones import db
from functools import wraps
from flask import redirect, url_for, flash, session,flash,current_app
from flask_mail import Message
import logging
from clases import Reserva
from sqlalchemy import func
from clases import Reserva, Habitacion, db
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime

logging.basicConfig(level=logging.INFO, filename='hotel_app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

def obtener_usuario_actual():
    """
    Devuelve el usuario actual basado en el ID almacenado en la sesión.
    """
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return None
    return Usuario.query.get(usuario_id)

def obtener_habitaciones_disponibles(fecha_inicio, fecha_fin):
    """
    Devuelve una lista de habitaciones disponibles en el rango de fechas especificado.
    """
    habitaciones = Habitacion.query.all()
    habitaciones_disponibles = []

    for habitacion in habitaciones:
        if verificar_disponibilidad_habitacion(habitacion.id, fecha_inicio, fecha_fin):
            habitaciones_disponibles.append(habitacion)

    return habitaciones_disponibles

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario = obtener_usuario_actual()
        if not usuario or (usuario.rol not in ['empleado', 'administrador']):
            flash("Acceso denegado. Esta sección es solo para administradores y empleados.", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario = obtener_usuario_actual()
        if not usuario or usuario.rol not in ['administrador', 'empleado']:
            flash("Acceso denegado. Esta sección es solo para administradores y empleados.", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def cancelar_reserva(reserva_id):
    try:
        # Usar Session.get() en lugar de Query.get()
        reserva = db.session.get(Reserva, reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada")
        
        # Cancelar la reserva y actualizar la habitación
        habitacion = reserva.habitacion
        reserva.estado = 'cancelada'
        habitacion.estado = 'disponible'
        
        # Alternativamente, puedes eliminar la reserva:
        # db.session.delete(reserva)
        db.session.commit()
    except ValueError as ve:
        flash(f"Error al cancelar la reserva: {str(ve)}", "danger")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inesperado al cancelar reserva: {str(e)}")
        flash(f"Error inesperado: {str(e)}", "danger")

def verificar_disponibilidad_habitacion(habitacion_id, fecha_inicio, fecha_fin):
    """
    Verifica si una habitación está disponible en el rango de fechas proporcionado.
    Ignora las reservas canceladas.
    """
    reservas = Reserva.query.filter_by(habitacion_id=habitacion_id).filter(Reserva.estado != 'cancelada').all()
    for reserva in reservas:
        if not (fecha_fin <= reserva.fecha_inicio or fecha_inicio >= reserva.fecha_fin):
            return False
    return True

def ingresos_diarios():
    # Obtener los ingresos de cada reserva por fecha
    ingresos_diarios_data = db.session.query(
        func.date_format(Reserva.fecha_reserva, '%Y-%m').label('fecha'),
        func.sum(Habitacion.precio).label('ingresos')
    ).join(Habitacion, Reserva.habitacion_id == Habitacion.id) \
    .group_by(func.date_format(Reserva.fecha_reserva, '%Y-%m')) \
    .with_labels() \
    .all()
    
    # Acceder a los resultados como diccionarios
    ingresos_formateados = [{'fecha': ingreso.fecha, 'ingresos': ingreso.ingresos} for ingreso in ingresos_diarios_data]
    
    return ingresos_formateados

def ingresos_mensuales():
    # Obtener los ingresos por mes
    ingresos_mensuales_data = db.session.query(
        func.date_format(Reserva.fecha_reserva, '%Y-%m').label('mes'),
        func.sum(Habitacion.precio).label('ingresos')
    ).join(Habitacion, Reserva.habitacion_id == Habitacion.id) \
    .group_by(func.date_format(Reserva.fecha_reserva, '%Y-%m')) \
    .all()

    # Formatear el resultado para acceder como diccionario
    ingresos_formateados = [{'mes': ingreso[0], 'ingresos': ingreso[1]} for ingreso in ingresos_mensuales_data]
    
    return ingresos_formateados

def ingresos_por_metodo_pago():
    # Obtener los ingresos por método de pago
    ingresos_data = db.session.query(
        Reserva.metodo_pago,
        func.sum(Habitacion.precio).label('ingresos')
    ).join(Habitacion, Reserva.habitacion_id == Habitacion.id) \
     .group_by(Reserva.metodo_pago) \
     .all()

    # Formatear el resultado para acceder como diccionario
    ingresos_formateados = [{'metodo_pago': ingreso[0], 'ingresos': ingreso[1]} for ingreso in ingresos_data]
    
    return ingresos_formateados

def crear_grafico(x, y, titulo, xlabel, ylabel, color):
    plt.figure(figsize=(10, 6))
    plt.bar(x, y, color=color)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Rotar etiquetas del eje X
    plt.xticks(rotation=45, ha="right")

    # Ajustar espaciamiento para evitar superposición
    plt.tight_layout()

    # Guardar el gráfico como imagen en base64
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    base64_img = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return base64_img


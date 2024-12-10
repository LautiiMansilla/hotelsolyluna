from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response,current_app
from db_extensiones import db
from clases import Usuario, Habitacion, Reserva
from werkzeug.security import generate_password_hash, check_password_hash
from funciones import obtener_usuario_actual, verificar_disponibilidad_habitacion, admin_required, cancelar_reserva, admin_or_employee_required, ingresos_diarios,ingresos_mensuales,ingresos_por_metodo_pago,crear_grafico
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import io
import logging
import csv
import paypalrestsdk
import matplotlib.pyplot as plt
import base64
from matplotlib.ticker import MaxNLocator
import re
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'S3cr3tK3yMuyL4rg4YS3gur4'
s = URLSafeTimedSerializer(app.secret_key)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:roote@localhost/hotel_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
db.init_app(app)
hoy = datetime.now().strftime('%Y-%m-%d')  # Obtiene la fecha actual en formato 'YYYY-MM-DD'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hotelsolylunaok@gmail.com'
app.config['MAIL_PASSWORD'] = 'oepa qzuj uogg aalv'
app.config['MAIL_DEFAULT_SENDER'] = 'hotelsolylunaok@gmail.com'

mail = Mail(app)
logging.basicConfig(level=logging.INFO, filename='hotel_app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

paypalrestsdk.configure({
    "mode": "sandbox",  # Cambiar a "live" en producción
    "client_id": "hasjkajasjkas",
    "client_secret": "ejemplo"
})

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']
        usuario = Usuario.query.filter_by(email=email).first()
        
        # Verificamos si el usuario existe y si la contraseña es correcta
        if usuario and check_password_hash(usuario.contrasena, contrasena):
            session['usuario_id'] = usuario.id  # Guardamos el ID del usuario en la sesión
            flash(f"¡Bienvenido, {usuario.nombre}!", "success")
            return redirect(url_for('home'))  # Redirige siempre a la página principal (home)
        else:
            flash("Correo electrónico o contraseña incorrectos", "danger")  # Mensaje de error

    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Recuperar datos del formulario
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        email = request.form.get('email')
        dni = request.form.get('dni')
        contrasena = request.form.get('contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        rol = 'cliente'  # Por defecto, el rol es cliente

        # Validar que no haya usuarios con el mismo DNI o correo electrónico
        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe un usuario registrado con este correo electrónico.", "danger")
            return redirect(url_for('register'))

        if Usuario.query.filter_by(dni=dni).first():
            flash("Ya existe un usuario registrado con este DNI.", "danger")
            return redirect(url_for('register'))

        # Validar que las contraseñas coincidan
        if contrasena != confirmar_contrasena:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for('register'))

        # Validar la contraseña (mínimo 8 caracteres, máximo 20, al menos una mayúscula y un número)
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[_\-/\*@])[A-Za-z\d_\-/\*]{8,20}$', contrasena):
            flash("La contraseña no es válida. Debe tener entre 8 y 20 caracteres, al menos una mayúscula, un número y un carácter especial (_-/*@).", "danger")
            return redirect(url_for('register'))

        # Generar un hash seguro para la contraseña
        hashed_password = generate_password_hash(contrasena, method='pbkdf2:sha256')

        # Crear instancia del nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            email=email,
            contrasena=hashed_password,
            dni=dni,
            rol=rol
        )

        try:
            # Guardar en la base de datos
            db.session.add(nuevo_usuario)
            db.session.commit()

            # Enviar correo de bienvenida
            mensaje = Message(
                "¡Bienvenido a Hotel Sol y Luna!",
                recipients=[email],  # Correo del usuario
                body=f"""
Hola {nombre},

Gracias por registrarte en Hotel Sol y Luna. Estamos encantados de que te unas a nuestra familia.
Ahora puedes realizar reservas y disfrutar de nuestros servicios.

¡Te esperamos pronto!

Atentamente,
Hotel Sol y Luna
"""
            )
            mail.send(mensaje)

            # Mostrar un mensaje de éxito
            flash("Registro exitoso. ¡Bienvenido! Por favor, haz clic en el botón para iniciar sesión.", "success")
            return render_template('registro.html', mostrar_boton_login=True)  # Renderiza la misma página con el botón para iniciar sesión
        except Exception as e:
            # Rollback en caso de error
            db.session.rollback()
            flash(f"Error al registrar usuario: {str(e)}", "danger")
            return redirect(url_for('register'))
    return render_template('registro.html', hoy=hoy)

@app.context_processor
def inject_usuario():
    if 'usuario_id' in session:
        usuario = db.session.get(Usuario, session['usuario_id'])
        return dict(usuario=usuario)
    return dict(usuario=None)

@app.route('/home')
def home():
    usuario = obtener_usuario_actual()  # Función que obtiene el usuario actual desde la sesión
    if usuario:
        return render_template('home.html', usuario=usuario)
    else:
        flash("Por favor, inicia sesión para acceder a esta página", "warning")
        return redirect(url_for('login'))
    
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            # Generar un token para el enlace
            token = s.dumps(email, salt='reset-password')

            # Crear el enlace
            reset_url = url_for('reset_with_token', token=token, _external=True)

            # Enviar correo con el enlace
            mensaje = Message(
                "Restablecimiento de contraseña - Hotel Sol y Luna",
                recipients=[email],
                body=f"""
Hola,

Recibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:

{reset_url}

Si no solicitaste este cambio, simplemente ignora este correo.

Atentamente,
Hotel Sol y Luna
"""
            )
            mail.send(mensaje)

            # Mensaje flash con enlace a iniciar sesión
            flash("Se ha enviado un correo con las instrucciones para restablecer tu contraseña. Revisa tu casilla de correo.", "info")
            flash("<a href='/login' class='btn btn-primary mt-3'>Iniciar Sesión</a>", "button")  # Botón como flash
            return render_template('reset_password.html')  # Mantiene la misma página con los flashes
        else:
            flash("El correo ingresado no está registrado.", "warning")
    return render_template('reset_password.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        # Verificar el token
        email = s.loads(token, salt='reset-password', max_age=3600)  # Expira en 1 hora
    except SignatureExpired:
        flash("El enlace ha expirado. Por favor, solicita otro restablecimiento.", "danger")
        return redirect(url_for('reset_password'))
    except BadSignature:
        flash("El enlace es inválido. Por favor, intenta nuevamente.", "danger")
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        contrasena = request.form.get('contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')

        if contrasena != confirmar_contrasena:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for('reset_with_token', token=token))

        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[_\-/\*@])[A-Za-z\d_\-/\*@]{8,20}$', contrasena):
            flash("La nueva contraseña no es válida. Debe tener entre 8 y 20 caracteres, al menos una mayúscula, un número y un carácter especial (_-/*@).", "danger")
            return redirect(url_for('reset_with_token', token=token))

        # Validar y actualizar la contraseña
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            hashed_password = generate_password_hash(contrasena, method='pbkdf2:sha256')
            usuario.contrasena = hashed_password
            db.session.commit()

            # Mensaje flash confirmando el cambio exitoso
            flash("Tu contraseña ha sido actualizada correctamente.", "success")
            flash("<a href='/login' class='btn btn-primary mt-3'>Haz clic aquí para iniciar sesión</a>", "button")  # Botón como flash
            return render_template('set_new_password.html')  # Mantiene la misma página con los flashes

    return render_template('set_new_password.html', token=token)
    
@app.route('/profile', methods=['GET'])
def profile():
    usuario_id = session.get('usuario_id')  # Usa .get para evitar KeyError
    if not usuario_id:
        flash("Debes iniciar sesión para ver tu perfil.", "warning")
        return redirect(url_for('login'))

    # Obtener el usuario actual
    usuario = db.session.get(Usuario, usuario_id)

    # Obtener todas las reservas del usuario
    reservas = Reserva.query.filter_by(cliente_id=usuario_id).all()

    # Calcular días y precio total para cada reserva
    reservas_modificadas = []
    for reserva in reservas:
        dias = (reserva.fecha_fin - reserva.fecha_inicio).days
        precio_total = dias * reserva.habitacion.precio
        reservas_modificadas.append({
            'habitacion': reserva.habitacion,
            'fecha_inicio': reserva.fecha_inicio,
            'fecha_fin': reserva.fecha_fin,
            'dias': dias,
            'precio_total': precio_total,
            'estado': reserva.estado
        })

    return render_template('profile.html', usuario=usuario, reservas=reservas_modificadas)

@app.route('/reserva', methods=['GET', 'POST'])
def reserva():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para realizar una reserva.", "warning")
        return redirect(url_for('login'))

    # Variables de filtro de fechas
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    try:
        habitaciones = Habitacion.query.all()  # Obtiene todas las habitaciones inicialmente

        # Si se proporcionan fechas, filtra las habitaciones disponibles
        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

            habitaciones_disponibles = []
            for habitacion in habitaciones:
                if verificar_disponibilidad_habitacion(habitacion.id, fecha_inicio_dt, fecha_fin_dt):
                    habitaciones_disponibles.append(habitacion)

            habitaciones = habitaciones_disponibles

        # Renderiza la página de reserva con las habitaciones filtradas
        return render_template(
            'reserva.html',
            habitaciones=habitaciones,
            hoy=datetime.now().strftime('%Y-%m-%d'),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

    except Exception as e:
        # Captura errores y muestra un mensaje apropiado
        flash(f"Error al cargar la página de reservas: {str(e)}", "danger")
        return redirect(url_for('home'))

@app.route('/procesar_reserva', methods=['POST'])
def procesar_reserva():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para realizar una reserva.", "warning")
        return redirect(url_for('login'))

    try:
        # Obtener datos del formulario
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        habitacion_id = request.form['habitacion']
        cliente_id = session['usuario_id']

        # Convertir fechas a objetos datetime
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

        # Validar si la fecha de fin es igual o menor que la fecha de inicio
        if fecha_inicio_dt > fecha_fin_dt:
            flash("La fecha de fin no puede ser anterior a la fecha de inicio.", "danger")
            return redirect(url_for('reserva'))
        elif fecha_inicio_dt == fecha_fin_dt:
            flash("La reserva debe durar al menos un día completo.", "danger")
            return redirect(url_for('reserva'))

        # Verificar si la habitación está disponible en el rango de fechas
        if not verificar_disponibilidad_habitacion(habitacion_id, fecha_inicio_dt, fecha_fin_dt):
            flash("La habitación seleccionada no está disponible en esas fechas.", "danger")
            return redirect(url_for('reserva'))

        # Calcular duración y precio total
        dias = (fecha_fin_dt - fecha_inicio_dt).days
        habitacion = db.session.get(Habitacion, habitacion_id)
        precio_total = dias * habitacion.precio

        # Crear la reserva
        nueva_reserva = Reserva(
            cliente_id=cliente_id,
            habitacion_id=habitacion_id,
            fecha_inicio=fecha_inicio_dt,
            fecha_fin=fecha_fin_dt,
            estado='activa'
        )

        # Cambiar el estado de la habitación a 'reservada'
        habitacion.estado = 'reservada'

        # Guardar cambios en la base de datos
        db.session.add(nueva_reserva)
        db.session.commit()

        # Enviar correo de confirmación
        try:
            cliente = Usuario.query.get(cliente_id)
            mensaje = Message(
                "Confirmación de Reserva - Hotel Sol y Luna",
                recipients=[cliente.email],
                body=f"""
                Hola {cliente.nombre},

                Tu reserva ha sido realizada con éxito. Aquí tienes los detalles:

                - Habitación: {habitacion.tipo}
                - Capacidad: {habitacion.capacidad} personas
                - Precio por noche: ${habitacion.precio:.2f}
                - Fecha de inicio: {fecha_inicio}
                - Fecha de fin: {fecha_fin}
                - Duración: {dias} días
                - Precio total: ${precio_total:.2f}

                Gracias por elegir Hotel Sol y Luna. ¡Te esperamos pronto!
                """
            )
            mail.send(mensaje)
            if fecha_inicio and fecha_fin:
                habitaciones_disponibles = []
                for habitacion in habitaciones:
                    if verificar_disponibilidad_habitacion(habitacion.id, fecha_inicio_dt, fecha_fin_dt):
                        # Calcula el precio total según la duración
                        dias = (fecha_fin_dt - fecha_inicio_dt).days
                        habitacion.precio_total = dias * habitacion.precio  # Agrega un atributo dinámico
                        habitaciones_disponibles.append(habitacion)

                habitaciones = habitaciones_disponibles

            return render_template(
                'reserva.html',
                habitaciones=habitaciones,
                hoy=datetime.now().strftime('%Y-%m-%d'),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin)
        except Exception as e:
            logging.error(f"Error al enviar correo: {e}")
        return redirect(url_for('confirmacion_reserva', reserva_id=nueva_reserva.id))

    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        flash(f"Error al realizar la reserva: {str(e)}", "danger")
        return redirect(url_for('reserva'))

@app.route('/pagar_con_paypal', methods=['POST'])
def pagar_con_paypal():
    try:
        # Obtener datos de la reserva
        reserva_id = request.form['reserva_id']
        reserva = Reserva.query.get(reserva_id)
        if not reserva:
            flash("No se encontró la reserva.", "danger")
            return redirect(url_for('reserva'))

        # Crear un pago en PayPal
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": url_for('confirmacion_pago', reserva_id=reserva.id, _external=True),
                "cancel_url": url_for('reserva', _external=True)
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Reserva Habitación {reserva.habitacion.numero}",
                        "sku": "reserva_habitacion",
                        "price": str(reserva.habitacion.precio),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(reserva.habitacion.precio),
                    "currency": "USD"
                },
                "description": f"Reserva en Hotel Sol y Luna - Habitación {reserva.habitacion.numero}"
            }]
        })

        if payment.create():
            # Guardar el ID del pago en la base de datos
            logging.info("Pago creado exitosamente.")
            reserva.paypal_payment_id = payment.id
            db.session.commit()

            # Redirigir al usuario a la URL de aprobación de PayPal
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            logging.error(f"Error al crear el pago: {payment.error}")
            flash(f"Error al crear el pago: {payment.error}", "danger")
            return redirect(url_for('reserva'))

    except Exception as e:
        flash(f"Error procesando el pago: {e}", "danger")
        return redirect(url_for('reserva'))

@app.route('/confirmacion_pago/<int:reserva_id>', methods=['GET'])
def confirmacion_pago(reserva_id):
    reserva = Reserva.query.get(reserva_id)
    if not reserva:
        flash("Reserva no encontrada.", "danger")
        return redirect(url_for('reserva'))

    payment = paypalrestsdk.Payment.find(reserva.paypal_payment_id)

    if payment.execute({"payer_id": request.args.get("PayerID")}):
        # Actualizar estado de la reserva
        reserva.estado = "pagada"
        db.session.commit()
        flash("Pago realizado con éxito. Tu reserva está confirmada.", "success")
        return redirect(url_for('reserva'))
    else:
        flash(f"Error al procesar el pago: {payment.error}", "danger")
        return redirect(url_for('reserva'))

@app.route('/confirmacion_reserva/<int:reserva_id>', methods=['GET'])
def confirmacion_reserva(reserva_id):
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para ver la confirmación.", "warning")
        return redirect(url_for('login'))

    try:
        # Cargar reserva desde la base de datos
        reserva = Reserva.query.get(reserva_id)
        if not reserva or reserva.cliente_id != session['usuario_id']:
            flash("Reserva no encontrada o no autorizada.", "danger")
            return redirect(url_for('reserva'))

        # Renderizar página de confirmación
        return render_template('confirmacion_reserva.html', reserva=reserva)

    except Exception as e:
        logging.error(f"Error al cargar la confirmación: {e}")
        flash("Error al cargar la confirmación de la reserva.", "danger")
        return redirect(url_for('reserva'))

@app.route('/habitaciones')
def habitaciones():
    return render_template('habitaciones.html')

@app.route('/habitaciones_disponibles')
def habitaciones_disponibles():
    habitaciones = Habitacion.query.filter_by(estado='disponible').all()
    return render_template('habitaciones_disponibles.html', habitaciones=habitaciones)

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)  # Elimina el usuario de la sesión
    flash("Has cerrado sesión correctamente", "success")
    return redirect(url_for('login'))

@app.route('/consulta', methods=['POST'])
def consulta():
    try:
        nombreConsulta = request.form['nombreConsulta']
        emailConsulta = request.form['emailConsulta']
        mensajeConsulta = request.form['mensajeConsulta']

        # Enviar correo al hotel con los detalles de la consulta
        mensaje_hotel = Message(
            "Nueva Consulta - Hotel Sol y Luna",
            recipients=["hotelsolylunaok@gmail.com"],  # Correo del hotel
            body=f"""
Nueva consulta recibida:

Nombre: {nombreConsulta}
Correo: {emailConsulta}
Mensaje: 
{mensajeConsulta}

Por favor, responde a la consulta a la brevedad.
"""
        )
        mail.send(mensaje_hotel)

        # Enviar correo de confirmación al usuario
        mensaje_usuario = Message(
            "Consulta Recibida - Hotel Sol y Luna",
            recipients=[emailConsulta],  # Correo del usuario
            body=f"""
Hola {nombreConsulta},

Gracias por contactarnos. Hemos recibido tu consulta y nuestro equipo se pondrá en contacto contigo lo antes posible. 

Detalles de tu consulta:
{mensajeConsulta}

Si necesitas más información, no dudes en escribirnos.

Atentamente,
Hotel Sol y Luna
"""
        )
        mail.send(mensaje_usuario)

        flash('Consulta enviada correctamente. Revisa tu correo para la confirmación.', 'success')
    except KeyError as e:
        flash(f'Error al procesar la consulta: {e}', 'danger')
    except Exception as e:
        flash(f'Error al enviar los correos: {str(e)}', 'danger')
    return redirect(url_for('home'))

@app.route('/admin/usuarios', methods=['GET'])
@admin_required
def admin_usuarios():
    nombre = request.args.get('nombre', '').strip()
    dni = request.args.get('dni', '').strip()
    rol = request.args.get('rol', '').strip()

    # Construcción dinámica de la consulta
    query = Usuario.query
    if nombre:
        query = query.filter(Usuario.nombre.like(f"%{nombre}%"))
    if dni:
        query = query.filter(Usuario.dni.like(f"%{dni}%"))
    if rol:
        query = query.filter(Usuario.rol == rol)

    usuarios = query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios)

# Ruta para editar un usuario
@app.route('/admin/usuario/editar/<int:usuario_id>', methods=['GET', 'POST'])
@admin_required
def admin_editar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == 'POST':
        try:
            usuario.nombre = request.form.get('nombre')
            usuario.apellido = request.form.get('apellido')
            usuario.email = request.form.get('email')
            usuario.dni = request.form.get('dni')
            usuario.rol = request.form.get('rol')
            db.session.commit()
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for('admin_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar usuario: {str(e)}", "danger")

    return render_template('admin_editar_usuario.html', usuario=usuario)

# Ruta para eliminar un usuario
@app.route('/admin/usuario/eliminar/<int:usuario_id>', methods=['POST'])
@admin_required
def admin_eliminar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuario eliminado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar usuario: {str(e)}", "danger")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/exportar', methods=['GET'])
@admin_required
def exportar_usuarios():
    usuarios = Usuario.query.all()
    output = []
    for usuario in usuarios:
        output.append([usuario.id, usuario.nombre, usuario.apellido, usuario.email, usuario.dni, usuario.rol])
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Nombre', 'Apellido', 'Email', 'DNI', 'Rol'])
    writer.writerows(output)
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=usuarios.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@app.route('/empleado/cancelar_reserva/<int:reserva_id>', methods=['POST'])
@admin_or_employee_required
def cancelar_reserva_empleado(reserva_id):
    try:
        # Obtener la reserva y cliente asociados
        reserva = Reserva.query.get(reserva_id)
        if not reserva:
            raise ValueError("La reserva no existe.")
        
        cliente = Usuario.query.get(reserva.cliente_id)
        if not cliente:
            raise ValueError("No se encontró el cliente asociado a esta reserva.")
        
        cancelar_reserva(reserva_id)  # Lógica de cancelación
        
        # Envío del correo de cancelación
        mensaje = Message(
            "Confirmación de Cancelación de Reserva",
            recipients=[cliente.email],
            body=f"""
Estimado {cliente.nombre},

Lamentamos informarle que su reserva del día {reserva.fecha_inicio} hasta el día {reserva.fecha_fin} ha sido cancelada con éxito.

Si tiene alguna pregunta, no dude en ponerse en contacto con nosotros.

Atentamente,
Hotel Sol y Luna
"""
        )
        mail.send(mensaje)
        flash("Reserva cancelada exitosamente. El cliente ha sido notificado por correo.", "success")

    except ValueError as ve:
        flash(str(ve), "danger")
    except Exception as e:
        current_app.logger.error(f"Error al cancelar la reserva o enviar el correo: {str(e)}")
        flash("La reserva fue cancelada, pero no se pudo enviar el correo de confirmación.", "warning")

    return redirect(url_for('empleado_reservas'))

@app.route('/empleado/reservas', methods=['GET'])
@admin_or_employee_required
def empleado_reservas():
    cliente_nombre = request.args.get('cliente_nombre', '')
    dni = request.args.get('dni', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    estado = request.args.get('estado', '')
    tipo_habitacion = request.args.get('tipo_habitacion', '')

    # Filtrar reservas según los parámetros
    reservas_query = Reserva.query.join(Usuario, Reserva.usuario_reserva).join(Habitacion, Reserva.habitacion)
    if cliente_nombre:
        reservas_query = reservas_query.filter(Usuario.nombre.ilike(f"%{cliente_nombre}%"))
    if dni:
        reservas_query = reservas_query.filter(Usuario.dni.ilike(f"%{dni}%"))
    if fecha_inicio:
        reservas_query = reservas_query.filter(Reserva.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        reservas_query = reservas_query.filter(Reserva.fecha_fin <= fecha_fin)
    if estado:
        reservas_query = reservas_query.filter(Reserva.estado.ilike(f"{estado}"))
    if tipo_habitacion:
        reservas_query = reservas_query.filter(Habitacion.tipo.ilike(f"%{tipo_habitacion}%"))

    reservas = reservas_query.all()
    return render_template(
        'empleado_reservas.html',
        reservas=reservas,
        cliente_nombre=cliente_nombre,
        dni=dni,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado=estado,
        tipo_habitacion=tipo_habitacion
    )

@app.route('/reportes')
@admin_required
def reportes():
    # Ingresos diarios
    ingresos_diarios_data = db.session.query(
        db.func.date(Reserva.fecha_reserva).label('fecha'),
        db.func.sum(db.func.datediff(Reserva.fecha_fin, Reserva.fecha_inicio) * Habitacion.precio).label('ingresos')
    ).join(Habitacion).group_by(db.func.date(Reserva.fecha_reserva)).all()

    # Ingresos mensuales
    ingresos_mensuales_data = db.session.query(
        db.func.date_format(Reserva.fecha_reserva, '%Y-%m').label('mes'),
        db.func.sum(db.func.datediff(Reserva.fecha_fin, Reserva.fecha_inicio) * Habitacion.precio).label('ingresos')
    ).join(Habitacion).group_by(db.func.date_format(Reserva.fecha_reserva, '%Y-%m')).all()

    # Ingresos por método de pago
    ingresos_metodo_pago_data = db.session.query(
        Reserva.metodo_pago,
        db.func.sum(db.func.datediff(Reserva.fecha_fin, Reserva.fecha_inicio) * Habitacion.precio).label('ingresos')
    ).join(Habitacion).group_by(Reserva.metodo_pago).all()

    # Habitaciones más reservadas
    habitaciones_populares = db.session.query(
        Habitacion.numero,
        Habitacion.tipo,
        db.func.count(Reserva.id).label('num_reservas')
    ).join(Reserva).group_by(Habitacion.id).order_by(db.desc(db.func.count(Reserva.id))).all()

    # Fechas más solicitadas
    fechas_populares = db.session.query(
        db.func.date(Reserva.fecha_inicio).label('fecha'),
        db.func.count(Reserva.id).label('num_reservas')
    ).group_by(db.func.date(Reserva.fecha_inicio)).order_by(db.desc(db.func.count(Reserva.id))).all()

    # Verificar si hay datos disponibles
    if not (ingresos_diarios_data or ingresos_mensuales_data or ingresos_metodo_pago_data):
        flash("No hay datos disponibles para generar los reportes", "warning")
        return redirect(url_for('home'))

    # Gráficos
    fechas_diarios = [ingreso.fecha for ingreso in ingresos_diarios_data]
    ingresos_diarios_values = [ingreso.ingresos for ingreso in ingresos_diarios_data]
    ingresos_diarios_img = crear_grafico(fechas_diarios, ingresos_diarios_values, 'Ingresos Diarios', 'Fecha', 'Ingresos', 'b')

    meses_mensuales = [ingreso.mes for ingreso in ingresos_mensuales_data]
    ingresos_mensuales_values = [ingreso.ingresos for ingreso in ingresos_mensuales_data]
    ingresos_mensuales_img = crear_grafico(meses_mensuales, ingresos_mensuales_values, 'Ingresos Mensuales', 'Mes', 'Ingresos', 'g')

    metodos_pago = [ingreso.metodo_pago for ingreso in ingresos_metodo_pago_data]
    ingresos_metodo_values = [ingreso.ingresos for ingreso in ingresos_metodo_pago_data]
    ingresos_metodo_img = crear_grafico(metodos_pago, ingresos_metodo_values, 'Ingresos por Método de Pago', 'Método de Pago', 'Ingresos', 'y')

    # Pasar datos a la plantilla
    return render_template('reportes.html',
                           ingresos_diarios_data=ingresos_diarios_data,
                           ingresos_mensuales_data=ingresos_mensuales_data,
                           ingresos_metodo_pago_data=ingresos_metodo_pago_data,
                           habitaciones_populares=habitaciones_populares,
                           fechas_populares=fechas_populares,
                           ingresos_diarios_img=ingresos_diarios_img,
                           ingresos_mensuales_img=ingresos_mensuales_img,
                           ingresos_metodo_img=ingresos_metodo_img)


if __name__ == "__main__":
    app.run(debug=True)
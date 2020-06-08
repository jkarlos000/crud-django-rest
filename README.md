# Notas

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://test-rest.ml/v1/)

Notas es un CRUD realizado en Django y Django Rest Framework (DRF) una herramienta que facilita el desarrollo de APIs para nuestra web, también cuenta con un sistema de autenticación JWT (JSon Web Token), ya que ciertos endpoints de la aplicación estarán protegidas.

Este CRUD manipula los siguientes modelos:
  - Usuarios
  - Grupos
  - Accesos
  - Notas

# Funcionalidades

  - Registro de Usuarios
  - Usuarios pueden crear grupos
  - Usuarios pueden dar dar acceso a otros usuarios
  - El usuario solo puede estar asociado a un grupo
  - Autenticación mediante JWT
  - Subir Notas protegido con JWT

JWT Authorization header empleada es  `"Bearer"`

# EndPoints:
User
  - `"v1/users/"` soporta "GET" (listar los usuarios del sistema), "POST" (Permite el registro de usuarios al sistema, es neceario validar el registro desde el enlace enviado al correo electrónico.)
  - `"v1/users/{user}"` soporta "GET" (lista un usuario en específico), "PUT/PATCH" (permite modificar datos del usuario, esta protegido con JWT), "DELETE" (permite eliminar el usuario especificado, esta protegido con JWT)
  - `"v1/users/token"` soporta "POST" (empleado como endpoint de login, requiere el email y password para el intercambio de credenciales JWT)
  - `"v1/token/refresh"` soporta "GET" (extiende el uso del lifetime del token JWT, es necesario proveer el refresh token de nuestra sesión)
  - `"v1/verify/{token}"` soporta "GET" (este 'token', es importante ya que valida el registro del usuario, habilitandolo para realizar operaciones dentro del sistema.)
  - `"v1/{user}/resend"` soporta "GET" (endpoint que permite refrescar el token de validación de registro, generando uno nuevo y enviandolo mediante E-mail a la dirección con la cual se registro.)

Group
  - `"v1/groups/"` soporta "GET" (Lista todos los grupos del sistema), "POST" (permite el registro de nuevos grupos en el sistema, es necesario que el usuario este con la sesión iniciada, protegido con JWT)
  - `"v1/groups/{group}"` soporta "GET" (Muestra información sobre un grupo en específico)
  - `"v1/groups/{group}/users"` soporta "GET" (Muestra todos los usuarios que forman parte de un grupo en específico.)
  - `"v1/groups/{group}/notes"` soporta "GET" (Muestra todas las notas de los usuarios publicadas en un grupo, debe pertener al grupo para poder visualizar, protegido con JWT)

Acceso
  - `"v1/access/"` soporta "POST" (permite agregar otros usuarios a su grupo, es necesario que el usuario invitado hubiese validado su cuenta, que el grupo este disponible, protegido con JWT, existe una version `"v1/access/groups/{group}/users/{user}"`, soporta POST y no requiere body.)

Notas

  - `"v1/notes/{note}"` soporta "GET" (muestra la información de una nota en específico.)

User-Group-Note

  - `"v1/users/{user}/groups/"` soporta "GET" (lista todos los grupos de cual el usuario es dueño, esta protegido con JWT)
  - `"v1/users/{user}/groups/all"` soporta "GET" (lista todos los grupos a los cuáles esta asociado el usuario, esta protegido con JWT.)
  - `"v1/users/{user}/groups/{group}"` soporta "PUT/PATCH" (Modifica un grupo en específico, se requiere que el usuario sea el dueño del grupo, los únicos parametros a cambiar son el "nombre del grupo", "state" o estado del grupo, esta protegido con JWT), "DELETE" (elimina el grupo especificado, se requiere que el usuario sea el dueño del grupo, protegido con JWT.)
  - `"v1/users/{user}/groups/{group}/notes"` soporta "GET" (Muestra información al respecto de una nota del usuario que ha publicado en un grupo específico, esta protegido con JWT), "POST" (crea una nota nueva, se requiere que el usuario este activo y que el grupo este este disponible, esta protegido con JWT.)
  - `"v1/users/{user}/groups/{group}/notes/{note}"` soporta "PUT/PATCH" (permite modificar el contenido de la nota, es necesario tener en cuenta que el grupo debe estar disponible para poder realizar las modificaciones, esta protegido con JWT), "DELETE" (elimina la nota especificada, requiere que el grupo este disponible para poder realizar la eliminación de la nota, esta protegido con JWT.)

### Instalación

Desarrollado en Python 3.8.3, por favor descargue el contenido desde este repositorio.

Es necesario tener instalado virtualenv, dentro de la carpeta del proyecto clonado, instale su entorno virtual de Python, activelo y ejecute los siguientes comandos.

```sh
$ pip install -r requirements.txt
$ python manage.py createmigrations
$ python manage.py migrate
```

### Inconvenientes

 - Código espagueti
 - Problemas para tener dos columnas de la base de datos como llave primaria ([ver aqui](https://code.djangoproject.com/wiki/MultipleColumnPrimaryKeys))
 - No se realizaron todos los tests, pero si se comprobo la funcionalidad en la mayoría de los casos.
 - Si va a utilizar un servicio de Email, modifique los datos de EMAIL en settings, cambie la URL del template que se ocupa para el envio de correos electrónicos.
 - Actualmente hay un ambiente de pruebas (puede mirar)

**Free Software, Hell Yeah!**

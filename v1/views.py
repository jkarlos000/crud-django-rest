from rest_framework import status
from rest_framework.decorators import api_view, permission_classes  # , authentication_classes
from rest_framework.views import APIView
from .serializers import *
from .messages import *
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

class IsAuthenticatedOrReadOnly(IsAuthenticated):
    SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

    def has_permission(self, request, view):
        if (request.method in self.SAFE_METHODS or
                request.user and
                request.user.is_authenticated):
            return True
        return False


@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'List users': '/users/',
        'List user': '/users/{user}/',
        'Create user': '/users/',
        'Update user': '/users/{user}/',
        'Delete user': '/users/{user}/',
        'Login user': '/users/token/',
        'Refresh session user': '/users/token/refresh',
    }
    return showOne(api_urls)


@api_view(['GET'])
def verify_token(request, token):
    if request.method == 'GET':
        try:
            user = User.objects.get(verification_token=token)
            data = {'is_active': True, 'verification_token': '0'}
            serializer = UserSerializer(instance=user, data=data)
            if serializer.is_valid():
                serializer.save()
                return showMessage("Se ha activado tu cuenta.")
        except ObjectDoesNotExist:
            return errorMessage("Operación no permitida.")
    return errorMessage("No permitido", status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def resend_token(request, pk):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=pk)
            if not user.is_active:
                serializer = UserSerializer(instance=user, data={'verification_token': 'generate'})
                if serializer.is_valid():
                    serializer.save()
                    email_data = {'subject': 'Reenvio de enlace de activación.',
                                  'email': serializer.data.get('email'),
                                  'verification_token': serializer.data.get('verification_token')}
                    sendEmail(email_data)
                    return showMessage(
                        "Un email ha sido enviado con su clave de activación, revise su correo por favor, si no lo "
                        "encuentra, revise en SPAM.")
            else:
                return errorMessage("El user ya esta activo.")
        except ObjectDoesNotExist:
            return errorMessage("Operación no permitida.")
    return errorMessage("No permitido", status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def list_group(request, pk):
    try:
        group = Group.objects.get(id=pk)
        serializer = GroupSerializer(group)
        data_list = ['id', 'name', 'status', 'user']
        return showOne(oneToDict(serializer.data, data_list))
    except BaseException as e:
        return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_group_users(request, pk):
    try:
        group = Group.objects.get(id=pk)
        users_id = Access.objects.filter(group=group).values_list('user', flat=True)
        user = User.objects.filter(id__in=users_id)
        serializer = UserSerializer(user, many=True)
        data_list = ['email', 'name', 'last_name', 'is_active', 'last_login']
        return showAll(bulkToDict(serializer.data, data_list))

    except BaseException as e:
        return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_group_notes(request, pk):
    try:
        group = Group.objects.get(id=pk)
        if len(Access.objects.filter(group=group, user=request.user)) != 0 or request.user.is_superuser:
            notes_id = Note.objects.filter(group=group)
            notes = Note.objects.filter(id__in=notes_id)
            serializer = NoteSerializer(notes, many=True)
            data_list = ['user', 'group', 'title', 'body']
            return showAll(bulkToDict(serializer.data, data_list))
        return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
    except BaseException as e:
        return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_note(request, pk):
    try:
        note = Note.objects.get(id=pk)
        serializer = NoteSerializer(note)
        data_list = ['user', 'group', 'title', 'body']
        return showOne(oneToDict(serializer.data, data_list))
    except BaseException as e:
        return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_groups(request, user_pk):
    try:
        if str(request.user.id) == str(user_pk) or request.user.is_superuser:
            user = User.objects.get(id=user_pk)
            groups_id = Group.objects.filter(user=user)
            groups = Group.objects.filter(id__in=groups_id)
            serializer = GroupSerializer(groups, many=True)
            data_list = ['id', 'name', 'status']
            return showAll(bulkToDict(serializer.data, data_list))
        return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
    except BaseException as e:
        return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_groups_all(request, user_pk):
    try:
        if str(request.user.id) == str(user_pk) or request.user.is_superuser:
            user = User.objects.get(id=user_pk)
            groups_id = Access.objects.filter(user=user).values_list('group', flat=True)
            groups = Group.objects.filter(id__in=groups_id)
            serializer = GroupSerializer(groups, many=True)
            data_list = ['id', 'name', 'status', 'user']
            return showAll(bulkToDict(serializer.data, data_list))
        return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
    except BaseException as e:
        return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def access_post(request):
    try:
        allowParams = ['user', 'group']
        if not isValidParams(request.data, allowParams):
            return errorMessage({"info": "Faltan parametros de registro."})
        data = oneToDict(request.data, allowParams)
        group = Group.objects.get(id=data['group'])
        if request.user == group.user or request.user.is_superuser:
            invite = Access.objects.filter(group=data['group'], user_id=data['user'])
            if len(invite) == 0:
                serializer = AccessSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return showMessage("Usuario agregado exitosamente.")
            return errorMessage("Este user ya pertenece a su grupo")
        return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
    except BaseException as e:
        return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

class Users(APIView):
    """
    Users Retorna una lista de todos los **usuarios** del sistema.
    Métodos no protegidos con JWT: todos.

    get:
    Return a lista de todos los usarios existentes.

    post:
    Crea un user con los parametros: email, password, password_verification.
    """
    def get(self, request, format=None):
        """
        Get retorna una lista completa de todos los usuarios.
        :param request: Solicitud de respuesta desde el usuario.
        :param format: None
        :return: Json formato con la lista de todos los usaurios.
        """
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        data_list = ['email', 'name', 'last_name', 'is_active', 'last_login']
        return showAll(bulkToDict(serializer.data, data_list))

    def post(self, request, format=None):
        allowParams = ['email', 'name', 'last_name', 'password', 'password_verification']
        if not isValidParams(request.data, allowParams):
            return errorMessage({"info": "Faltan parametros de registro."})

        data = oneToDict(request.data, allowParams)

        if data.get('password'):
            if data.get('password') != data.get('password_verification'):
                return errorMessage({"message": "Las contraseñas no coincide."}, status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            email_data = {'subject': 'Enlace para la activación de cuenta.', 'email': serializer.data.get('email'),
                          'verification_token': serializer.data.get('verification_token')}
            sendEmail(email_data)
            data_list = ['email', 'date_joined']
            return showOne(oneToDict(serializer.data, data_list, {
                'info': 'Un email ha sido enviado con su clave de activación, revise su correo por favor, si no lo '
                        'encuentra, revise en SPAM.'}),
                           status.HTTP_201_CREATED)
        return errorMessage(serializer.errors, status.HTTP_400_BAD_REQUEST)


class UsersDetail(APIView):
    """
    UsersDetail muestra un único usuario a partir de su <id>.
    Métodos no protegidos con JWT: get, head, options.

    get:
    Return una respuesta en Json de los datos del usuario.

    put/patch:
    Modifica los parametros del usuario ('email', 'name', 'last_name', 'password')
    Si desea modificar la contraseña deberá agregar el campo 'password_verification'.

    delete:
    Elimina la instancia del usuario. Es necesario estar autenticado con JWT.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return User.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise Exception("El user no existe")

    def get(self, request, pk, format=None):
        try:
            user = self.get_object(pk)
            serializer = UserSerializer(user)
            data_list = ['email', 'name', 'last_name', 'is_active', 'date_joined']
            return showOne(oneToDict(serializer.data, data_list))
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        if not request.user.is_superuser:
            if not request.user.is_active:
                return errorMessage("Su cuenta no esta activa aún, validela primero.", status.HTTP_403_FORBIDDEN)
            if str(request.user.id) != str(pk):
                return errorMessage("No tiene permisos para realizar esta operación",
                                    status.HTTP_401_UNAUTHORIZED)
        allowParams = ['email', 'name', 'last_name', 'password', 'password_verification']
        data = oneToDict(request.data, allowParams)
        if data.get('password'):
            if data.get('password') != data.get('password_verification'):
                return errorMessage({"message": "Las contraseñas no coincide."})
        try:
            user = self.get_object(pk)
            serializer = UserSerializer(instance=user, data=data)
            if serializer.is_valid():
                serializer.save()
                data_list = ['id', 'email', 'name', 'last_name', 'is_active', 'date_joined']
                return showOne(oneToDict(serializer.data, data_list))
            return errorMessage(serializer.errors)
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, format=None):
        return self.put(request, pk)

    def delete(self, request, pk, format=None):
        try:
            if not request.user.is_superuser:
                if str(request.user.id) != str(pk):
                    return errorMessage({"message": "No tiene permisos para realizar esta operación"},
                                        status.HTTP_403_FORBIDDEN)
            user = self.get_object(pk)
            user.delete()
            return showMessage("El user ha sido eliminado.")
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)


class Groups(APIView):
    """
    Groups lista todos los grupos del sistema. El campo status definirá si podra agregar otro usuarios o no a su grupo.
    Métodos no protegidos con JWT: get, head, options.

    URL de acceso: /v1/groups/

    get:
    Retorna una lista en formato Json de todos los grupos en el sistema.

    post:
    Registra un grupo en específico, es necesario que el usuario cuente con autenticación JWT.

    La ruta "/v1/grupos/{group}/notes" se encuentra protegida con JWT, solamente los miembros del grupo pueden ver las
    notas.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return User.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise Exception("El user no existe")

    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        data_list = ['id', 'name', 'status', 'user']
        return showAll(bulkToDict(serializer.data, data_list))

    def post(self, request):
        allowParams = ['name']
        if not isValidParams(request.data, allowParams):
            return errorMessage({"info": "Faltan parametros de registro."})
        data = oneToDict(request.data, allowParams)
        data.update({'user': request.user.id})
        serializer = GroupSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            data_list = ['id', 'name', 'status', 'user']
            return showOne(oneToDict(serializer.data, data_list, {'info': 'Grupo creado exitosamente!'}))
        return errorMessage(serializer.errors)

class AccessGroups(APIView):
    """
    AccessGroups permite a un dueño de grupo agregar a otro usuario a su grupo.
    Con esto tendra acceso a todas las notas existentes en el grupo.
    Métodos no protegidos con JWT: ninguno.

    URL de acceso: /v1/access/groups/{group}/users/{user}

    post:
    Registra un usuario dentro de un grupo, siempre y cuando usted sea dueño del grupo y tambiene este habilitado.

    delete:
    Elimina un usuario de un grupo, [Verificar si las Notas tambien se eliminan]
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, group_pk, user_pk):
        try:
            group = Group.objects.get(id=group_pk)
            if request.user == group.user or request.user.is_superuser:
                invite = Access.objects.filter(group=group_pk, user_id=user_pk)
                if len(invite) == 0:
                    serializer = AccessSerializer(data={'group': group_pk, 'user': user_pk})
                    if serializer.is_valid():
                        serializer.save()
                        return showMessage("Usuario agregado exitosamente.")
                return errorMessage("Este user ya pertenece a su grupo")
            return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

    def delete(self, request, group_pk, user_pk):
        try:
            group = Group.objects.get(id=group_pk)
            if request.user == group.user or request.user.is_superuser:
                invite = Access.objects.get(group=group_pk, user_id=user_pk)
                invite.delete()
                return showMessage("El user ha sido eliminado de su grupo.")
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

class UserGroup(APIView):
    """
    UserGroup maneja funciones especiales de User y Group, como modificar el 'nombre', 'status' de un grupo del cuál
    sea propietario.
    Métodos no protegidos con JWT: ninguno.
    URL de acceso: /v1/users/{user}/groups/{group}
    put/patch:
    Modifica los datos de un grupo 'name', 'status' (enable, disable).

    delete:
    Elimina un grupo en especifico.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def put(self, request, user_pk, group_pk):
        try:
            if (len(Group.objects.filter(id=group_pk, user_id=user_pk)) != 0 and str(request.user.id) == str(user_pk)) or request.user.is_superuser:
                allowParams = ['name', 'status']
                data = oneToDict(request.data, allowParams)
                group = Group.objects.get(id=group_pk)
                serializer = GroupSerializer(instance=group, data=data)
                if serializer.is_valid():
                    serializer.save()
                    data_list = ['id', 'name', 'status', 'user']
                    return showOne(oneToDict(serializer.data, data_list, {'info': 'Información actualizada.'}))
                return errorMessage(serializer.errors)
            return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

    def patch(self, request, user_pk, group_pk):
        return self.put(request, user_pk, group_pk)

    def delete(self, request, user_pk, group_pk):
        try:
            if (len(Group.objects.filter(id=group_pk, user_id=user_pk)) != 0 and str(request.user.id) == str(user_pk)) or request.user.is_superuser:
                group = Group.objects.get(id=group_pk)
                group.delete()
                return showMessage("Grupo eliminado on éxito.")
            return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

class UserGroupNote(APIView):
    """
    UserGroupNote encargada de listar y registrar las notas de un usuario, si quiere ver una nota en específico revise:
    en v1/notes/{note}
    Métodos no protegidos con JWT: ninguno.

    URL de acceso: /v1/users/{user}/groups/{group}/notes

    get:
    Lista todas las notas del usuario específicado que fueron creadas dentro de un grupo (únicamente las de él).

    post:
    Crea una nueva nota en el grupo específicado, tenga en cuenta que esta nota ya se comparte automáticamente con el
    grupo al ser creada.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_pk, group_pk):
        try:
            group = Group.objects.get(id=group_pk)
            if (group.user == request.user and str(request.user.id) == user_pk) or request.user.is_superuser:
                notes_id = Note.objects.filter(group=group, user_id=user_pk)
                notes = Note.objects.filter(id__in=notes_id)
                serializer = NoteSerializer(notes, many=True)
                data_list = ['group', 'title', 'body']
                return showAll(bulkToDict(serializer.data, data_list))
            return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

    def post(self, request, user_pk, group_pk):
        try:
            group = Group.objects.get(id=group_pk)
            # group.user == request.user
            if (len(Access.objects.filter(group=group, user=request.user)) != 0 and str(request.user.id) == user_pk) or request.user.is_superuser:
                allowParams = ['title', 'body']
                if not isValidParams(request.data, allowParams):
                    return errorMessage({"info": "Faltan parametros de registro."})
                data = oneToDict(request.data, allowParams)
                data.update({'user': user_pk, 'group': group_pk})
                serializer = NoteSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    data_list = ['title', 'body', 'group']
                    return showOne(oneToDict(serializer.data, data_list, {'info': 'Nota creada exitosamente!'}))
                return errorMessage(serializer.errors)
            return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

class UserGroupNoteDetail(APIView):
    """
    UserGroupNoteDetail encargada de modificar y eliminar las notas de un usuario, si quiere ver una
    nota en específico revise:
    en v1/notes/{note}
    Métodos no protegidos con JWT: get, head, options.

    URL de acceso: /v1/users/{user}/groups/{group}/notes

    put/patch:
    Modifica una Nota del usuario, si el grupo esta disable no podrá actualizar su nota. Abstengase a la auditoría.

    delete:
    Elimina una nota en especifico, si el grupo esta deshabilitado, no podrá eliminar la nota, a menos que se realice
    una cirugia de datos.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def put(self, request, user_pk, group_pk):
        try:
            group = Group.objects.get(id=group_pk)
            if (group.user == request.user and str(request.user.id) == user_pk) or request.user.is_superuser:
                allowParams = ['title', 'body']
                data = oneToDict(request.data, allowParams)
                note = Note.objects.get(user_id=user_pk, group=group)
                serializer = NoteSerializer(instance=note, data=data)
                if serializer.is_valid():
                    serializer.save()
                    data_list = ['title', 'body', 'group']
                    return showOne(oneToDict(serializer.data, data_list))
                return errorMessage(serializer.errors)
            return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

    def patch(self, request, user_pk, group_pk):
        return self.put(request, user_pk, group_pk)

    def delete(self, request, user_pk, group_pk):
        try:
            group = Group.objects.get(id=group_pk)
            if (group.user == request.user and str(request.user.id) == user_pk and group.status == 'enable') or request.user.is_superuser:
                note = Note.objects.get(user_id=user_pk, group=group)
                note.delete()
                return showMessage("Nota eliminada on éxito.")
            return errorMessage("Operacion no permitida", status.HTTP_403_FORBIDDEN)
        except BaseException as e:
            return errorMessage({"message": e.args}, status.HTTP_404_NOT_FOUND)

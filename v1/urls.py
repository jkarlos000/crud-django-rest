from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from v1.views import (
    apiOverview,
    Users,
    UsersDetail,
    verify_token,
    resend_token,
    Groups,
    list_user_groups,
    list_group,
    list_group_users,
    list_user_groups_all,
    AccessGroups,
    list_group_notes,
    list_note,
    access_post,
    UserGroup,
    UserGroupNote,
    UserGroupNoteDetail)

urlpatterns = [
    path('', apiOverview, name="api-overview"),

    path('users/', Users.as_view(), name='users'),  # Listar, Crear
    path('users/<str:pk>', UsersDetail.as_view(), name='users_single'),
    path('users/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('users/verify/<str:token>', verify_token, name='verify_token'),
    path('users/<str:pk>/resend', resend_token, name='resend_token'),

    path('groups/', Groups.as_view(), name='groups'),  # Listar, Crear
    path('groups/<str:pk>', list_group, name='groups_single'),
    path('groups/<str:pk>/users', list_group_users, name='groups_single_users'),
    path('groups/<str:pk>/notes', list_group_notes, name='groups_single_notes'),

    path('access/groups/<str:group_pk>/users/<str:user_pk>', AccessGroups.as_view(), name='access'),
    path('access/', access_post, name='access-post'),

    path('notes/<str:pk>', list_note, name='notes_user'),

    path('users/<str:user_pk>/groups/', list_user_groups, name='users_groups_list'),
    path('users/<str:user_pk>/groups/all', list_user_groups_all, name='users_groups_list_all'),
    path('users/<str:user_pk>/groups/<str:group_pk>', UserGroup.as_view(), name='users_groups'),
    path('users/<str:user_pk>/groups/<str:group_pk>/notes', UserGroupNote.as_view(), name='users_groups_notes'),
    path('users/<str:user_pk>/groups/<str:group_pk>/notes/<str:note_pk>', UserGroupNoteDetail.as_view(), name='users_groups_notes_single')

]

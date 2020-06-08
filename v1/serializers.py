from rest_framework import serializers
from .models import User, Group, Access, Note
from django.core import validators
import secrets

class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    # email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    verified = serializers.CharField(required=False)
    verification_token = serializers.CharField(required=False)
    update_at = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        instance = User()
        instance.name = validated_data.get('name')
        instance.last_name = validated_data.get('last_name')
        self.valid_email(validated_data.get('email'))
        instance.email = validated_data.get('email')
        instance.set_password(validated_data.get('password'))
        instance.is_active = False
        instance.verification_token = str(secrets.token_hex(43))
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for k in validated_data:
            if k == 'name':
                instance.name = validated_data.get('name')
            if k == 'last_name':
                instance.last_name = validated_data.get('last_name')
            if k == 'email':
                if str(instance.email) != str(validated_data.get('email')):
                    self.valid_email(validated_data.get('email'))
                instance.email = validated_data.get('email')
            if k == 'password':
                instance.set_password(validated_data.get('password'))
            if k == 'verification_token':
                if validated_data.get('verification_token') != '0':
                    instance.verification_token = str(secrets.token_hex(43))
                else:
                    instance.verification_token = validated_data.get('verification_token')
            if k == 'is_active':
                instance.is_active = validated_data.get('is_active')
        instance.save()
        return instance

    def validate_email(self, data):
        try:
            validators.validate_email(data)
            return data
        except validators.ValidationError as e:
            raise serializers.ValidationError(e)

    def valid_email(self, data):
        users = User.objects.filter(email=data)
        if len(users) != 0:
            raise serializers.ValidationError("Correo electronico ya registrado")
        else:
            return data

class GroupSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    update_at = serializers.CharField(required=False)
    user = serializers.CharField(required=False)
    # user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id')

    class Meta:
        model = Group
        fields = '__all__'

    def create(self, validated_data):
        instance = Group()
        instance.name = validated_data.get('name')
        user = User.objects.get(id=validated_data.get('user'))
        instance.user = user
        instance.save()
        if user.active_group == '0':
            user.active_group = instance.id
            user.save()
        access = Access()
        access.user = user
        access.group = instance
        access.save()
        return instance

    def update(self, instance, validated_data):
        for k in validated_data:
            if k == 'name':
                instance.name = validated_data.get('name')
            if k == 'status':
                if not validated_data.get('status') in ['enable', 'disable']:
                    raise serializers.ValidationError("Status no válido, use 'disable' o 'enable'")
                instance.status = validated_data.get('status')
        instance.save()
        return instance

class AccessSerializer(serializers.ModelSerializer):
    user = serializers.CharField(required=False)
    group = serializers.CharField(required=False)
    date_joined = serializers.CharField(required=False)

    class Meta:
        model = Access
        fields = '__all__'

    def create(self, validated_data):
        instance = Access()
        user = User.objects.get(id=validated_data.get('user'))
        group = Group.objects.get(id=validated_data.get('group'))
        if group.status == 'disable':
            raise serializers.ValidationError("El grupo seleccionado esta deshabilitado.")
        instance.user = user
        if not user.is_active:
            raise serializers.ValidationError("El user seleccionado esta deshabilitado.")
        instance.group = group
        instance.save()
        return instance

class NoteSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    body = serializers.CharField(required=False)
    user = serializers.CharField(required=False)
    group = serializers.CharField(required=False)
    created_at = serializers.CharField(required=False)
    updated_at = serializers.CharField(required=False)

    class Meta:
        model = Note
        fields = '__all__'

    def create(self, validated_data):
        instance = Note()
        user = User.objects.get(id=validated_data.get('user'))
        group = Group.objects.get(id=validated_data.get('group'))
        instance.user = user
        if group.status == 'disable':
            raise serializers.ValidationError("El grupo seleccionado esta deshabilitado.")
        instance.group = group
        instance.title = validated_data.get('title')
        instance.body = validated_data.get('body')
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if instance.group.status == 'disable':
            raise serializers.ValidationError("El grupo seleccionado esta deshabilitado.")
        for k in validated_data:
            if k == 'title':
                instance.title = validated_data.get('title')
            if k == 'body':
                instance.body = validated_data.get('body')
        instance.save()
        return instance

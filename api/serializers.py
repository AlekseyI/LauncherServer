from rest_framework import serializers
from main.models import *
from django.contrib.auth import authenticate
from rest_framework import exceptions
from rest_framework.authtoken.models import Token
import api.reg as parser
import base64
import requests
from TestServer.settings import AUTH_SERVER


class ProgramInfoSerializer(serializers.ModelSerializer):
    is_updated = serializers.SerializerMethodField(read_only=True, required=False)

    def get_is_updated(self, obj):
        return True

    class Meta:
        model = ProgramInfo
        fields = [
            'name',
            'version',
            'is_updated',
            'dep'
        ]


class CheckVersionLauncherSerializer(serializers.ModelSerializer):
    is_updated = serializers.SerializerMethodField(read_only=True, required=False)

    def get_is_updated(self, obj):
        return self.validated_data['version'] == obj.version

    def update(self, instance, validated_data):
        return instance

    class Meta:
        model = ProgramInfo
        extra_kwargs = {
            'version': {'required': True},
        }
        fields = [
            'version',
            'is_updated',
        ]


class CheckVersionProgramSerializer(serializers.ModelSerializer):
    is_updated = serializers.SerializerMethodField(read_only=True, required=False)

    def get_is_updated(self, obj):
        if isinstance(obj, ProgramInfo):
            return obj.get_data['version'] == obj.version
        return None

    def to_internal_value(self, data):
        try:
            prog = ProgramInfo.objects.get(dep=data['dep'])
            if self.context['user'].allowedprogram_set.all().filter(program_id=prog).exists():
                prog.get_data = data
                return prog
            else:
                raise ProgramInfo.DoesNotExist()
        except ProgramInfo.DoesNotExist:
            return {'version': None, 'dep': None, 'is_updated': None}

    class Meta:
        model = ProgramInfo
        extra_kwargs = {
            'version': {'required': True},
            'dep': {'required': True}
        }
        fields = [
            'version',
            'is_updated',
            'dep'
        ]


class ProgramSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField(read_only=True, required=False)
    is_updated = serializers.SerializerMethodField(read_only=True, required=False)

    def get_is_updated(self, obj):
        return True

    def get_data(self, obj):
        with FileReader.read_file(obj.program.path, 'r+b') as data_file:
            enc_data = base64.b64encode(data_file)
        return enc_data

    class Meta:
        model = ProgramInfo

        extra_kwargs = {
            'dep': {'required': True},
            'name': {'allow_null': True},
            'version': {'allow_null': True},
            'hash': {'allow_null': True}
        }

        fields = [
            'name',
            'version',
            'data',
            'hash',
            'dep',
            'is_updated'
        ]


class LauncherSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField(read_only=True, required=False)
    is_updated = serializers.SerializerMethodField(read_only=True, required=False)

    def get_is_updated(self, obj):
        return True

    def get_data(self, obj):
        with FileReader.read_file(obj.program.path, 'r+b') as data_file:
            enc_data = base64.b64encode(data_file)
        return enc_data

    class Meta:
        model = ProgramInfo

        extra_kwargs = {
            'name': {'required': False},
            'version': {'required': False},
            'hash': {'required': False}
        }

        fields = [
            'name',
            'version',
            'data',
            'hash',
            'is_updated'
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def update_user_programs(self, get_json, user):
        try:
            if get_json is None:
                raise exceptions.ValidationError({'detail': ['Ошибка получения списка программ']})
            if AllowedProgram.objects.filter(user_id=user).exists():
                id_prog = user.allowedprogram_set.all().values('program_id')
                user_prog = ProgramInfo.objects.filter(id__in=id_prog)
                for prog in user_prog:
                    prog.admitteduser_set.all().delete()
                user.allowedprogram_set.all().delete()

            if isinstance(get_json['DepId'], list):
                if len(get_json['DepId']) > 0 and get_json['DepId'].__contains__(0):
                    raise ProgramInfo.DoesNotExist()
                for dep in get_json['DepId']:
                    prog = ProgramInfo.objects.get(dep=dep)
                    AdmittedUser.objects.create(program_id=prog, user_id=user)
                    AllowedProgram.objects.create(user_id=user, program_id=prog)
            else:
                raise exceptions.ValidationError({'detail': ['Ошибка получения списка программ']})
        except ProgramInfo.DoesNotExist:
            raise exceptions.ValidationError({'detail': ['Для пользователя с такими данными программ не найдено']})

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                attrs['user'] = user
                self.update_user_programs(self.context, user)
            else:
                raise exceptions.ValidationError({'detail': ['Аккаунт не активен']})
        else:
            raise exceptions.ValidationError({'detail': ['Неверено введен логин или пароль']})
        return attrs


class TokenSerializer(serializers.ModelSerializer):

    @staticmethod
    def get_token(user):
        return Token.objects.get_or_create(user=user)

    class Meta:
        model = Token
        fields = [
            'key'
        ]


class UserSerializer(serializers.ModelSerializer):

    def auth_remote(self, username, password):
        try:
            data = requests.get(AUTH_SERVER.format(username, Crypt.hash(password)))
            if data.status_code != 200:
                raise requests.exceptions.ConnectionError()
            else:
                get_json = data.json()[0]

                if 'AuthStatus' not in get_json or 'AuthStatus' in get_json and \
                        not isinstance(get_json['AuthStatus'], bool) or 'DepId' not in get_json:
                    raise requests.exceptions.ConnectionError()

                try:
                    get_json['DepId'] = parser.parse_to_list(get_json['DepId'])
                except parser.DecodeException:
                    raise requests.exceptions.ConnectionError()


                if not get_json['AuthStatus']:
                    raise exceptions.ValidationError({'detail': ['Неверено введен логин или пароль']})

        except requests.exceptions.ConnectionError:
            raise exceptions.ValidationError({'detail': ['Возникла ошибка при авторизации, попробуйте позже']})
        return get_json

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    def is_valid(self, raise_exception=False):
        valid = super(UserSerializer, self).is_valid(raise_exception)
        if len(self.validated_data) == 0:
            self.context['data'] = self.auth_remote(self.data['username'], self.data['password'])
        else:
            self.context['data'] = self.auth_remote(self.validated_data['username'], self.validated_data['password'])
        return valid

    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]


class ValidateCheckProgramSerializer(serializers.ModelSerializer):
    programs_info = serializers.ListSerializer(child=CheckVersionProgramSerializer(), allow_null=True)

    def create(self, validated_data):
        for prog in validated_data['programs_info']:
            if not isinstance(prog, ProgramInfo):
                validated_data['programs_info'].remove(prog)
        return validated_data

    class Meta:
        model = ProgramInfo
        fields = [
            'programs_info'
        ]


class UserCheckProgramSerializer(serializers.ModelSerializer):
    programs_info = serializers.SerializerMethodField(read_only=True, required=False)

    def get_programs_info(self, obj):
        return ProgramInfoSerializer(obj, many=True).data

    class Meta:
        model = ProgramInfo
        fields = [
            'programs_info'
        ]

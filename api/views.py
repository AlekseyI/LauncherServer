from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from django.contrib.auth import login, logout


# Create your views here.

class LogoutView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        logout(request)
        return Response({'detail': ['ok']}, status=status.HTTP_200_OK)


class CheckVersionLauncherView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            inst = ProgramInfo.objects.get(type=ProgramInfo.LAUNCHER)
            serializer = CheckVersionLauncherSerializer(data=request.data, instance=inst)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProgramInfo.DoesNotExist:
            return Response({'detail': ['Данных нет']}, status=status.HTTP_200_OK)


class CheckVersionProgramView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = ValidateCheckProgramSerializer(data=request.data, context={'user': self.request.user})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_200_OK)
        if request.data['programs_info'] is None or len(request.data['programs_info']) == 0:
            id_progs = self.request.user.allowedprogram_set.all().values('program_id')
            user_progs = ProgramInfo.objects.filter(id__in=id_progs)
            serializer = UserCheckProgramSerializer(user_progs)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = ValidateCheckProgramSerializer(data=request.data, context={'user': self.request.user})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReturnLauncherView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            serializer = LauncherSerializer(ProgramInfo.objects.get(type=ProgramInfo.LAUNCHER))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProgramInfo.DoesNotExist:
            return Response({'detail': ['Данных нет']}, status=status.HTTP_200_OK)


class ReturnProgramView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            serializer = ProgramSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_200_OK)
            id_prog = self.request.user.allowedprogram_set.all().filter(program_id__dep=serializer.validated_data['dep']).values('program_id')
            user_prog = ProgramInfo.objects.get(id__in=id_prog)
            serializer = ProgramSerializer(user_prog)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProgramInfo.DoesNotExist:
            return Response({'detail': ['Данных нет']}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            user_ser = UserSerializer(data=request.data)
            if user_ser.is_valid():
                user_ser.save()

            serializer = LoginSerializer(data=request.data, context=user_ser.context['data'])
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            login(request, user)
            TokenSerializer.get_token(user)

        except exceptions.ValidationError as ex:
            return Response(ex.detail, status=status.HTTP_200_OK)
        return Response(user_ser.data, status=status.HTTP_200_OK)

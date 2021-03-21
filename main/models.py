import mmap

from django.db import models
import hashlib
import os
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from TestServer.settings import AUTH_USER_MODEL
# Create your models here.


class Crypt:

    @staticmethod
    def hash(data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()


class FileReader:

    @staticmethod
    def read_file(path, access):
        with open(path, access) as file:
            data = mmap.mmap(file.fileno(), 0)
        return data


class ProgramInfo(models.Model):

    LAUNCHER = 'LNR'
    PROGRAM = 'PGM'

    TYPE_PROGRAM = (
        (LAUNCHER, 'Лаунчер'),
        (PROGRAM, 'Программа'),
    )

    name = models.CharField('Название', max_length=100)
    start_app = models.CharField('Запускаемый файл', max_length=100)
    version = models.CharField('Версия', max_length=20)
    hash = models.CharField('Хэш', max_length=64)
    type = models.CharField('Тип приложения', max_length=3, choices=TYPE_PROGRAM, default=PROGRAM)
    program = models.FileField('Программа', upload_to='programs')
    dep = models.PositiveIntegerField('DepId')

    get_data = None

    def __str__(self):
        return self.name


class User(AbstractUser):

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class AllowedProgram(models.Model):
    user_id = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    program_id = models.ForeignKey(ProgramInfo, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Разрешенная программа'
        verbose_name_plural = 'Разрешенные программы'


class AdmittedUser(models.Model):
    program_id = models.ForeignKey(ProgramInfo, on_delete=models.CASCADE)
    user_id = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Допущенный пользователь'
        verbose_name_plural = 'Допущенные пользователи'


@receiver(post_save, sender=ProgramInfo)
def encode_hash_program(sender, instance, created, **kwargs):
    if instance.get_data is None:
        if instance.hash != '':
            instance.get_data = {'save': True}
            instance.save()
        elif os.path.isfile(instance.program.path):
            with FileReader.read_file(instance.program.path, 'r+b') as data_file:
                instance.hash = Crypt.hash(data_file)
                instance.get_data = {'save': True}
                instance.save()
        else:
            raise ValueError('Файл {0} не найден'.format(instance.program.name))


@receiver(pre_save, sender=ProgramInfo)
def pre_encode_hash_program(sender, instance, *args, **kwargs):
    try:
        prog = sender.objects.get(hash=instance.hash)
        if prog.program.path != instance.program.path:
            if os.path.isfile(prog.program.path):
                os.remove(prog.program.path)
            instance.hash = ''
    except sender.DoesNotExist:
        pass


@receiver(post_delete, sender=ProgramInfo)
def delete_program(sender, instance, **kwargs):
    if os.path.isfile(instance.program.path):
        os.remove(instance.program.path)
import secrets

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class StaticFilesStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    location = 'nawoka/media'
    default_acl = 'public-read'
    default_content_type = 'image/jpg'
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    location = 'private'
    default_acl = 'private'
    default_content_type = 'image/jpg'
    file_overwrite = False
    custom_domain = False


class CustomeFileSystemStorage(FileSystemStorage):
    def _open(self, name, mode='rb'):
        obj = File(open(self.path(name), mode))
        new_name = secrets.token_hex(5)
        _, ext = name.split('.')
        obj.name = f'{new_name}.{ext}'
        return obj


def select_storage():
    return (CustomeFileSystemStorage() 
        if settings.DEBUG else PublicMediaStorage())

"""This module regroups a series of classes and utilities that can be useful
for interacting with AWS within Django (e.g. uploading items...)

Base
----

    There are three main classes:
        - AWS
        - QueryManager
        - TransferManager

    The two last classes are subclasses of AWS so you might want to use the latter
    directly as opposed to the main one.

Utilities
---------

    The utilities definitions are useful for doing common stuffs when dealing with
    AWS -; for instance creating a file name and path:

        - object_size_creator
        - aws_url_for
        - unique_path_creator

author: pendenquejohn@gmail.com
"""

import os
import secrets
from mimetypes import guess_extension, guess_type
from django.conf import settings

import boto3

# SETTINGS = {
#     'url': 'https://s3.%s.amazonaws.com/%s/%s',

#     'bucket_name': settings.AWS_STORAGE_BUCKET_NAME,
#     'region_name': settings.AWS_S3_REGION_NAME,

#     'access_keys': {
#         'secret_key': settings.AWS_SECRET_ACCESS_KEY,
#         'access_key': settings.AWS_ACCESS_KEY_ID
#     }
# }

def object_size_creator(image_or_path):
    """
    Create three different types of image sizes for the
    S3 bucket. The original one, small, medium and large.

    Creates a dictionnary of values such as:
        {
            original: file.txt, 
            small: file-small.txt, 
            medium: file-medium.txt, 
            large: file-large.txt
        }
    """
    name, extension = image_or_path.split('.', 1)
    images_size = {
        'original': image_or_path,
        'small': name + '-small',
        'medium': name + '-medium',
        'large': name + '-large'
    }

    for key, value in images_size.items():
        if key != 'original':
            images_size.update({key: value + '.' + extension})

    return images_size

def aws_url_for(object_path):
    """
    Create a base url for an object that was previously
    created in a bucket in order to save it to a local
    database for example.
    
    The general settings `AWS_REGION`
    can be overriden with the `region` and so as the bucket

    `object_path` should be the relative path of the object
    in the bucket such as `folder/object.ext` or `folder/folder/object.ext`

    Example link
    ------------

        https://s3.eu-west-3.amazonaws.com/jobswebsite/banners/object.jpg
    """
    return f'https://s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{settings.AWS_STORAGE_BUCKET_NAME}/{object_path}'

def unique_entry_for(n=20):
    return secrets.token_hex(n)

def unique_path_creator(folder, filename, rename=False):
    """
    Create a unique path for an object to be stored
    in an AWS bucket. Returns a dictionnary with the
    object's new name, path and url.

    Parameters
    ----------

    `folder` is the folder to access within the bucket. You can
    also use a path such as path/to/

    `filename` is the name of the file

    `rename` allows you to rename the file to a random name

    Description
    -----------

        {
            'object_name': ['name', ('image/jpeg', None)], 
            'object_path': 'path/to/file.jpg',
            'object_url': 'https://s3...',
            'unique_entry': 'acc318515f364f1d37ecac456e6365bc1e4ae216'
        }

        unique_entry is the unique folder created in order to identify a set
        of files in your bucket
    """
    name, extension = filename.split('.', 1)

    unique_entry = unique_entry_for()

    if rename:
        name = secrets.token_hex(10)
        extension = extension.lower()
    
    else:
        name = name.lower()
        extension = extension.lower()

    object_path = '%s/%s/%s.%s' % (folder, unique_entry, name, extension)
    # Create the objet's URL to save to a database for example
    # FIXME: Find a way to pass the bucket and the region
    object_url = aws_url_for(object_path)
    
    return {'object_name': [name, guess_type(filename)], 'object_path': object_path, 
                'object_url': object_url, 'unique_entry': unique_entry}


# class AWS:
#     session = boto3.Session

#     def create_session(self, access_key, secret_key, region_name):
#         session = self.session(access_key, secret_key, region_name=region_name)
#         return session

# class QueryManager(AWS):
#     def __init__(self, bucket_name, access_key, secret_key, region_name):
#         # Use .resource() to perform actions from a
#         # bucket standpoint eg. .filter(), .all()
#         session = super().create_session(access_key, secret_key, region_name)
#         self.resource = session.resource('s3')
#         self.bucket = self.resource.Bucket(bucket_name)

#         self.bucket_name = bucket_name
#         self.region_name = region_name

#     def list_bucket(self):
#         """Lists the items withing a bucket
#         """
#         return [item for item in self.bucket.objects.all()]

#     def list_folder(self, folder):
#         """List the specific items of a folder

#         Description
#         -----------

#             For example, return the folder ./test in a bucket:

#                 (
#                     ('test/', 'item'), 
#                     ('test/subfolder/to.jpg', 'item'), 
#                     ...
#                 )
#         """
#         items = list((item.key, item.last_modified) for item in self.bucket.objects.filter(Prefix=folder))
#         items.pop(0)
#         return items

#     def list_folder_urls(self, folder):
#         """Get the specific items' links in a folder

#         Description
#         -----------

#             [
#                 https://s3...,
#                 ...
#             ]
#         """
#         items = self.list_folder(folder)
#         for item in items:
#             yield aws_url_for(item[0], self.region_name, self.bucket_name)

#     def delete_object(self, aws_path, request=None):
#         """Deletes an object from the bucket"""
#         obj = self.resource.Object(self.bucket_name, aws_path)
#         try:
#             obj.delete()
#         except boto3.exceptions.Boto3Error as e:
#             print(e.args)
#             return False
#         else:
#             print('Item deleted.')
#             return True


# class TransferManager(AWS):
#     def __init__(self, bucket_name, access_key, secret_key, region_name):
#         session = super().session(access_key, secret_key, region_name=region_name)
#         self.client = session.client('s3')
        
#         self.bucket_name = bucket_name
#         self.region_name = region_name

#     def upload(self, data, subfolder_path, contenttype, request=None, **params):
#         """This is the overall definition used to upload objects to
#         a given AWS bucket.

#         Parameters
#         ----------
#             data: the content of the file to upload in bytes

#             subfolder_path: is the subfolder to upload the file to

#             contenttype: the content disposition of the file e.g. application/jpg
#         """
#         base_params = {
#             'Bucket': self.bucket_name,
#             'Key': subfolder_path,
#             'Body': data,
#             'ACL': 'public-read',
#             'ContentType': contenttype,
#             'CacheControl': '86400'
#         }
#         if params:
#             base_params.update(params)

#         try:
#             response = self.client.put_object(**base_params)
#         except boto3.exceptions.S3TransferFailedError:
#             print('The file could not be uploaded to Amazon S3.')
#             return False
#         else:
#             print('File uploaded.')
#             return response
    
#     def upload_from_local(self, file_to_upload, upload_to):
#         """Uploads a file from a local path creating a unique
#         folder key within the AWS folder

#         Parameters
#         ----------

#             file_to_upload: the absolute path of the file to upload

#             upload_to: path in your AWS bucket in which to upload the file
#             e.g. path/to/folder

#             model: if you need to save items to a Django model after upload,
#             then pass your model here

#         Result
#         ------

#             Returns the key of the newly created folder
#         """
#         result = self._check_file(file_to_upload)
#         if result:
#             with open(file_to_upload, 'rb') as f:
#                 data = f.read()
#                 path = unique_path_creator(upload_to, result[0])
#                 self.upload(data, path['object_path'], result[1])
#             return path['unique_entry']
#         return False

#     def local_to_existing(self, file_to_upload, aws_path, unique_folder_key=None):
#         """
#         Upload a local file to an existing folder in AWS.
        
#         NOTE: the definition automatically guesses the name of the file.
#         """
#         result = self._check_file(file_to_upload)
#         if result:
#             with open(file_to_upload, 'rb') as f:
#                 data = f.read()

#                 if unique_folder_key:
#                     complete_path = f'{aws_path}/{unique_folder_key}/{result[0]}'
#                 else:
#                     complete_path = aws_path
                
#                 self.upload(data, complete_path, result[1])
#             return True
#         return False

#     def upload_multiple_to_new(self, local_folder_path, upload_to):
#         """
#         Uploads multiple local files to an AWS bucket

#         Parameters
#         ----------

#             local_folder_path: path of the local folder 
#             containing the files to upload

#             transfer_to: AWS folder to upload to
#         """
#         items = os.listdir(local_folder_path)
#         items_path = [os.path.join(local_folder_path, item) for item in items]
#         # Transfer a first object to create
#         # the folder and then proceeed with
#         # transfering the rest of the items
#         unique_key = self.upload_from_local(items_path.pop(0), upload_to)
#         newly_created_folder_path = f'{upload_to}/{unique_key}'
#         for path in items_path:
#             result = self._check_file(path)
#             if result:
#                 with open(path, 'rb') as f:
#                     data = f.read()
#                     aws_full_path = f'{newly_created_folder_path}/{result[0]}'
#                     self.upload(data, aws_full_path, result[1])
#         return True
        
#     def upload_multiple_to_existing(self, folder_path, aws_path, unique_folder_key=None):
#         items = os.listdir(folder_path)
#         for item in items:
#             local_path = os.path.join(folder_path, item)
#             result = self._check_file(local_path)
#             if result:
#                 with open(local_path, 'rb') as f:
#                     data = f.read()
#                     if unique_folder_key:
#                         complete_path = f'{aws_path}/{unique_folder_key}/{result[0]}'

#                     self.upload(data, complete_path, result[1])

#     @staticmethod
#     def _check_file(file_to_upload):
#         """
#         Checks that the file is a local file and returns
#         an array: [file_name, contentype].
#         """
#         is_local_file = os.path.isfile(file_to_upload)
#         if is_local_file:
#             item_name = os.path.basename(file_to_upload)
#             # Guess the type of the file for AWS
#             # Transform to list to have better flexibility
#             # as opposed to using a tuple
#             contenttype = guess_type(file_to_upload)[0]

#             # HACK: If content type is none, we
#             # have to find something here!
#             if not contenttype:
#                 contenttype = 'image/jpeg'
#             return [item_name, contenttype]
#         print(f'File is not on a valid path: {file_to_upload}')
#         return False

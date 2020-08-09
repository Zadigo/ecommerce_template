from urllib.parse import urljoin

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

register = template.Library()


def get_folder_url(path=None):
    try:
        aws_url = settings.AWS_IMAGES_FOLDER
    except AttributeError:
        raise ImproperlyConfigured(('In order to use the aws_images templatetag, '
                                    'you should provide an AWS_IMAGES_FOLDER settings variable that points to the AWS '
                                    'folder you want to get the AWS image url from.'))
    else:
        return aws_url


def iterator(base, images: list):
    normalized_images = []
    for image in images:
        normalized_images.append(urljoin(base, image.strip()))
    return normalized_images


@register.simple_tag
def create_aws_image_url(image_name, path=None):
    """Gets an image from an AWS folder
    
    Parameters
    ----------

        path: is the image path starting from the root url that
        was provided.
        
        For example if the root path is: https://aws.myfolder.com/ 
        and path is hero/images then the final path will be
        https://aws.myfolder.com/hero/images/image.jpg
    """
    return urljoin(get_folder_url(path=path), image_name)


@register.simple_tag
def create_aws_image_urls(*image_names, path=None):
    return {'urls': iterator(get_folder_url(path=path), image_names)}

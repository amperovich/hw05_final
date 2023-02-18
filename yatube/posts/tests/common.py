import secrets

from django.core.files.uploadedfile import SimpleUploadedFile


def image(name: str = 'test_image.jpg') -> SimpleUploadedFile:
    return SimpleUploadedFile(
        name=name,
        content=secrets.token_bytes(600 * 300),
        content_type='image/jpeg',
    )

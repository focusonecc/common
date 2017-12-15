import os
from django.core.exceptions import ValidationError

valid_image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
valid_audio_extensions = ['.mp3', '.wav']
valid_video_extensions = ['.mp4', '.rmbv']


def validate_file_extension(value, valid_extensions=None):
    valid_extensions = valid_extensions or []
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported audio file extension.')


def validate_image_extensions(value, valid_extensions=valid_image_extensions):
    return validate_file_extension(value, valid_extensions=valid_extensions)


def validate_audio_extensions(value, valid_extensions=valid_audio_extensions):
    return validate_file_extension(value, valid_extensions=valid_extensions)


def validate_video_extensions(value, valid_extensions=valid_video_extensions):
    return validate_file_extension(value, valid_extensions=valid_extensions)

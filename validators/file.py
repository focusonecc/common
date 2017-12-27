import os
from django.core.exceptions import ValidationError

valid_image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
valid_audio_extensions = ['.mp3', '.wav', '.aac', '.ac3', '.aiff',
                          '.m4a', '.mp2', '.ogg', '.ra', '.au', '.wma',
                          '.mka', '.flac', '.3gp', '.aa', '.rm', '.webm']

valid_video_extensions = ['.mp4', '.rmbv', '.mkv', '.webm', '.flv', '.vob',
                          '.ogv', '.ogg', '.drc', '.gif', '.gifv', '.mng',
                          '.avi', '.mov', '.wmv', '.yuv', '.qt', '.rm', '.asf',
                          '.amv', '.m4p', '.m4v', '.mpg', '.mp2', '.mpeg',
                          '.mpv', '.m2v', '.3gp']


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

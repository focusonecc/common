# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-09-08 10:55:04
# @Last Modified by:   theo-l
# @Last Modified time: 2017-12-15 15:40:43

import json
from django.db import models
from django.db.models.fields.files import (ImageField, ImageFieldFile, FileField)
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import DateField, URLField, DateTimeField, UUIDField

from common.utils import gen_uuid, get_absolute_url_path, datetime2timestamp
from .settings import MODEL_COMMON_FIELDS


class EnabledObjectsManager(models.Manager):

    def get_queryset(self):
        return super(EnabledObjectsManager, self).get_queryset().filter(enabled=True)


class AllObjectsManager(models.Manager):

    def get_queryset(self):
        return super(AllObjectsManager, self).get_queryset()


class BaseModel(models.Model):
    object_id = models.UUIDField(primary_key=True, default=gen_uuid, editable=False)
    created_at = models.DateTimeField(editable=False, auto_now_add=True, null=True, verbose_name='Creation time')
    updated_at = models.DateTimeField(editable=False, auto_now=True, null=True, verbose_name='Last update time')
    enabled = models.BooleanField(default=True, verbose_name='Is active?')
    priority = models.IntegerField(default=1)

    objects = AllObjectsManager()
    enables = EnabledObjectsManager()

    class Meta:
        abstract = True

    @property
    def id(self):
        return self.pk

    @property
    def isEnabled(self):
        return self.enabled

    def delete(self, using=None, keep_paraents=False):
        """
        Override delete method to set 'enabled=False' to immulate a delete action
        """
        self.enabled = False
        self.save()

    def to_dict(self, dehydrate_fields=None, excludes=None, json_fields=None, exclude_common=True):
        """
        Deserialize model object to simple dict object
        """
        dehydrate_fields = dehydrate_fields or []
        excludes = excludes or []
        if exclude_common:
            excludes.extend(MODEL_COMMON_FIELDS)
        json_fields = json_fields or []
        data = {}
        for field in self._meta.fields:
            field_name = field.name
            if field_name in excludes:
                continue
            field_value = getattr(self, field_name)

            if not field_value:
                data[field_name] = None
                continue

            if field_name in json_fields:
                data[field_name] = json.loads(field_value)
                continue

            if isinstance(field, (ImageField, ImageFieldFile, FileField)):
                data[field_name] = get_absolute_url_path(field_value.url)
                continue

            if isinstance(field, ForeignKey):
                data[field_name] = field_value.to_dict() if field_name in dehydrate_fields else str(getattr(self, '{}_id'.format(field_name)))
                continue

            if isinstance(field, (DateField, DateTimeField)):
                data[field_name] = datetime2timestamp(field_value)
                continue

            if isinstance(field, (UUIDField,)):
                data[field_name] = str(field_value)
                continue

            if isinstance(field, URLField):
                data[field_name] = get_absolute_url_path(field_value)
                continue

            data[field_name] = field_value
        return data

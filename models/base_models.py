# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-06-26 18:50:30
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-08 20:44:50

from django.db import models

from common.utils import gen_uuid


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

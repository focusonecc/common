# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-06-26 18:50:30
# @Last Modified by:   theo-l
# @Last Modified time: 2017-06-26 18:50:30

from django.db import models


class EnabledObjectsManager(models.Manager):
    def get_queryset(self):
        return super(EnabledObjectsManager, self).get_queryset().filter(enabled=True)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return super(AllObjectsManager, self).get_queryset()



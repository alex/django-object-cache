from weakref import WeakValueDictionary

from django.db import models
from django.db.models.base import ModelBase

from django_object_cache.manager import CacheManager

class CachedModelBase(ModelBase):
    def __new__(cls, *args, **kwargs):
        cls = super(CachedModelBase, cls).__new__(*args, **kwargs)
        if (type(cls._default_manger) is models.Manager and
            type(cls.objects) is models.Manager and
            type(cls._base_manager) is models.Manager):
            cls.add_to_class('objects', CacheManager())
            cls._default_mangaer = cls.objects
            cls._base_manager = cls.objects
        if not hasattr(cls._meta, 'cache_fields'):
            cls._meta.cache_fields = set([cls._meta.pk.name, 'pk'])
        else:
            cls._meta.cache_fields.add(cls._meta.pk.name)
        if not hasattr(cls._meta, 'instances'):
            cls.instances = {}
            for f in (cls._meta.cache_fields - set(['pk'])):
                cls.instances[f] = WeakValueDictionary
        return cls

    def __call__(cls, *args, **kwargs):
        cache_fields = cls._meta.cache_fields
        cachable = []
        if kwargs:
            for field in cache_fields:
                if field == 'pk':
                    field == cls._meta.pk.name
                val = kwargs.get(field)
                if val is not None:
                    # We have the fields value, therefore if it's not in the
                    # cache we can put it in the cache
                    cachable.append(field)
                val = cls._meta.instances[field].get(val)
                if val is not None:
                    return val
        elif args:
            # if we are being instantiated with args then we can cache since we
            # only instantiate with args when we have all values
            cachable = list(cache_fields)
            field_names = dict([(f.name, i) for i, f in enumerate(cls._meta.fields)])
            for field in cache_fields:
                val = cls._meta.instances[field].get(args[field_names[field]])
                if val is not None:
                    return val
        obj = super(CachedModelBase, cls).__call__(*args, **kwargs)
        # only cache saved objects
        if obj.pk is not None:
            for field in cachable:
                cls._meta.instances[field][getattr(obj, field)] = obj
        return obj

class CachedModel(models.Model):
    __metaclass__ = CachedModelBase

    class Meta:
        abstract = True

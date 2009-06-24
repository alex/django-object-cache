from django.core.cache import cache
from django.db.models.query import QuerySet

from django_object_cache.util import cache_key_for_obj

class CacheQuerySet(QuerySet):
    def iterator(self):
        iterator = super(CacheQuerySet, self).iterator()
        for obj in iterator:
            obj = self.model._cache_obj(obj)
            yield obj

    def get(self, *args, **kwargs):
        sup = lambda: super(CacheQuerySet, args).get(*args, **kwargs)
        if args or self.query.where or len(kwargs) != 1:
            # parsing out the items from args is too much of a pain.  If the
            # Query is already filtered we don't want to interfere.  Lastly we
            # don't work if there is more than one filter.
            return sup()
        key, val = kwargs.iteritems().next()
        key = key.strip('__exact')
        if key == 'pk':
            key = self.model._meta.pk.name
        cache_fields = self.model._meta.cache_fields
        if key not in cache_fields:
            return sup()
        obj = self.model._meta.instances[key].get(val)
        if obj is not None:
            return obj
        cache_key = cache_key_for_obj(self.model, key, val)
        obj = cache.get(cache_key)
        if obj is not None:
            self.model._meta.instances[key][val] = obj
            return obj
        obj = sup()
        self.model._meta.instances[key][val] = obj
        cache.set(cache_key, obj)
        return obj

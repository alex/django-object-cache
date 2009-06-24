from django.db.models import Manager

from django_object_cache.query import CacheQuerySet

class CacheManager(Manager):
    def get_query_set(self):
        return CacheQuerySet(self.model)

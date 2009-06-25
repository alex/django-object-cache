from django.db.models import Manager

from django_object_cache.query import CacheQuerySet

class CacheManager(Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return CacheQuerySet(self.model)

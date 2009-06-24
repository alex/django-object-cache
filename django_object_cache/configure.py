class CacheConfigure(object):
    def __init__(self, *args):
        """
        *args is a list of fields to cache.
        """
        self.fields = set(args)
        self.fields.add('pk')

    def contribute_to_class(self, model, name):
        self.model._meta.cache_fields = self.fields

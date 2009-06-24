from django.utils.hashcompat import sha_constructor

def cache_key_for_obj(klass, field, val):
    val = ":".join((klass._meta.app_label, klass._meta.object_name, field, val))
    if len(val) > 250:
        val = sha_constructor(val).hexdigest()
    return val

try:
    from django.utils import simplejson

except ImportError:
    import simplejson


def get_value(obj, attr):
    """ Gets a nested attribute from an object.

    >>> class Product(object):
    >>>     def __init__(self, *args, **kwargs):
    >>>         self.category = kwargs.get('category', None)
    >>>         self.name = kwargs.get('name', None)
    >>>
    >>> class Category(object):
    >>>     def __init__(self, *args, **kwargs):
    >>>         self.name = kwargs.get('name', None)
    >>>
    >>> category = Category(name='Laptops')
    >>> product = Product(name='MacBook Pro', category=category)
    >>> value = get_value(product, 'category.name')
    >>> assert product.category.name == 'Laptops'
    >>> assert value == 'Laptops'

    """

    for a in attr.split('.'):
        if hasattr(obj, a):
            get = obj.__getattribute__ if hasattr(obj, '__getattribute__') \
                    else obj.__getattr__
            obj = get(a)
        else:
            obj = None
            break
    return obj


def to_dict(obj, fields=None):
    """ Converts objects to dicts

    This code allows you to take a nested object and flatten it,
    or to construct a new dict containing only the properties
    or child dicts that you specify.

    >>> class Person(object):
    >>>     def __init__(self, *args, **kwargs):
    >>>         self.manager = kwargs.get('manager', None)
    >>>         self.name = kwargs.get('name', None)
    >>>
    >>> ceo = Person(name='Bill')
    >>> manager = Person(name='Sue', manager=ceo)
    >>> employee = Person(name='Christian', manager=manager)
    >>> obj = to_dict(employee, fields=['name',
    >>>                                 ('manager.manager.name', 'ceo_name'),
    >>>                                 {'manager': ['name',]}])
    >>> assert obj['name'] == 'Christian Toivola'
    >>> assert obj['manager']['name']

    """

    # If fields is not set, just use all fields.
    if fields == None:
        fields = obj._meta.get_all_field_names() if hasattr(obj, '_meta') else []

    data = {}

    for field in fields:
        if type(field) == type('') and hasattr(obj, field):
            data[field] = get_value(obj, field)

        if type(field) == type(()) and \
                len(field) == 2 and \
                hasattr(obj, field[0].split('.')[0]):
            data[field[1]] = get_value(obj, field[0])

        if type(field) == type({}):
            for key in field.keys():
                if hasattr(obj, key.split('.')[0]):
                    key_fields = field[key]
                    nested_obj = get_value(obj, key)
                    data[key] = to_dict(nested_obj, key_fields)
    return data


def to_json(obj, fields=None):
    """
    Serializes an object to json and includes
    only the fields that you specify.
    """
    data = to_dict(obj, fields=fields)
    return simplejson.dumps(data)

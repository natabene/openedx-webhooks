from __future__ import print_function, unicode_literals

import functools
import requests
from urlobject import URLObject


def pop_dict_id(d):
    id = d["id"]
    del d["id"]
    return (id, d)


def paginated_get(url, session=None, limit=None, per_page=100, **kwargs):
    """
    Retrieve all objects from a paginated API.

    Assumes that the pagination is specified in the "link" header, like
    Github's v3 API.

    The `limit` describes how many results you'd like returned.  You might get
    more than this, but you won't make more requests to the server once this
    limit has been exceeded.  For example, paginating by 100, if you set a
    limit of 250, three requests will be made, and you'll get 300 objects.

    """
    url = URLObject(url).set_query_param('per_page', str(per_page))
    limit = limit or 999999999
    session = session or requests.Session()
    returned = 0
    while url:
        resp = session.get(url, **kwargs)
        result = resp.json()
        if not resp.ok:
            raise requests.exceptions.RequestException(result["message"])
        for item in result:
            yield item
            returned += 1
        url = None
        if resp.links and returned < limit:
            url = resp.links.get("next", {}).get("url", "")


def memoize(func):
    cache = {}

    def mk_key(*args, **kwargs):
        return (tuple(args), tuple(sorted(kwargs.items())))

    @functools.wraps(func)
    def memoized(*args, **kwargs):
        key = memoized.mk_key(*args, **kwargs)
        try:
            return cache[key]
        except KeyError:
            cache[key] = func(*args, **kwargs)
            return cache[key]

    memoized.mk_key = mk_key

    def uncache(*args, **kwargs):
        key = memoized.mk_key(*args, **kwargs)
        if key in cache:
            del cache[key]
            return True
        else:
            return False

    memoized.uncache = uncache

    return memoized


def memoize_except(values):
    """
    Just like normal `memoize`, but don't cache when the function returns
    certain values. For example, you could use this to make a function not
    cache `None`.
    """
    if not isinstance(values, (list, tuple)):
        values = (values,)

    def decorator(func):
        cache = {}

        def mk_key(*args, **kwargs):
            return (tuple(args), tuple(sorted(kwargs.items())))

        @functools.wraps(func)
        def memoized(*args, **kwargs):
            key = memoized.mk_key(*args, **kwargs)
            try:
                return cache[key]
            except KeyError:
                value = func(*args, **kwargs)
                if not value in values:
                    cache[key] = value
                return value

        memoized.mk_key = mk_key

        def uncache(*args, **kwargs):
            key = memoized.mk_key(*args, **kwargs)
            if key in cache:
                del cache[key]
                return True
            else:
                return False

        memoized.uncache = uncache

        return memoized

    return decorator

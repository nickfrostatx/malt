from .helpers import izip, want_bytes, want_text
import base64
import hashlib
import hmac
import json


def b64e_raw(data):
    return want_text(base64.urlsafe_b64encode(data).rstrip(b'='))


def b64d_raw(data):
    data += u'=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(want_bytes(data))


def _constant_time_compare(a, b):
    """Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.

    For the sake of simplicity, this function executes in constant time only
    when the two strings have the same length. It short-circuits when they
    have different lengths.

    This is an alias of :func:`hmac.compare_digest` on Python>=2.7,3.3.
    """
    a = want_bytes(a)
    b = want_bytes(b)
    if len(a) != len(b):
        return False
    result = 0
    for x, y in izip(bytearray(a), bytearray(b)):
        result |= x ^ y
    return result == 0


def safe_str_cmp(a, b):
    a = want_bytes(a)
    b = want_bytes(b)
    return getattr(hmac, 'compare_digest', _constant_time_compare)(a, b)


def get_hmac(key, data):
    k = hmac.new(key, b'malt-session', hashlib.sha256).digest()
    sig = hmac.new(k, data, hashlib.sha256).digest()
    return b64e_raw(sig)


def sign(key, data):
    return data + u'.' + get_hmac(key, want_bytes(data))


def unsign(key, data):
    if u'.' not in data:
        return None
    payload, sig = data.rsplit(u'.', 1)

    correct_sig = get_hmac(key, want_bytes(payload))
    if not safe_str_cmp(sig, correct_sig):
        return None

    return payload


def get_key(request):
    if 'SECRET_KEY' not in request.config:
        raise Exception("You must set config['SECRET_KEY'] to use sessions")
    return want_bytes(request.config['SECRET_KEY'])


def open_session(request):
    key = get_key(request)
    cookie_name = request.config.get('SESSION_COOKIE_NAME', 'session')
    session_cookie = request.cookies.get(cookie_name)

    if session_cookie is None:
        return {}

    encoded = unsign(key, session_cookie)
    if encoded is None:
        return {}
    else:
        return json.loads(want_text(b64d_raw(encoded)))


def save_session(request, response):
    # We want the JSON to be small, and consistent (keys in sorted order)
    as_json = json.dumps(request.session, separators=(',', ':'),
                         sort_keys=True)
    # Create the signed session cookie
    encoded = b64e_raw(want_bytes(as_json))
    session_cookie = sign(get_key(request), encoded)
    # Set the cookie
    cookie_name = request.config.get('SESSION_COOKIE_NAME', 'session')
    response.set_cookie(cookie_name, session_cookie)
    return response

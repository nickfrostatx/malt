from malt import Request, Response
from malt.sessions import b64d_raw, b64e_raw, safe_str_cmp, sign, unsign, \
                          get_key, open_session, save_session
import pytest


def test_b64d_raw():
    assert b64d_raw(u'') == b''
    assert b64d_raw(u'dGVzdA') == b'test'
    assert b64d_raw(u'dGVzdDE') == b'test1'
    assert b64d_raw(u'dGVzdDEy') == b'test12'


def test_b64e_raw():
    assert b64e_raw(b'') == u''
    assert b64e_raw(b'test') == u'dGVzdA'
    assert b64e_raw(b'test1') == u'dGVzdDE'
    assert b64e_raw(b'test12') == u'dGVzdDEy'


def test_contstant_time_compare():
    assert not safe_str_cmp(b'abc', b'ab')
    assert not safe_str_cmp(b'abc', b'xyz')
    assert safe_str_cmp(b'abc', b'abc')
    assert safe_str_cmp(u'abc', b'abc')
    assert safe_str_cmp(u'abc', u'abc')


def test_sign():
    assert (sign(b'key123', u'') ==
            u'.Mvb4L5BS5aUrDYhWuPN1sLoGHrtOtGEsnFDMe1YBDY4')
    assert (sign(b'key123', u'test') ==
            u'test.0rjJa1KuUdmZEuR6enCSJXlNQFeLOQtwUE0jZdM23Yw')
    assert (sign(b'key123', u'test.test') ==
            u'test.test.Xwq30zOy_agpvv990HyxMDGcJHy40-UF4RTJFn644zQ')


def test_unsign():
    assert unsign(b'key123',
                  u'.Mvb4L5BS5aUrDYhWuPN1sLoGHrtOtGEsnFDMe1YBDY4') == u''
    assert (unsign(b'key123',
                   u'test.0rjJa1KuUdmZEuR6enCSJXlNQFeLOQtwUE0jZdM23Yw') ==
            u'test')
    assert (unsign(b'key123',
                   u'test.test.Xwq30zOy_agpvv990HyxMDGcJHy40-UF4RTJFn644zQ') ==
            u'test.test')
    assert unsign(b'key123', u'test') is None
    assert unsign(b'key123', u'test.xyz') is None
    assert unsign(b'key123', u'test.test.xyz') is None


def test_get_key():
    with pytest.raises(Exception) as exc_info:
        get_key(Request({}, {}))
    assert (exc_info.value.args[0] == "You must set config['SECRET_KEY'] to "
                                      "use sessions")

    assert get_key(Request({}, config={'SECRET_KEY': b'abc'})) == b'abc'


def test_open_session():
    key = b'abc'

    good_sess = 'eyJhIjoxfQ.2XFQKMS-erhoKkSGsezDxFsim6YctUnzxaiiMP1wzFs'
    good_req = Request({'HTTP_COOKIE': 'session=' + good_sess},
                       {'SECRET_KEY': key})
    assert open_session(good_req) == {u'a': 1}

    for bad_sess in ('eyJhIjoxfQ.abc', 'eyJhIjoxfQ', ''):
        bad_req = Request({'HTTP_COOKIE': 'session=' + bad_sess},
                          {'SECRET_KEY': key})
        assert open_session(bad_req) == {}

    assert open_session(Request({}, {'SECRET_KEY': key})) == {}


def test_save_session():
    req = Request({}, {'SECRET_KEY': b'abc'})
    req.session = {u'a': 1}
    resp = Response()

    save_session(req, resp)
    expected = u'eyJhIjoxfQ.2XFQKMS-erhoKkSGsezDxFsim6YctUnzxaiiMP1wzFs'
    assert resp.headers['Set-Cookie'] == u'session=' + expected

import pytest
from time import time
from memobase.error import ServerError
from memobase.utils import string_to_uuid

CONFIG = """
language: zh
"""


def test_user_profile_curd_client(api_client):
    a = api_client
    u = a.add_user()
    print(u)
    ud = a.get_user(u)
    pid = ud.add_profile("test", "topic", "sub_topic")
    print(pid)
    ps = ud.profile()
    assert len(ps) == 1
    assert ps[0].content == "test"
    assert ps[0].topic == "topic"
    assert ps[0].sub_topic == "sub_topic"
    print(ud.update_profile(pid, "test2", "topic2", "sub_topic2"))
    ps = ud.profile()
    assert len(ps) == 1
    assert ps[0].content == "test2"
    assert ps[0].topic == "topic2"
    assert ps[0].sub_topic == "sub_topic2"
    print(ud.delete_profile(pid))
    ps = ud.profile()
    assert len(ps) == 0


def test_user_curd_client(api_client):
    a = api_client

    print(api_client.get_config())
    print(api_client.update_config(CONFIG))
    c = api_client.get_config()
    assert c == CONFIG

    u = a.add_user()
    print(u)
    ud = a.get_user(u)
    print(a.update_user(u, {"test": 111}))
    print("user", a.get_user(u).fields)
    print(a.delete_user(u))
    with pytest.raises(ServerError):
        a.get_user(u)

    new_uid = string_to_uuid(f"test{time()}")
    ud = a.get_or_create_user(new_uid)
    assert ud.user_id == new_uid

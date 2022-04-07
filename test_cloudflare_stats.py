""" testing things """

from cloudflare_stats import k2v


def test_k2v() -> None:
    """ basic test """

    testvalue = [{
        "key" : "thenewkey",
        "weirdvalue" : 12345,
    }]

    assert k2v(testvalue) == {
        "thenewkey" : testvalue[0]
    }

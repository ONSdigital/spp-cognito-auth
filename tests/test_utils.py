from spp_cognito_auth.utils import fix_url


def test_fix_url_http():
    assert fix_url("http://google.com") == "http://google.com"


def test_fix_url_https():
    assert fix_url("https://google.com") == "https://google.com"


def test_fix_url_no_scheme():
    assert fix_url("google.com") == "https://google.com"

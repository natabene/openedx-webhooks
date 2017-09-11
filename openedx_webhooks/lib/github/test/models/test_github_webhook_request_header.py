# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import pytest

from openedx_webhooks.lib.github.models import GithubWebHookRequestHeader


@pytest.fixture
def headers():
    headers = {
        'X-Github-Event': 'event',
        'X-Hub-Signature': 'signature',
    }
    return GithubWebHookRequestHeader(headers)


def test_event_type(headers):
    assert headers.event_type == 'event'


def test_signature(headers):
    assert headers.signature == 'signature'

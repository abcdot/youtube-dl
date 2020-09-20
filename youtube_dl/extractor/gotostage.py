# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import compat_str
from ..utils import (
    url_or_none,
    try_get)

import json


class GoToStageIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?gotostage\.com/channel/[a-z0-9]+/recording/(?P<id>[a-z0-9]+)/watch'
    _TESTS = [{
        'url': 'https://www.gotostage.com/channel/8901680603948959494/recording/60bb55548d434f21b9ce4f0e225c4895/watch',
        'md5': 'ca72ce990cdcd7a2bd152f7217e319a2',
        'info_dict': {
            'id': '60bb55548d434f21b9ce4f0e225c4895',
            'ext': 'mp4',
            'title': 'What is GoToStage?',
            'thumbnail': r're:^https?://.*\.jpg$',
            'duration': 93.924711
        }
    }, {
        'url': 'https://www.gotostage.com/channel/bacc3d3535b34bafacc3f4ef8d4df78a/recording/831e74cd3e0042be96defba627b6f676/watch?source=HOMEPAGE',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        metadata = self._download_json(
            'https://api.gotostage.com/contents?ids=%s' % video_id,
            video_id,
            note='Downloading video metadata',
            errnote='Unable to download video metadata')

        registration_data = {
            'product': try_get(metadata, lambda x: x[0]['product'], compat_str),
            'resourceType': try_get(metadata, lambda x: x[0]['contentType'], compat_str),
            'productReferenceKey': try_get(metadata, lambda x: x[0]['productRefKey'], compat_str),
            'firstName': 'foo',
            'lastName': 'bar',
            'email': 'foobar@example.com'}

        registration_response = self._download_json(
            'https://api-registrations.logmeininc.com/registrations',
            video_id,
            data=json.dumps(registration_data).encode(),
            expected_status=409,
            headers={'Content-Type': 'application/json'},
            note='Register user',
            errnote='Unable to register user')

        content_response = self._download_json(
            'https://api.gotostage.com/contents/%s/asset' % video_id,
            video_id,
            headers={'x-registrantkey': try_get(registration_response, lambda x: x['registrationKey'], compat_str)},
            note='Get download url',
            errnote='Unable to get download url')

        return {
            'id': video_id,
            'title': try_get(metadata, lambda x: x[0]['title'], compat_str),
            'url': try_get(content_response, lambda x: x['cdnLocation'], compat_str),
            'ext': 'mp4',
            'thumbnail': url_or_none(try_get(metadata, lambda x: x[0]['thumbnail']['location'])),
            'duration': try_get(metadata, lambda x: x[0]['duration'], float),
            'categories': [try_get(metadata, lambda x: x[0]['category'], compat_str)],
            'is_live': False}

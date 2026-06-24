import re

from .common import InfoExtractor
from ..utils import unified_timestamp


class DudeThatsContentBaseIE(InfoExtractor):
    MEDIADELIVERY_REFERER = {'Referer': 'https://iframe.mediadelivery.net/'}

    def parse_nuxt_jsonp(self, nuxt_jsonp_url, video_id, name):
        nuxt_jsonp = self._download_webpage(nuxt_jsonp_url, video_id, note=f'Downloading {name} __NUXT_JSONP__')
        return self._search_nuxt_data(nuxt_jsonp, video_id, '__NUXT_JSONP__')

    def video_meta(self, video_id, title, release_date):
        timestamp = unified_timestamp(release_date)
        return {
            'id': video_id,
            'title': title,
            'http_headers': self.MEDIADELIVERY_REFERER,
            'uploader': 'DudeThatsLewd',
            'creator': 'DudeThatsLewd',
            'release_timestamp': timestamp,
            'timestamp': timestamp,
            'uploader_id': 'DudeThatsLewd',
            'uploader_url': 'https://www.patreon.com/c/DudeTL/posts',
            'was_live': True,
            'availability': 'public',
            # 'series': game_name,
            # 'season': category_name,
            # 'episode_number': episode_number,
        }


class DudeThatsContentIE(DudeThatsContentBaseIE):
    _VALID_URL = r'https?://(?:www\.)?dudethatscontent\.com/helper-tier/(?P<id>[0-9]+)/?'
    _TESTS = [
        {
            'url': 'https://dudethatscontent.com/helper-tier/1091',
            # Posts are gated behind the creator's Patreon tier; running this requires --cookies.
            'skip': 'Requires Patreon authentication',
            'info_dict': {
                'id': '1091',
                'ext': 'mp4',
                'title': '2024.01_Patreon_IRL_Video',
                'thumbnail': r're:^https?://.*\.b-cdn\.net/[a-f0-9\-]+/thumbnail\.jpg$',
                'uploader': 'DudeThatsLewd',
                'creator': 'DudeThatsLewd',
                'uploader_id': 'DudeThatsLewd',
                'uploader_url': 'https://www.patreon.com/c/DudeTL/posts',
                'duration': 615,
                'was_live': True,
                'availability': 'public',
            },
            'params': {'skip_download': True},
        },
    ]

    def _extract_bunnycdn_iframe(self, video_id, bunnycdn_url):
        iframe = self._download_webpage(
            bunnycdn_url.replace('&amp;', '&'),
            video_id, note='Downloading BunnyCDN iframe', headers={'Referer': 'https://dudethatscontent.com/', 'Sec-Fetch-Dest': 'iframe'})

        # activate_url = self._search_regex(r'(https?://video-\d{4}\.mediadelivery\.net/\.drm/[a-zA-Z0-9_\-=+]+/activate)', iframe, 'activate url')
        # activation_resp = self._download_webpage(activate_url, video_id, note=f'Activating', headers={'Referer': "https://iframe.mediadelivery.net/"})

        # m3u8_url = self._search_regex(r'(https?://iframe\.mediadelivery\.net/[a-f0-9\-]+/playlist\.drm\?contextId=[a-zA-Z0-9_\-=+]+&secret=[a-f0-9\-]+)', iframe, 'm3u8 url')
        # https://vz-68a79baa-451.b-cdn.net/b6350115-5b03-4402-b840-249d25232a75/playlist.m3u8
        m3u8_url = self._search_regex(r'(https?://.*?\.b-cdn\.net/[a-zA-Z0-9_\-=+]+/playlist.m3u8)', iframe, 'm3u8 url')
        # Thumbnail is optional metadata: don't let a missing/changed thumbnailUrl abort the whole
        # extraction. BunnyCDN serves the thumbnail under the same /<guid>/ path as the playlist,
        # so fall back to deriving it from the m3u8 URL.
        thumbnail_url = self._search_regex(
            r'"thumbnailUrl":\s*"(https://[^"]+?\.b-cdn\.net/[a-zA-Z0-9_\-=+]+/[^"]+?\.jpg)"',
            iframe, 'thumbnail url', fatal=False)
        if not thumbnail_url:
            thumbnail_url = re.sub(r'/playlist\.m3u8.*$', '/thumbnail.jpg', m3u8_url)

        m3u8_formats = self._extract_m3u8_formats(m3u8_url, video_id, headers=self.MEDIADELIVERY_REFERER)

        if not m3u8_formats:
            duration = None
        else:
            duration = self._extract_m3u8_vod_duration(
                m3u8_formats[0]['url'], video_id, headers=self.MEDIADELIVERY_REFERER)

        # Two iframe templates are in use: older ones embed JSON-LD ("name"/"uploadDate"), newer
        # ones put the title in a data-plyr-config blob ("title") and omit the upload date.
        title = self._search_regex(
            [r'"name":\s*"(.*?)\.mp4"', r'"title":\s*"(.*?)\.mp4"', r'"(?:name|title)":\s*"(.*?)"'],
            iframe, 'title', fatal=False) or video_id
        release_date = self._search_regex(
            r'"uploadDate":\s*"(.*?)"', iframe, 'release date', fatal=False)

        return {
            'formats': m3u8_formats,
            'thumbnail': thumbnail_url,
            'duration': duration,
            'http_headers': {'Referer': 'https://iframe.mediadelivery.net/'},
            **self.video_meta(
                video_id=video_id,
                title=title,
                release_date=release_date,
            ),
        }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        bunnyUrl = self._search_regex(r'(https://iframe\.mediadelivery\.net/embed/380576/[a-f0-9\-]+\?token=[a-f0-9]+(&|&amp;)expires=\d+)', webpage, 'bunnyId')
        return self._extract_bunnycdn_iframe(video_id, bunnyUrl)


class DudeThatsContentPlaylistIE(DudeThatsContentIE):
    _VALID_URL = r'https?://(?:www\.)?dudethatscontent\.com/index'
    _TESTS = [
        {
            'url': 'https://dudethatscontent.com/index',
            # The index is gated behind the creator's Patreon tier; running this requires --cookies.
            'skip': 'Requires Patreon authentication',
            'info_dict': {
                'id': 'index',
                'title': 'index',
            },
            'playlist_mincount': 1,
        },
    ]

    def _real_extract(self, url):
        playlist_id = 'index'
        webpage = self._download_webpage(url, playlist_id)

        # href="https://dudethatscontent.com/helper-tier/1117"
        page_urls = re.findall(r'href="(https://dudethatscontent.com/helper-tier/\d+)"', webpage)
        page_urls = sorted(set(page_urls))

        entries = [{
            **self.url_result(page, ie=DudeThatsContentIE.ie_key()),
        } for i, page in enumerate(page_urls)]

        return self.playlist_result(entries, playlist_id, playlist_id)

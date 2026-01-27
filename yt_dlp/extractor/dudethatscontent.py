import re

from .common import InfoExtractor
from ..utils import try_get, unified_timestamp


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
            #'series': game_name,
            #'season': category_name,
            #'episode_number': episode_number,
        }


class DudeThatsContentIE(DudeThatsContentBaseIE):
    _VALID_URL = r'https?://(?:www\.)?dudethatscontent\.com/helper-tier/(?P<id>[0-9]+)/?'
    _TESTS = [
        {
            'url': 'https://dudethatscontent.com/helper-tier/1117',
            'md5': 'bd012b04b261725510ca5383074cdd55',
            'info_dict': {
                'id': '1337',
                'ext': 'mp4',
                'title': 'The Witcher #13',
                'thumbnail': r're:^https?://.*\.b-cdn\.net/2f0cfbf4-3588-43a9-a7d6-7c9ea3755e67/thumbnail\.jpg$',
                'uploader': 'SovietWomble',
                'creator': 'SovietWomble',
                'release_timestamp': 1492091580,
                'release_date': '20170413',
                'timestamp': 1492091580,
                'upload_date': '20170413',
                'uploader_id': 'SovietWomble',
                'uploader_url': 'https://www.twitch.tv/SovietWomble',
                'duration': 7007,
                'was_live': True,
                'availability': 'public',
                'series': 'The Witcher',
                'season': 'Misc',
                'episode_number': 13,
                'episode': 'Episode 13',
            },
        },
        {
            'url': 'https://dudethatscontent.com/helper-tier/1115',
            'md5': '89fa928f183893cb65a0b7be846d8a90',
            'info_dict': {
                'id': '1105',
                'ext': 'mp4',
                'title': 'Arma 3 - Zeus Games #5',
                'uploader': 'SovietWomble',
                'thumbnail': r're:^https?://.*\.b-cdn\.net/c0e5e76f-3a93-40b4-bf01-12343c2eec5d/thumbnail\.jpg$',
                'creator': 'SovietWomble',
                'release_timestamp': 1461157200,
                'release_date': '20160420',
                'timestamp': 1461157200,
                'upload_date': '20160420',
                'uploader_id': 'SovietWomble',
                'uploader_url': 'https://www.twitch.tv/SovietWomble',
                'duration': 8804,
                'was_live': True,
                'availability': 'public',
                'series': 'Arma 3',
                'season': 'Zeus Games',
                'episode_number': 5,
                'episode': 'Episode 5',
            },
        },
    ]

    def _extract_bunnycdn_iframe(self, video_id, bunnycdn_url):
        iframe = self._download_webpage(
            bunnycdn_url.replace('&amp;', '&'),
            video_id, note='Downloading BunnyCDN iframe', headers={'Referer': 'https://dudethatscontent.com/', 'Sec-Fetch-Dest': 'iframe'})

        #activate_url = self._search_regex(r'(https?://video-\d{4}\.mediadelivery\.net/\.drm/[a-zA-Z0-9_\-=+]+/activate)', iframe, 'activate url')
        #activation_resp = self._download_webpage(activate_url, video_id, note=f'Activating', headers={'Referer': "https://iframe.mediadelivery.net/"})

        #m3u8_url = self._search_regex(r'(https?://iframe\.mediadelivery\.net/[a-f0-9\-]+/playlist\.drm\?contextId=[a-zA-Z0-9_\-=+]+&secret=[a-f0-9\-]+)', iframe, 'm3u8 url')
        # https://vz-68a79baa-451.b-cdn.net/b6350115-5b03-4402-b840-249d25232a75/playlist.m3u8
        m3u8_url = self._search_regex(r'(https?://.*?\.b-cdn\.net/[a-zA-Z0-9_\-=+]+/playlist.m3u8)', iframe, 'm3u8 url')
        thumbnail_url = self._search_regex(r'"thumbnailUrl": "(https://.*?\.b-cdn\.net/[a-zA-Z0-9_\-=+]+/thumbnail.*?\.jpg)",', iframe, 'thumbnail url')

        m3u8_formats = self._extract_m3u8_formats(m3u8_url, video_id, headers=self.MEDIADELIVERY_REFERER)

        if not m3u8_formats:
            duration = None
        else:
            duration = self._extract_m3u8_vod_duration(
                m3u8_formats[0]['url'], video_id, headers=self.MEDIADELIVERY_REFERER)
            

        title = self._search_regex(r'"name": "(.*?)\.mp4"', iframe, 'title')
        release_date = self._search_regex(r'"uploadDate": "(.*?)"', iframe, 'release date')

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
            'url': 'https://sovietscloset.com/The-Witcher',
            'info_dict': {
                'id': 'The-Witcher',
                'title': 'The Witcher',
            },
            'playlist_mincount': 31,
        },
        {
            'url': 'https://sovietscloset.com/Arma-3/Zeus-Games',
            'info_dict': {
                'id': 'Arma-3/Zeus-Games',
                'title': 'Arma 3 - Zeus Games',
            },
            'playlist_mincount': 3,
        },
        {
            'url': 'https://sovietscloset.com/arma-3/zeus-games/',
            'info_dict': {
                'id': 'arma-3/zeus-games',
                'title': 'Arma 3 - Zeus Games',
            },
            'playlist_mincount': 3,
        },
        {
            'url': 'https://sovietscloset.com/Total-War-Warhammer',
            'info_dict': {
                'id': 'Total-War-Warhammer',
                'title': 'Total War: Warhammer - Greenskins',
            },
            'playlist_mincount': 33,
        },
    ]

    def _real_extract(self, url):
        playlist_id = 'index'
        webpage = self._download_webpage(url, playlist_id)

        # href="https://dudethatscontent.com/helper-tier/1117"
        page_urls = re.findall(rf'href="(https://dudethatscontent.com/helper-tier/\d+)"', webpage)
        page_urls = sorted(set(page_urls))

        entries = [{
            **self.url_result(page, ie=DudeThatsContentIE.ie_key()),
        } for i, page in enumerate(page_urls)]

        return self.playlist_result(entries, playlist_id, playlist_id)

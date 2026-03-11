from .common import InfoExtractor
from ..utils import float_or_none, int_or_none, traverse_obj


class AudiochanIE(InfoExtractor):
    IE_NAME = 'audiochan'
    _VALID_URL = r'https?://(?:www\.)?audiochan\.com/a/(?P<id>[A-Za-z0-9]+)'
    _TEST = {
        'url': 'https://audiochan.com/a/GQY6V5C2DV0Sc6MvSc',
        'info_dict': {
            'id': '6f9b4fc8-82f2-4aad-a1af-c0af7247a6a9',
            'ext': 'mp3',
            'title': 'Mommy Needs To Breed You With Her Girlcock🥰🌸',
            'uploader': '🌸PinkVelvetKat🌸',
            'uploader_id': 'pinkvelvetkat',
        },
    }

    def _real_extract(self, url):
        slug = self._match_id(url)
        data = self._download_json(
            f'https://api.audiochan.com/audios/slug/{slug}', slug)

        audio_file = data['audioFile']
        key = audio_file['key']
        audio_url = f'https://content.audiochan.com/{key}'
        ext = key.rsplit('.', 1)[-1] if '.' in key else 'mp3'

        uploader = (traverse_obj(data, ('credits', 0, 'display_name'))
                    or traverse_obj(data, ('credits', 0, 'user', 'display_name')))
        uploader_id = traverse_obj(data, ('credits', 0, 'user', 'username'))

        return {
            'id': data['id'],
            'title': data['title'],
            'url': audio_url,
            'ext': ext,
            'duration': float_or_none(audio_file.get('duration')),
            'filesize': int_or_none(audio_file.get('filesize')),
            'thumbnail': data.get('creator_visual'),
            'uploader': uploader,
            'uploader_id': uploader_id,
            'tags': [t['name'] for t in data.get('tags', [])],
            'vcodec': 'none',
        }

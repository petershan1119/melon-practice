from bs4 import BeautifulSoup, NavigableString
from .utils.parsing import get_dict_from_dl
import requests


DOMAIN = 'https://www.melon.com'

__all__ = (
    'ArtistData',
)


def require_detail(f):
    def wrap(self, *args, **kwargs):
        if not self.detail:
            self.get_detail()
        return f(self, *args, **kwargs)

    return wrap


class ArtistData:
    def __init__(self, artist_id, name='', url_img_cover=''):
        self.artist_id = artist_id
        self.name = name
        self.real_name = None
        self.url_img_cover = url_img_cover
        self.detail = False
        self._info = {}
        self._award_history = []
        self._introduction = {}
        self._activity_information = {}
        self._personal_information = {}
        self._related_information = {}

    def __str__(self):
        if self.real_name:
            return f'{self.name} ({self.real_name})'
        return f'{self.name}'

    def __repr__(self):
        return self.__str__()

    def get_detail(self):
        url = f'{DOMAIN}/artist/detail.htm'
        params = {
            'artistId': self.artist_id,
        }
        response = requests.get(url, params)
        source = response.text
        soup = BeautifulSoup(source, 'lxml')
        info = soup.select_one('.wrap_atist_info')
        src = soup.select_one('.wrap_dtl_atist .wrap_thumb #artistImgArea img').get('src')

        # 일반 정보
        url_img_cover = src.rsplit('?', 1)[0]
        name = info.select_one('.title_atist').contents[1]
        real_name = name.next_sibling
        self.url_img_cover = url_img_cover
        self.name = name
        self.real_name = real_name
        self._info = get_dict_from_dl(info.select_one('dl'), first_text=True)

        # 상세정보 - 수상이력
        award_list = []
        award_dd_list = soup.select('.section_atistinfo01 dl > dd')
        for dd in award_dd_list:
            title, award = dd.get_text(strip=True).split('|')
            award_list.append(f'{title} ({award})')
        self._award_history = award_list

        # 상세정보 - 아티스트 소개
        div_intro = soup.select_one('.section_atistinfo02 #d_artist_intro')
        if div_intro:
            intro = ''
            for item in div_intro:
                if item.name == 'br':
                    intro += '\n'
                elif type(item) is NavigableString:
                    intro += item.strip()
            self._introduction = intro

        # 상세정보 - 활동정보
        dl_activity_information = soup.select_one('.section_atistinfo03 dl.list_define')
        if dl_activity_information:
            self._activity_information = get_dict_from_dl(dl_activity_information)

        # 상세정보 - 신상정보
        dl_personal_information = soup.select_one('.section_atistinfo04 dl')
        if dl_personal_information:
            self._personal_information = get_dict_from_dl(dl_personal_information)

        # 상세정보 - 연관정보
        dl_list_related_information = soup.select('.section_atistinfo05 dl')
        if dl_list_related_information:
            related_information_dict = {}
            for dl in dl_list_related_information:
                related_information_dict.update(get_dict_from_dl(dl))
            self._related_information = related_information_dict

        self.detail = True

    @require_detail
    def show_info(self):
        for key, value in self._info.items():
            print(f'{key}\n  {value}')

    @property
    @require_detail
    def info(self):
        return self._info

    @property
    @require_detail
    def award_history(self):
        return self._award_history

    @property
    @require_detail
    def introduction(self):
        return self._introduction

    @property
    @require_detail
    def activity_information(self):
        return self._activity_information

    @property
    @require_detail
    def personal_information(self):
        return self._personal_information

    @property
    @require_detail
    def related_information(self):
        return self._related_information
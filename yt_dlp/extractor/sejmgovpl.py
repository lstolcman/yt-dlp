# coding: utf-8

import re
import datetime

from .common import InfoExtractor
from ..utils import (
    sanitized_Request,
)
from ..compat import compat_etree_fromstring
from ..utils import HEADRequest


def parseDateTime(datetime_str):
    # based on dateTimeStringToNumber from https://www.sejm.gov.pl/Sejm9.nsf/video.js?open&ver=20211222
    date = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    date = date.replace(year=date.year-31)  # datetime calculates years from 1970, we calculate it from 2001
    return int(date.timestamp())*1000



class SejmGovPlIE(InfoExtractor):
    _VALID_URL = r'http(s)?://(?:www\.)?sejm\.gov\.pl/(s|S)ejm([0-9]+)\.nsf/transmisja\.xsp\?documentId\=(?P<id>[0-9A-F]+)'

    '''
    not supported yet:
    https://www.sejm.gov.pl/Sejm9.nsf/transmisje_arch.xsp?unid=C9EB0FEA9A446135C1258829004720F6
    ok:
    https://www.sejm.gov.pl/Sejm9.nsf/transmisja.xsp?documentId=24F31B5C5223CB9DC125883F002B5580&symbol=STENOGRAM_TRANSMISJA
    http://www.sejm.gov.pl/sejm7.nsf/transmisja.xsp?documentId=7C5F29646C5A06BEC1257E980045B068
    https://www.sejm.gov.pl/Sejm7.nsf/transmisja.xsp?documentId=D474BE52283D38B8C1257D4F002E2A2B&symbol=STENOGRAM_TRANSMISJA
    https://www.sejm.gov.pl/Sejm8.nsf/transmisja.xsp?documentId=03388A8171820F02C125844600284135&symbol=STENOGRAM_TRANSMISJA
    https://www.sejm.gov.pl/Sejm9.nsf/transmisja.xsp?documentId=E9F49F20EEA47D3AC125883F002B2D60&symbol=STENOGRAM_TRANSMISJA
    '''

    _TESTS = [{
        'url': 'https://www.sejm.gov.pl/Sejm8.nsf/transmisja.xsp?documentId=03388A8171820F02C125844600284135&symbol=STENOGRAM_TRANSMISJA',
        'info_dict': {
            'id': '03388A8171820F02C125844600284135',
            'ext': 'mp4',
            'title': '85. posiedzenie Sejmu VIII kadencji - retransmisja',
        }
    }, {
        'url': 'https://www.sejm.gov.pl/Sejm8.nsf/transmisja.xsp?documentId=B1AE0E42B4E31F91C125847100331CA8&symbol=STENOGRAM_TRANSMISJA',
        'only_matching': True,
    }, {
        'url': 'http://www.sejm.gov.pl/sejm7.nsf/transmisja.xsp?documentId=7C5F29646C5A06BEC1257E980045B068',
        'only_matching': True,
    }, {
        'url': 'http://sejm.gov.pl/sejm7.nsf/transmisja.xsp?documentId=7C5F29646C5A06BEC1257E980045B068&symbol=STENOGRAM_TRANSMISJA',
        'only_matching': True,
    }, {
        'url': 'https://www.sejm.gov.pl/sejm7.nsf/transmisja.xsp?documentId=7C5F29646C5A06BEC1257E980045B068&symbol=STENOGRAM_TRANSMISJA',
        'only_matching': True,
    }, {
        'url': 'https://www.sejm.gov.pl/sejm8.nsf/transmisja.xsp?documentId=EB37F5B8B617E550C12580880029FBC6&symbol=STENOGRAM_TRANSMISJA',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        '''
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        # TODO more code goes here, for example ...
        title = self._html_search_regex(r'<h1>(.+?)</h1>', webpage, 'title')

        return {
            'id': video_id,
            'title': title,
            'description': self._og_search_description(webpage),
            'uploader': self._search_regex(r'<div[^>]+id="uploader"[^>]*>([^<]+)<', webpage, 'uploader', fatal=False),
            # TODO more properties (see yt_dlp/extractor/common.py)
        }
        
        '''


        '''
        https://www.sejm.gov.pl/Sejm9.nsf/transmisja.xsp?documentId=24F31B5C5223CB9DC125883F002B5580&symbol=STENOGRAM_TRANSMISJA
        var IFRAME_SRC = "https://sejm-embed.redcdn.pl/Sejm9.nsf/";
        https://sejm-embed.redcdn.pl/Sejm9.nsf/
        https://sejm-embed.redcdn.pl/Sejm9.nsf/VideoFrame.xsp/24F31B5C5223CB9DC125883F002B5580
        https://sejm-embed.redcdn.pl/Sejm9.nsf/VideoFrame.xsp/24F31B5C5223CB9DC125883F002B5580


        https://sejm.atmitv.pl/sejm/GetMessagesHistory.do?format=json&since=1670922330000&till=1670971715000
        



        todo:
        - messages json ( szukaj 'ext': 'json',  w kodzie)
        - komisje, nie tylko posiedzenia
        - sprawdz sejm api - czy da sie cos wyciagnac
        https://sejm.atmitv.pl/sejm/GetMessagesHistory.do?format=json&since=1670922330000&till=1670971715000
        '''

        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        iframe_src = self._search_regex(r'var IFRAME_SRC = "(.*?)";', webpage, 'title')
        iframe_url = f"{iframe_src}VideoFrame.xsp/{video_id}"
        iframe_page = self._download_webpage(iframe_url, video_id)


        start = self._search_regex(r'"start":"(.*?)"', webpage, 'start')
        stop = self._search_regex(r'"stop":"(.*?)"', webpage, 'stop')
        file_base_url = self._search_regex(r'"file":"(.*?)"', webpage, 'file_base_url')
        title = self._search_regex(r'<title>(.*?)</title>', webpage, 'title')

        cameras = self._html_search_regex(r'var cameras = \[(.+)\];', iframe_page, 'cameras', flags=re.DOTALL)
        cameras_list = re.findall(r'flv: "(.*?)"', cameras)



        f2 = []
        for i in range(len(cameras_list)):
            file_base_url = cameras_list[i]



            # 'http:\\/\\/r.dcs.redcdn.pl\\/nvr\\/o2\\/sejm\\/ENC01\\/live.livx'
            # take first start date only (both are equal but doesn't matter...)
            start_date = start.split(' ')[0]

            # build an url based on informations from html source and js player...
            file_base_url = "https:" + file_base_url
            file_base_url = file_base_url.replace('\\', '')
            file_base_url = file_base_url.replace('nvr', 'livedash')

            url=f"{file_base_url}?indexMode=true&startTime={parseDateTime(start)}&stopTime={parseDateTime(stop)}"

            # extract actual transmission frame url, e.g.:
            # https://www.sejm.gov.pl/sejm8.nsf/transmisja.xsp?documentId=F11E0704B2C7BDF6C12584390028EFD9&symbol=STENOGRAM_TRANSMISJA
            # base transmission url:
            # https://r.dcs.redcdn.pl/webcache/sejm-embed/Sejm8.nsf/VideoFrame.xsp/F11E0704B2C7BDF6C12584390028EFD9
            # http 302 redirect to actual webpage url ->
            # https://n-22-6.dcs.redcdn.pl/webcache/sejm-embed/Sejm8.nsf/VideoFrame.xsp/F11E0704B2C7BDF6C12584390028EFD9

            # get the url to mpeg dash schema after redirect
            redirect_req = HEADRequest(url)
            req = self._request_webpage(redirect_req, video_id, note='Resolving final URL', errnote='Could not resolve final URL')
            url = req.geturl()

            request = sanitized_Request(url)
            # request.add_header('Accept-Encoding', '*')
            full_response = self._request_webpage(request, video_id)
            webpage = self._webpage_read_content(full_response, url, video_id)

            doc = compat_etree_fromstring(webpage.encode('utf-8'))
            
            formats = self._parse_mpd_formats(
                doc,
                # mpd_base_url=full_response.geturl().rpartition('/')[0],
                # mpd_url=url
            )
            # ownloading multifeed video (%s) - add --no-playlist to just download video %s'
            for elem in formats:
                elem_ = elem.copy()
                elem_['format_id'] = f"{i}-{elem['format_id']}"
                elem_['format_note'] = f"{elem_['format_note']}, camera {i}"
                elem_['source_preference'] = 1 if i==0 else 2
                f2.append(elem_)
        # for elem in formats:
        #     elem_ = elem.copy()
        #     elem_['format_id'] = f"cam2-{elem['format_id']}"
        #     f2.append(elem_)
        formats=f2
        info_dict = {
            'id': video_id,
            'title': f'{title} - {start_date}',
            'formats': formats,
            # see extractor/common.py
            # * format_note Additional info about the format
        }
        return info_dict

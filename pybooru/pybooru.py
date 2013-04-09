#!/usr/bin/env Python
#encoding: utf-8

"""
    Pybooru is a library for Python for access to API Danbooru based sites.
    Version: 1.4.9
    Under a MIT License
"""

__author__ = 'Daniel Luque <danielluque14 at gmail.com>'
__version__ = '1.4.9'


#urllib2 imports
from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import HTTPError

#urlparse imports
from urlparse import urlparse

try:
    #simplejson imports
    from simplejson import loads
except ImportError:
    try:
        #Python 2.6 and up
        from json import loads
    except ImportError:
        raise Exception('Pybooru requires the simplejson library to work')

#pyborru resources import
from resources import http_status_codes


class PybooruError(Exception):
    """
       Class for return error message
    """

    def __init__(self, err_msg, err_code=None, url=None):
        self.msg = err_msg
        self.code = err_code

        if (err_code is not None) and (err_code in http_status_codes) and (
            url is not None):
            self.msg = '%i: %s, %s -- %s -- URL: %s' % (err_code,
                        http_status_codes[err_code][0],
                        http_status_codes[err_code][1], self.msg, url)

    def __str__(self):
        """This function return self.err_msg"""

        return repr(self.msg)


class Pybooru(object):
    def __init__(self, name=None, siteURL=None):
        """
            Pybooru class

            Init parameters:
                    name: of the site name
                    siteURL: URL of Danbooru site
        """

        self.baseURL = ''

        if name is not None:
            self.name = str(name).lower()
            self._site_name(self.name)
        elif siteURL is not None:
            self.siteURL = str(siteURL).lower()
            self._url_validator(self.siteURL)
        else:
            print PybooruError('siteURL or name invalid')

    def _site_name(self, name):
        """Function for check name site and get URL"""

        self.site_list = {'konachan': 'http://konachan.com',
                          'danbooru': 'http://danbooru.donmai.us',
                          'yandere': 'https://yande.re',
                          'chan-sankaku': 'http://chan.sankakucomplex.com',
                          'idol-sankaku': 'http://idol.sankakucomplex.com',
                          '3dbooru': 'http://behoimi.org',
                          'nekobooru': 'http://nekobooru.net'}

        if name in self.site_list.keys():
            self.baseURL = self.site_list[name]
        else:
            print PybooruError('Site name is not valid')

    def _url_validator(self, url):
        """URL validator for siteURL parameter of Pybooru"""

        self.parse = urlparse(url)

        if (self.parse[0] != 'http' or 'https') or (url[-1] == '/'):
            if self.parse[0] != 'http' or 'https':
                self.url = 'http://' + self.parse[1] + self.parse[2] + \
                self.parse[3]
            if url[-1] == '/':
                self.url = self.url[:-1]

        self.baseURL = self.url

    def _build_url(self, api_url, params=None):
        """Builder url for _json_load"""

        if params is not None:
            self.url_request = self.baseURL + api_url + params
            self.url_request = self._json_load(self.url_request)
            return self.url_request
        else:
            self.url_request = self.baseURL + api_url
            self.url_request = self._json_load(self.url_request)
            return self.url_request

    def _json_load(self, url):
        """Function for read and return JSON response"""

        try:
            #urlopen() from module urllib2
            self.openURL = urlopen(url)
            self.reading = self.openURL.read()
            #loads() is a function of simplejson module
            self.response = loads(self.reading)
            return self.response
        except (URLError, HTTPError) as err:
            if hasattr(err, 'code'):
                raise PybooruError('in _json_load', err.code, url)
            else:
                raise PybooruError('in _json_load %s' % (err.reason), url)

    def posts(self, tags=None, limit=10, page=1):
        self.posts_url = '/post/index.json?'
        self.params = 'limit=%i&page=%i' % (limit, page)

        if tags is not None:
            self.tags = str(tags)
            self.params += '&tags=%s' % (tags)
            return self._build_url(self.posts_url, self.params)
        else:
            return self._build_url(self.posts_url, self.params)

    def tags(self, name=None, id_=None, limit=100, page=1, order='name',
                                                            after_id=0):
        self.tags_url = '/tag/index.json?'

        if id_ is not None:
            self.params = 'id=%i' % (id_)
            return self._build_url(self.tags_url, self.params)
        if name is not None:
            self.name = str(name)
            self.params = "name=%s" % (self.name)
            return self._build_url(self.tags_url, self.params)
        else:
            self.params = "limit=%i&page=%i&order=%s&after_id=%i" % (limit,
                                                    page, order, after_id)
            return self._build_url(self.tags_url, self.params)

    def artists(self, name=None, id_=None, limit=20, order='name', page=1):
        self.artists_url = '/artist/index.json?'
        self.params = 'limit=%i&page%i&order=%s' % (limit, page, order)

        if name is not None:
            self.name = str(name)
            self.params += '&name=%s' % (self.name)
            return self._build_url(self.artists_url, self.params)
        elif id_ is not None:
            self.params = 'id=%i' % (id_)
            return self._build_url(self.artists_url, self.params)
        else:
            return self._build_url(self.artists_url, self.params)

    def comments(self, id_=None):
        self.comments_url = '/comment/show.json?'

        if id_ is not None:
            self.params = 'id=%i' % (id_)
            return self._build_url(self.comments_url, self.params)
        else:
            print PybooruError('id_ attribute is empty')

    def wiki(self, query=None, order='title', limit=20, page=1):
        self.wiki_url = '/wiki/index.json?'
        self.params = 'order=%s&limit=%i&page=%i' % (order, limit, page)

        if query is not None:
            self.query = str(query)
            self.params += '&query=%s' % (self.query)
            return self._build_url(self.wiki_url, self.params)
        else:
            return self._build_url(self.wiki_url, self.params)

    def wiki_history(self, title=None):
        self.wiki_history_url = '/wiki/history.json?'

        if title is not None:
            self.title = str(title)
            self.params = 'title=%s' % (self.title)
            return self._build_url(self.wiki_history_url, self.params)
        else:
            PybooruError('title atribute is required')

    def notes(self, id_=None):
        self.notes_url = '/note/index.json?'

        if id_ is not None:
            self.params = 'post_id=%i' % (id_)
            return self._build_url(self.notes_url, self.params)
        else:
            return self._build_url(self.notes_url)

    def search_notes(self, query=None):
        self.search_notes_url = '/note/search.json?'

        if query is not None:
            self.query = str(query)
            self.params = 'query=%s' % (self.query)
            return self._build_url(self.search_notes_url, self.params)
        else:
            print PybooruError('query attribute is empty')

    def history_notes(self, post_id=None, id_=None, limit=10, page=1):
        self.history_notes_url = '/note/history.json?'

        if post_id is not None:
            self.params = 'post_id=%i' % (post_id)
            return self._build_url(self.history_notes_url, self.params)
        elif id_ is not None:
            self.params = 'id=%i' % (post_id)
            return self._build_url(self.history_notes_url, self.params)
        else:
            self.params = 'limit=%i&page=%i' % (limit, page)
            return self._build_url(self.history_notes_url, self.params)

    def users(self, name=None, id_=None):
        self.users_url = '/user/index.json?'

        if name is not None:
            self.name = str(name)
            self.params = 'name=%s' % (self.name)
            return self._build_url(self.users_url, self.params)
        elif id_ is not None:
            self.params = 'id=%i' % (self.id_)
            return self._build_url(self.users_url, self.params)
        else:
            return self._build_url(self.users_url)

    def forum(self, id_=None):
        self.forum_url = '/forum/index.json?'

        if id_ is not None:
            self.params = 'parent_id%i' % (id_)
            return self._build_url(self.forum_url, self.params)
        else:
            return self._build_url(self.forum_url)

    def pools(self, query=None, page=1):
        self.pools_url = '/pool/index.json?'

        if query is not None:
            self.query = str(query)
            self.params = 'query=%s' % (self.query)
            return self._build_url(self.pools_url, self.params)
        else:
            self.params = 'page=%i' % (page)
            return self._build_url(self.pools_url, self.params)

    def pools_posts(self, id_=None, page=1):
        self.pools_posts_url = '/pool/show.json?'

        if id_ is not None:
            self.params = 'id=%i&page=%i' % (id_, page)
            return self._build_url(self.pools_posts_url, self.params)
        else:
            print PybooruError('id_ attribute is empty')

    def favorites(self, id_=None):
        self.favorites = '/favorite/list_users.json?'

        if id_ is not None:
            self.params = 'id=%i' % (id_)
            return self._build_url(self.favorites, self.params)
        else:
            print PybooruError('id_ attribute is empty')

    def tag_history(self, post_id=None, user_id=None, user_name=None):
        self.tag_history_url = '/post_tag_history/index.json?'

        if post_id is not None:
            self.params = 'post_id=%i' % (post_id)
            return self._build_url(self.tag_history_url, self.params)
        if user_id is not None:
            self.params = 'user_id=%i' % (user_id)
            return self._build_url(self.tag_history_url, self.params)
        if user_name is not None:
            self.user_name = str(user_name)
            self.params = 'user_name=%s' % (self.user_name)
            return self._build_url(self.tag_history_url, self.params)


if __name__ == '__main__':
    print PybooruError('Import this module into your project to use')
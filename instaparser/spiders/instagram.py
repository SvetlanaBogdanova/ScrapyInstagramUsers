import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import UserParserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    login_link = 'https://www.instagram.com/accounts/login/ajax/'
    username = 'bubblegum_2022@mail.ru'
    pwd = '#PWD_INSTAGRAM_BROWSER:10:1638732268:ATlQAB/DTHjcDZSkFeN07VMum4NjU3RRPGnJSh0tK1THkFdK28ukHjKlE2TYL39vKIfsGhhXG0nHCFhjxmC5cmF9rZ1wlezCQXd1cKWKtxIi8I5Xj+6QFYo7Bm1uJMDV9+EnnpZDBHp9sx8P7qYa'
    users = ['__i.r.i.s.h.k.a__', 'misss_brunetka_']
    friendships_api_link = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.username,
                                           'enc_password': self.pwd},
                                 headers={'x-csrftoken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users:
                yield response.follow(
                    f'/{user}',
                    callback=self.start_parsing,
                    cb_kwargs={'username': user}
                )

    def start_parsing(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables_followers = {'count': 12, 'search_surface': 'follow_list_page'}
        url_followers = f'{self.friendships_api_link}{user_id}/followers/?{urlencode(variables_followers)}'

        yield response.follow(
            url_followers,
            callback=self.parse_followers,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables_followers)}
        )

        variables_following = {'count': 12}
        url_following = f'{self.friendships_api_link}{user_id}/following/?{urlencode(variables_following)}'

        yield response.follow(
            url_following,
            callback=self.parse_following,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables_following)}
        )

    def parse_followers(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        if 'next_max_id' in j_data:
            variables['max_id'] = j_data['next_max_id']
            url_followers = f'{self.friendships_api_link}{user_id}/followers/?{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.parse_followers,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        followers = j_data['users']
        for follower in followers:
            item = UserParserItem(
                target_user_id=user_id,
                target_username=username,
                relationship_type='follower',
                user_id=follower['pk'],
                username=follower['username'],
                full_name=follower['full_name'],
                is_private=follower['is_private'],
                profile_pic=follower['profile_pic_url'],
                user_data=follower
            )
            yield item

    def parse_following(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        if 'next_max_id' in j_data:
            variables['max_id'] = j_data['next_max_id']
            url_following = f'{self.friendships_api_link}{user_id}/following/?{urlencode(variables)}'

            yield response.follow(
                url_following,
                callback=self.parse_following,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        following_list = j_data['users']
        for following in following_list:
            item = UserParserItem(
                target_user_id=user_id,
                target_username=username,
                relationship_type='following',
                user_id=following['pk'],
                username=following['username'],
                full_name=following['full_name'],
                is_private=following['is_private'],
                profile_pic=following['profile_pic_url'],
                user_data=following
            )
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

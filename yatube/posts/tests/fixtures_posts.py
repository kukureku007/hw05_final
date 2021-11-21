from http import HTTPStatus


class FixturesData():
    TEST_GROUP_TITLE_1 = 'test-group1'
    TEST_GROUP_TITLE_2 = 'test-group2'
    TEST_GROUP_SLUG_1 = 'test-slug1'
    TEST_GROUP_SLUG_2 = 'test-slug2'
    TEST_GROUP_DESCRIPTION_1 = 'some description about testing group'
    TEST_GROUP_DESCRIPTION_2 = 'some 2 description about testing group'

    TEST_POST_TEXT_1 = 'POST1'
    TEST_POST_TEXT_2 = 'POST2'
    TEST_POST_WO_GROUP_TEXT = 'FDFSDFSDFSDFSD'
    TEST_POST_EDIT = 'EDITED INFOFO'

    AUTHOR_USERNAME_1 = 'SteveJ'
    AUTHOR_USERNAME_2 = 'SteveV'
    USER_USERNAME = 'SteveO'

    POST_TEXT = 'text'
    POST_NUM = 13

    urls_unauthorized = {
        'posts:home_page': [[], HTTPStatus.OK,
                            'posts/index.html', '/'],
        'posts:group_list': [[], HTTPStatus.OK,
                             'posts/group_list.html', '/group/{slug}/'],
        'posts:profile': [[], HTTPStatus.OK,
                          'posts/profile.html', '/profile/{username}/'],
        'posts:post_detail': [[], HTTPStatus.OK,
                              'posts/post_detail.html', '/posts/{post_id}/'],
        'posts:post_create': [[], HTTPStatus.FOUND,
                              None, '/create/'],
        'posts:post_edit': [[], HTTPStatus.FOUND,
                            None, '/posts/{post_id}/edit/'],
    }
    urls_authorized = {
        'posts:post_create': [[], HTTPStatus.OK,
                              'posts/create_post.html', '/create/'],
        'posts:post_edit': [[], HTTPStatus.FOUND,
                            None, '/posts/{post_id}/edit/'],
    }
    urls_author = {
        'posts:post_edit': [[], HTTPStatus.OK,
                            'posts/create_post.html',
                            '/posts/{post_id}/edit/'],
    }
    urls_paginator = {
        'posts:home_page': None,
        'posts:group_list': (TEST_GROUP_SLUG_1,),
        'posts:profile': (AUTHOR_USERNAME_1,),
    }

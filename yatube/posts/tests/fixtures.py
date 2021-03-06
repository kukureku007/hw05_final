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
    TEST_POST_CACHE = 'cache-cache-cache'

    AUTHOR_USERNAME_1 = 'SteveJ'
    AUTHOR_USERNAME_2 = 'SteveV'
    USER_USERNAME = 'SteveO'
    USER_USERNAME_1 = 'Hohoho'

    POST_TEXT = 'text'
    POST_NUM = 13

    TEST_IMAGE = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )

    URLS_PAGINATOR = {
        'posts:home_page': None,
        'posts:group_list': (TEST_GROUP_SLUG_1,),
        'posts:profile': (AUTHOR_USERNAME_1,),
        # 'posts:follow_index': None,
    }

    def __init__(self) -> None:
        """создание базовых словарей для тестов
        name: reverse-args, HTTPStatus, template, url.
        1.Добавлены тесты страниц комментариев"""
        self.URLS_UNAUTHORIZED = {
            'posts:home_page': [
                [], HTTPStatus.OK,
                'posts/index.html', '/'
            ],
            'posts:group_list': [
                [], HTTPStatus.OK,
                'posts/group_list.html', '/group/{slug}/'
            ],
            'posts:profile': [
                [], HTTPStatus.OK,
                'posts/profile.html', '/profile/{username}/'
            ],
            'posts:post_detail': [
                [], HTTPStatus.OK,
                'posts/post_detail.html', '/posts/{post_id}/'
            ],
            'posts:post_create': [
                [], HTTPStatus.FOUND,
                None, '/create/'
            ],
            'posts:post_edit': [
                [], HTTPStatus.FOUND,
                None, '/posts/{post_id}/edit/'
            ],
            'posts:add_comment': [
                [], HTTPStatus.FOUND,
                None, '/posts/{post_id}/comment/'
            ]
        }
        self.URLS_AUTHORIZED = {
            'posts:post_create': [
                [], HTTPStatus.OK,
                'posts/create_post.html',
                '/create/'
            ],
            'posts:post_edit': [
                [], HTTPStatus.FOUND,
                None,
                '/posts/{post_id}/edit/'
            ],
            'posts:add_comment': [
                [], HTTPStatus.FOUND,
                None, '/posts/{post_id}/comment/'
            ]
        }
        self.URLS_AUTHOR = {
            'posts:post_edit': [
                [], HTTPStatus.OK,
                'posts/create_post.html',
                '/posts/{post_id}/edit/'
            ],
        }

    def make_dict(self, post, group):
        """Формирование тестовых словарей с данными."""
        self.URLS_UNAUTHORIZED[
            'posts:group_list'][3] = self.URLS_UNAUTHORIZED[
            'posts:group_list'][3].format(slug=group.slug)
        self.URLS_UNAUTHORIZED[
            'posts:profile'][3] = self.URLS_UNAUTHORIZED[
            'posts:profile'][3].format(
                username=post.author.username)
        self.URLS_UNAUTHORIZED[
            'posts:post_detail'][3] = self.URLS_UNAUTHORIZED[
            'posts:post_detail'][3].format(
                post_id=post.pk)
        self.URLS_UNAUTHORIZED[
            'posts:post_edit'][3] = self.URLS_UNAUTHORIZED[
            'posts:post_edit'][3].format(
                post_id=post.pk)
        self.URLS_UNAUTHORIZED[
            'posts:add_comment'][3] = self.URLS_UNAUTHORIZED[
            'posts:add_comment'][3].format(
                post_id=post.pk)

        self.URLS_AUTHORIZED[
            'posts:post_edit'][3] = self.URLS_AUTHORIZED[
            'posts:post_edit'][3].format(
                post_id=post.pk)
        self.URLS_AUTHORIZED[
            'posts:add_comment'][3] = self.URLS_AUTHORIZED[
            'posts:add_comment'][3].format(
                post_id=post.pk)

        self.URLS_AUTHOR[
            'posts:post_edit'][3] = self.URLS_AUTHOR[
            'posts:post_edit'][3].format(
                post_id=post.pk)

        self.URLS_UNAUTHORIZED[
            'posts:post_detail'][0].append(post.pk)
        self.URLS_UNAUTHORIZED[
            'posts:post_edit'][0].append(post.pk)
        self.URLS_UNAUTHORIZED[
            'posts:group_list'][0].append(group.slug)
        self.URLS_UNAUTHORIZED[
            'posts:profile'][0].append(post.author.username)
        self.URLS_UNAUTHORIZED[
            'posts:add_comment'][0].append(post.pk)

        self.URLS_AUTHORIZED[
            'posts:post_edit'][0].append(post.pk)
        self.URLS_AUTHORIZED[
            'posts:add_comment'][0].append(post.pk)
        self.URLS_AUTHOR[
            'posts:post_edit'][0].append(post.pk)

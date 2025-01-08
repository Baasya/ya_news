from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'

NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass

@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client

@pytest.fixture
def news(db):
    """Тестовая новость."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(author, news):
    """Тестовый комментарий."""
    comment = Comment.objects.create(
            news=news,
            author=author,
            text='Текст комментария'
        )
    return comment

@pytest.fixture
def comment_for_args(comment):
    return (comment.id,)


@pytest.fixture
def news_on_home_page():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )

@pytest.fixture
def form_data():
    return {'text': COMMENT_TEXT}

@pytest.fixture
def form_data_new():
    return {'text': NEW_COMMENT_TEXT}


# urls
# @pytest.fixture
# def news_home_url():
#     return reverse('news:home')

# @pytest.fixture
# def users_login_url():
#     return reverse('users:login')

# @pytest.fixture
# def users_logout_url():
#     return reverse('users:logout')

# @pytest.fixture
# def users_signup_url():
#     return reverse('users:signup')

# @pytest.fixture
# def comment_update_url(comment):
#     return reverse('news:edit', args=(comment.id,))


# @pytest.fixture
# def comment_delete_url(comment):
#     return reverse('news:delete', args=(comment.id,))


# @pytest.fixture
# def news_detail_url(news):
#     return reverse('news:detail', args=(news.id,))


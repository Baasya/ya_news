from django.conf import settings

from news.forms import CommentForm


def test_news_count(client, news_on_home_page, news_home_url):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(news_home_url)
    object_list = response.context['object_list']
    new_count = object_list.count()
    assert new_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_on_home_page, news_home_url):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(news_home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, news_detail_url):
    """
    Комментарии отдельной новости отсортированы от старых к новым:
    старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news, news_detail_url):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news, news_detail_url):
    """
    Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

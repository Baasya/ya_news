from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from news.forms import CommentForm
from news.models import Comment, News

User = get_user_model()


class TestHomePage(TestCase):
    """Тестирование контента главной страницы."""

    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        today = datetime.today()
        News.objects.bulk_create(
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

    def test_news_count(self):
        """Количество новостей на главной странице — не более 10."""
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        new_count = object_list.count()
        self.assertEqual(new_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        """
        Новости отсортированы от самой свежей к самой старой.
        Свежие новости в начале списка.
        """
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(TestCase):
    """Тесты отдельной новостной страницы."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        cls.news = News.objects.create(
            title='Тестовая новость',
            text='Просто текст'
        )
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='Комментатор')
        now = timezone.now()
        for index in range(10):
            comment = Comment.objects.create(
                news=cls.news,
                author=cls.author,
                text=f'Tекст {index}',
            )
            comment.created = now + timedelta(days=index)
            comment.save()

    def test_comments_order(self):
        """
        Комментарии отдельной новости отсортированы от старых к новым:
        старые в начале списка, новые — в конце.
        """
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        self.assertEqual(all_timestamps, sorted_timestamps)

    def test_anonymous_client_has_no_form(self):
        """
        Анонимному пользователю недоступна форма для отправки
        комментария на странице отдельной новости.
        """
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        """
        Авторизованному пользователю доступна форма для отправки
        комментария на странице отдельной новости.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CommentForm)

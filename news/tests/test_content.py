# news/tests/test_content.py
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News

User = get_user_model()


class TestHomePage(TestCase):
    # Вынесем ссылку на домашнюю страницу в атрибуты класса
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        today = datetime.today()
        # 1___метод создания объектов 
        # all_news = []
        # for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        #     news = News(title=f'Новость {index}', text='Просто текст.')
        #     all_news.append(news)
        # News.objects.bulk_create(all_news)

        # 2___тожк самое с помощью list comprehension:
        # all_news = [
        #     News(title=f'Новость {index}', text='Просто текст.')
        #     for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        # ]
        # News.objects.bulk_create(all_news)

        # 3__тоже самое прямо внутри метода bulk_create:
        News.objects.bulk_create(
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

    # test OK
    def test_news_count(self):
        # загружаем главную страницу
        response = self.client.get(self.HOME_URL)
        # получаем список объектов словаря контекста
        object_list = response.context['object_list']
        # считаем количество записей
        new_count = object_list.count()
        # проверяем что записей именно 10
        self.assertEqual(new_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    # test OK
    def test_news_order(self):
        # загружаем главную страницу
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        # Получаем даты новостей в том порядке, как они выведены на странице
        all_dates = [news.date for news in object_list]
        # Сортируем полученный список по убыванию.
        sorted_dates = sorted(all_dates, reverse=True)
        # Проверяем, что исходный список был отсортирован правильно.
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title='Тестовая новость',
            text='Просто текст'
        )
        # Сохраняем в переменную адрес страницы с новостью:
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='Комментатор')
        # Запоминаем текущее время:
        now = timezone.now()
        # Создаём комментарии в цикле.
        for index in range(10):
            # Создаём объект и записываем его в переменную.
            comment = Comment.objects.create(
                news=cls.news,
                author=cls.author,
                text=f'Tекст {index}',
            )
            # Сразу после создания меняем время создания комментария.
            comment.created = now + timedelta(days=index)
            # И сохраняем эти изменения.
            comment.save()

    # test OK
    def test_comments_order(self):
        response = self.client.get(self.detail_url)
        # Проверяем, что объект новости находится в словаре контекста
        # под ожидаемым именем - названием модели.
        self.assertIn('news', response.context)
        # Получаем объект новости.
        news = response.context['news']
        # Получаем все комментарии к новости.
        all_comments = news.comment_set.all()
        # Собираем временные метки всех комментариев.
        all_timestamps = [comment.created for comment in all_comments]
        # Сортируем временные метки, менять порядок сортировки не надо.
        sorted_timestamps = sorted(all_timestamps)
        # Проверяем, что временные метки отсортированы правильно.
        self.assertEqual(all_timestamps, sorted_timestamps)

    # test OK
    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    # test OK
    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], CommentForm)

from http import HTTPStatus

from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from pytest_django.asserts import assertRedirects, assertFormError

from .conftest import COMMENT_TEXT, NEW_COMMENT_TEXT


def test_anonymous_user_cant_create_comment(client, form_data, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, form_data, news):
    """Авторизованный пользователь может отправить комментарий."""
    comments_amount = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == (comments_amount + 1)
    new_comment = Comment.objects.get()
    assert new_comment.text == COMMENT_TEXT
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    url_to_comments = reverse(
        'news:detail', args=(news.id,)
    ) + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, news, comment, form_data_new):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data_new)
    url_to_comments = reverse(
        'news:detail', args=(news.id,)
    ) + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, form_data_new
):
    """
    Авторизованный пользователь не может
    редактировать чужие комментарии.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=form_data_new)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT

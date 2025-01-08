from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

from .conftest import COMMENT_TEXT, NEW_COMMENT_TEXT


def test_anonymous_user_cant_create_comment(
    client, form_data, news_detail_url, users_login_url
):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(news_detail_url, data=form_data)
    expected_url = f'{users_login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, author, form_data, news_detail_url, news
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_amount = Comment.objects.count()
    response = author_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == (comments_amount + 1)
    new_comment = Comment.objects.get()
    assert new_comment.text == COMMENT_TEXT
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, news_detail_url):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client, news_detail_url, comment_delete_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment_delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, news_detail_url, comment, form_data_new, comment_edit_url
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(comment_edit_url, data=form_data_new)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, form_data_new, comment_edit_url
):
    """
    Авторизованный пользователь не может
    редактировать чужие комментарии.
    """
    response = not_author_client.post(comment_edit_url, data=form_data_new)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT

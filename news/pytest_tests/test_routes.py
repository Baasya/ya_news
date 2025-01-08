from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from .conftest import (
    AUTHOR_CLIENT,
    COMMENT_DELETE_URL,
    COMMENT_EDIT_URL,
    NEWS_DETAIL_URL,
    NEWS_HOME_URL,
    NOT_AUTHOR_CLIENT,
    USERS_LOGIN_URL,
    USERS_LOGOUT_URL,
    USERS_SIGHNUP_URL,
)


@pytest.mark.parametrize(
    'url',
    (
        NEWS_DETAIL_URL,
        NEWS_HOME_URL,
        USERS_LOGIN_URL,
        USERS_LOGOUT_URL,
        USERS_SIGHNUP_URL,
    ),
)
def test_pages_availability_for_anonymous_user(client, url):
    """Главная страница доступна анонимному пользователю.

    Страницы регистрации пользователей, входа в учётную
    запись и выхода из неё доступны всем пользователям.

    Страница отдельной новости доступна анонимному пользователю.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (AUTHOR_CLIENT, HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'url',
    (COMMENT_EDIT_URL, COMMENT_DELETE_URL),
)
def test_pages_availability_for_different_users(
        parametrized_client, url, expected_status
):
    """
    Страницы удаления и редактирования комментария
    доступны автору комментария.

    Авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев (возвращается ошибка 404).
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (COMMENT_EDIT_URL, COMMENT_DELETE_URL),
)
def test_redirects(client, url, users_login_url):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    expected_url = f'{users_login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

import datetime

import pytest
from flask import request
from werkzeug.exceptions import Forbidden

from app import load_service_before_request
from app.models.user import AnonymousUser, User
from app.utils.user import get_user_created_at_for_ticket, user_has_permissions
from tests.conftest import create_user


@pytest.mark.parametrize(
    "permissions",
    (
        pytest.param(
            [
                # Route has a permission which the user doesn’t have
                "send_messages"
            ],
            marks=pytest.mark.xfail(raises=Forbidden),
        ),
        [
            # Route has one of the permissions which the user has
            "manage_service"
        ],
        [
            # Route has more than one of the permissions which the user has
            "manage_templates",
            "manage_service",
        ],
        [
            # Route has one of the permissions which the user has, and one they do not
            "manage_service",
            "send_messages",
        ],
        [
            # Route has no specific permissions required
        ],
    ),
)
def test_permissions(
    client_request,
    permissions,
    api_user_active,
):
    request.view_args.update({"service_id": "foo"})

    api_user_active["permissions"] = {"foo": ["manage_users", "manage_templates", "manage_settings"]}
    api_user_active["services"] = ["foo", "bar"]

    client_request.login(api_user_active)

    @user_has_permissions(*permissions)
    def index():
        pass

    load_service_before_request()
    index()


def test_restrict_admin_usage(
    client_request,
    platform_admin_user,
):
    request.view_args.update({"service_id": "foo"})
    client_request.login(platform_admin_user)

    @user_has_permissions(restrict_admin_usage=True)
    def index():
        pass

    load_service_before_request()
    with pytest.raises(Forbidden):
        index()


def test_no_user_returns_redirect_to_sign_in(client_request):
    client_request.logout()

    @user_has_permissions()
    def index():
        pass

    response = index()
    assert response.status_code == 302
    assert response.location.startswith("/sign-in?next=")


def test_user_has_permissions_for_organisation(
    client_request,
    api_user_active,
):
    api_user_active["organisations"] = ["org_1", "org_2"]
    client_request.login(api_user_active)

    request.view_args = {"org_id": "org_2"}

    @user_has_permissions()
    def index():
        pass

    index()


def test_platform_admin_can_see_orgs_they_dont_have(
    client_request,
    platform_admin_user,
):
    platform_admin_user["organisations"] = []
    client_request.login(platform_admin_user)

    request.view_args = {"org_id": "org_2"}

    @user_has_permissions()
    def index():
        pass

    index()


def test_cant_use_decorator_without_view_args(
    client_request,
    platform_admin_user,
):
    client_request.login(platform_admin_user)

    request.view_args = {}

    @user_has_permissions()
    def index():
        pass

    with pytest.raises(NotImplementedError):
        index()


def test_user_doesnt_have_permissions_for_organisation(
    client_request,
    api_user_active,
):
    api_user_active["organisations"] = ["org_1", "org_2"]
    client_request.login(api_user_active)

    request.view_args = {"org_id": "org_3"}

    @user_has_permissions()
    def index():
        pass

    with pytest.raises(Forbidden):
        index()


def test_user_with_no_permissions_to_service_goes_to_templates(
    client_request,
    api_user_active,
):
    api_user_active["permissions"] = {"foo": ["manage_users", "manage_templates", "manage_settings"]}
    api_user_active["services"] = ["foo", "bar"]
    client_request.login(api_user_active)
    request.view_args = {"service_id": "bar"}

    @user_has_permissions()
    def index():
        pass

    load_service_before_request()
    index()


def test_get_user_created_at_date_for_ticket_returns_none_for_unauthenticated_user():
    unauthenticated_user = AnonymousUser()

    assert get_user_created_at_for_ticket(unauthenticated_user) is None


@pytest.mark.parametrize(
    "user_created_at, expected_value",
    [
        ("2023-11-07T08:34:54.857402Z", datetime.datetime(2023, 11, 7, 8, 34, 54, 857402, tzinfo=datetime.UTC)),
        ("2023-11-07T23:34:54.857402Z", datetime.datetime(2023, 11, 7, 23, 34, 54, 857402, tzinfo=datetime.UTC)),
        ("2023-06-07T23:34:54.857402Z", datetime.datetime(2023, 6, 7, 23, 34, 54, 857402, tzinfo=datetime.UTC)),
        ("2023-06-07T12:34:54.857402Z", datetime.datetime(2023, 6, 7, 12, 34, 54, 857402, tzinfo=datetime.UTC)),
    ],
)
def test_get_user_created_at_for_ticket(client_request, user_created_at, expected_value):
    user_json = create_user(created_at=user_created_at)
    user = User(user_json)

    assert get_user_created_at_for_ticket(user) == expected_value

from freezegun import freeze_time

from tests.conftest import (
    SERVICE_ONE_ID,
    create_active_user_empty_permissions,
    create_active_user_manage_template_permissions,
    create_active_user_view_permissions,
    create_active_user_with_permissions,
    normalize_spaces,
)


@freeze_time("2023-02-03 01:00")
def test_page_lists_team_members_of_service(
    mocker,
    client_request,
):
    manage_service_user_1 = create_active_user_with_permissions()
    manage_service_user_2 = create_active_user_with_permissions()
    manage_service_user_1["name"] = "Manage service user 1"
    manage_service_user_2["name"] = "Manage service user 2"
    manage_service_user_1["logged_in_at"] = "2023-01-02 01:00"
    manage_service_user_2["logged_in_at"] = "2023-02-03 01:00"

    mock_get_users = mocker.patch(
        "app.models.user.Users.client_method",
        return_value=[
            # These three users should not appear on the page
            create_active_user_empty_permissions(),
            create_active_user_manage_template_permissions(),
            create_active_user_view_permissions(),
            # These two users should appear on the page
            manage_service_user_1,
            manage_service_user_2,
        ],
    )

    page = client_request.get("main.join_service", service_to_join_id=SERVICE_ONE_ID)
    assert normalize_spaces(page.select_one("h1").text) == "Join service one"
    assert [normalize_spaces(item.text) for item in page.select("main .govuk-list li")] == [
        "Manage service user 1 – last logged in 2 January",
        "Manage service user 2 – last logged in today",
    ]
    mock_get_users.assert_called_once_with(SERVICE_ONE_ID)

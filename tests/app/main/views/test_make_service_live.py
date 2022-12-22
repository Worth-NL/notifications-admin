import pytest
from flask import url_for
from freezegun import freeze_time

from tests.conftest import (
    ORGANISATION_ID,
    SERVICE_ONE_ID,
    create_user,
    normalize_spaces,
    sample_uuid,
)


@pytest.mark.parametrize(
    "user, organisation_can_approve_own_go_live_requests, service_has_active_go_live_request, expected_status",
    (
        (
            # A user who is a member of the organisation
            create_user(id=sample_uuid(), organisations=[ORGANISATION_ID]),
            True,
            True,
            200,
        ),
        (
            # A platform admin users who is not a member of the organisation
            create_user(id=sample_uuid(), platform_admin=True),
            True,
            True,
            200,
        ),
        (
            # User who is a not an organisation team member can’t approve go live requests
            create_user(id=sample_uuid()),
            True,
            True,
            403,
        ),
        (
            # If the organisation can’t approve its own go live requests then the user is blocked
            create_user(id=sample_uuid(), organisations=[ORGANISATION_ID]),
            False,
            True,
            403,
        ),
        (
            # If the service doesn’t have an active go live request then the user is blocked
            create_user(id=sample_uuid(), organisations=[ORGANISATION_ID]),
            False,
            True,
            403,
        ),
    ),
)
def test_get_make_service_live_page(
    mocker,
    client_request,
    service_one,
    organisation_one,
    user,
    organisation_can_approve_own_go_live_requests,
    service_has_active_go_live_request,
    expected_status,
):
    organisation_one["can_approve_own_go_live_requests"] = organisation_can_approve_own_go_live_requests

    mocker.patch("app.organisations_client.get_organisation", return_value=organisation_one)

    service_one["has_active_go_live_request"] = service_has_active_go_live_request
    service_one["organisation"] = ORGANISATION_ID
    service_one["volume_letter"] = None

    client_request.login(user)

    page = client_request.get(
        "main.make_service_live",
        service_id=SERVICE_ONE_ID,
        _expected_status=expected_status,
    )

    if expected_status < 300:
        assert (
            normalize_spaces(page.select_one("main p")) == "Test User has requested for this service to be made live."
        )
        assert [normalize_spaces(li) for li in page.select("main li")] == [
            "111,111 emails per year",
            "222,222 text messages per year",
            "No letters",
        ]

        assert [
            (radio.select_one("input[type=radio]")["value"], normalize_spaces(radio.select_one("label").text))
            for radio in page.select(".govuk-radios__item")
        ] == [
            ("True", "Approve the request and make this service live"),
            ("False", "Reject the request"),
        ]


@pytest.mark.parametrize(
    "post_data, expected_arguments_to_update_service",
    (
        (
            True,
            {
                "message_limit": 250000,
                "restricted": False,
                "go_live_at": "2022-12-22 12:12:12",
                "has_active_go_live_request": False,
            },
        ),
        (
            False,
            {
                "message_limit": 50,
                "restricted": True,
                "go_live_at": None,
                "has_active_go_live_request": False,
            },
        ),
    ),
)
@freeze_time("2022-12-22 12:12:12")
def test_post_make_service_live_page(
    client_request,
    platform_admin_user,
    service_one,
    mock_get_organisation,
    mock_update_service,
    post_data,
    expected_arguments_to_update_service,
):
    service_one["has_active_go_live_request"] = True
    service_one["organisation"] = ORGANISATION_ID

    client_request.login(platform_admin_user)

    client_request.post(
        "main.make_service_live",
        service_id=SERVICE_ONE_ID,
        _data={
            "enabled": post_data,
        },
        _expected_redirect=url_for("main.organisation_dashboard", org_id=ORGANISATION_ID),
    )

    mock_update_service.assert_called_once_with(
        SERVICE_ONE_ID,
        **expected_arguments_to_update_service,
    )

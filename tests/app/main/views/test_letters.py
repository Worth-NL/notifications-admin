from functools import partial

import pytest
from flask import url_for

from tests import sample_uuid

letters_urls = [
    partial(url_for, "main.edit_service_template", template_id=sample_uuid()),
]


@pytest.mark.parametrize("method", ("get", "post"))
def test_add_template_page_doesnt_work_for_letters(
    client_request,
    service_one,
    method,
):
    service_one["permissions"] += ["letter"]
    getattr(client_request, method)(
        "main.add_service_template",
        template_type="letter",
        service_id=service_one["id"],
        _expected_status=404,
    )


@pytest.mark.parametrize("url", letters_urls)
@pytest.mark.parametrize("permissions, response_code", [(["letter"], 200), ([], 403)])
def test_letters_access_restricted(
    client_request,
    platform_admin_user,
    mocker,
    permissions,
    response_code,
    mock_get_service_letter_template,
    url,
    service_one,
):
    service_one["permissions"] = permissions
    client_request.login(platform_admin_user)
    client_request.get_url(
        url(service_id=service_one["id"]),
        _follow_redirects=True,
        _expected_status=response_code,
    )


@pytest.mark.parametrize("url", letters_urls)
def test_letters_lets_in_without_permission(
    client_request,
    mocker,
    mock_login,
    mock_has_permissions,
    api_user_active,
    mock_get_service_letter_template,
    url,
    service_one,
):
    service_one["permissions"] = ["letter"]
    mocker.patch("app.service_api_client.get_service", return_value={"data": service_one})

    client_request.login(api_user_active)
    client_request.get_url(url(service_id=service_one["id"]))

    assert api_user_active["permissions"] == {}


@pytest.mark.parametrize(
    "permissions, choices",
    [
        (["email", "sms", "letter"], ["Email", "Text message", "Letter", "Copy an existing template"]),
        (["email", "sms"], ["Email", "Text message", "Copy an existing template"]),
    ],
)
def test_given_option_to_add_letters_if_allowed(
    client_request,
    service_one,
    mocker,
    mock_get_service_templates,
    mock_get_template_folders,
    mock_get_organisations_and_services_for_user,
    mock_get_api_keys,
    permissions,
    choices,
):
    service_one["permissions"] = permissions

    page = client_request.get("main.choose_template", service_id=service_one["id"])

    radios = page.select("#add_new_template_form input[type=radio]")
    labels = page.select("#add_new_template_form label")

    assert len(radios) == len(choices)
    assert len(labels) == len(choices)

    for index, choice in enumerate(permissions):
        assert radios[index]["value"] == choice

    for index, label in enumerate(choices):
        assert labels[index].text.strip() == label

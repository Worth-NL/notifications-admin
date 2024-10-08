from flask import abort, redirect, render_template, url_for

from app import current_user
from app.limiters import RateLimit
from app.main import main
from app.main.forms import JoinServiceForm, SearchByNameForm
from app.models.service import Service
from app.utils.user import user_is_gov_user, user_is_logged_in


@main.route("/choose-service-to-join", methods=["GET", "POST"])
@user_is_logged_in
@user_is_gov_user
@RateLimit.USER_LIMIT
def choose_service_to_join():
    if not current_user.default_organisation.can_ask_to_join_a_service:
        abort(403)

    return render_template(
        "views/choose-service-to-join.html",
        _search_form=SearchByNameForm(),
    )


@main.route("/services/<uuid:service_to_join_id>/join", methods=["GET", "POST"])
@user_is_logged_in
@user_is_gov_user
@RateLimit.USER_LIMIT
def join_service(service_to_join_id):
    service = Service.from_id(service_to_join_id)

    if not service.organisation.can_ask_to_join_a_service:
        abort(403)

    if service.organisation != current_user.default_organisation:
        abort(403)

    form = JoinServiceForm(
        users=service.active_users_with_permission("manage_service"),
    )
    if form.validate_on_submit():
        service.request_invite_for(
            current_user,
            service_managers_ids=form.users.data,
            reason=form.reason.data,
        )
        return redirect(
            url_for(
                "main.join_service_requested",
                service_to_join_id=service.id,
                number_of_users_emailed=len(form.users.data),
            )
        )

    return render_template(
        "views/join-service.html",
        service=service,
        form=form,
    )


@main.route("/services/<uuid:service_to_join_id>/join/requested", methods=["GET", "POST"])
@user_is_logged_in
@user_is_gov_user
@RateLimit.USER_LIMIT
def join_service_requested(service_to_join_id):
    service = Service.from_id(service_to_join_id)
    return render_template(
        "views/join-service-requested.html",
        service=service,
    )

# Email Branding

Email branding allows specifying which branding should be used when sending an email from a specific `service`.

## UK flow

The intended flow (based on the UK codebase) for adding a new email branding is as follows:
1. A user/service makes a request for a new email branding
1. This request ends up in ZenDesk ticketing system
1. An admin user processes the request by adding a new email branding
1. An admin user assigns the new email branding to the service

## Current flow

At the moment of writing there is no ZenDesk available for this project, so users cannot send requests for new email branding.

Admins can add/edit a new email branding. For this, they require a branding `logo`.

## Dependencies

For the email branding flow to work, the app requires two AWS resources: an S3 bucket and a CDN.

The following two were created (currently in Ernout's account):

* S3_BUCKET_LOGO_UPLOAD = "public-logos-tools-notifynl"
* LOGO_CDN_DOMAIN = "d26j1qfpsndp6a.cloudfront.net"

The `S3_BUCKET_LOGO_UPLOAD` must be public, so that logos that are put in it are accessible/visible when distributing through the `LOGO_CDN_DOMAIN`.

__Note__: the `notifications-api` also needs to know the `CDN` domain. It uses it for the logo `image sources` in the email.
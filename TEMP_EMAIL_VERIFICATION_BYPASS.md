# Temporary email verification bypass (competition build)

Email verification has been temporarily disabled because SMTP delivery is not configured and the resend route currently errors.

- New accounts are created as `email_verified=1` and `account_status='active'`.
- Login, account-role access, career-discovery saving, and password-reset lookup do not require email verification while the switch is off.
- The verification routes and email-sending functions remain in the code for later repair.
- To re-enable later, set `EMAIL_VERIFICATION_REQUIRED = True` in `app.py`, then fix and test SMTP delivery and the resend route first.

This is a temporary local competition/demo configuration, not a recommended production security setting.

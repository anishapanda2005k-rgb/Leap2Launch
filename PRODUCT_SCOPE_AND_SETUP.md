# Leap2Launch — Product direction and setup

## Product direction
Leap2Launch is intended to be a broad, evolving career and lifelong-learning platform—not a single-degree portal. This build adds an expandable starter catalogue across science/research, computing/AI, healthcare, business/finance, engineering and trades, creative/media, hospitality/culinary, education/languages, sports/yoga/wellness, law/public service, agriculture/environment and applied technical careers. Each starter pathway includes an overview, related paths, skills, practice ideas and selected external learning resources.

The catalogue is intentionally a starter dataset, not a claim to cover every global degree, occupation, license, salary or course. Expansion should use reviewed, source-attributed records with country, currency, update date, eligibility, credentialing body, salary source/date, resource price/access, certificate conditions and license/permissions metadata. Do not mirror copyrighted books/PDFs without permission; link to legal open-access resources or host only material with suitable rights.

## Account model
- One account can hold multiple roles; roles are editable at `/account/roles`.
- The selected signup purpose is not a permanent identity. Existing dashboard behavior is preserved for backward compatibility while `user_roles` stores additional roles.
- New accounts remain pending until email verification succeeds. Existing accounts are migrated as verified to avoid locking out existing users.
- Email OTP is six digits, expires after 10 minutes, and is stored as a hash. A resend cooldown is enforced. Password-reset tokens are hashed and time-limited; reset links are emailed rather than displayed in the page.
- Email verification proves control of an inbox only. Education, employment, professional licensing and organization claims require separate verification.

## Configure real email delivery
Set these environment variables before starting the app. Use a provider SMTP credential/app password, not a personal account password.

Windows PowerShell example (values are examples/placeholders):

```powershell
$env:LEAP2LAUNCH_SMTP_HOST = "smtp.your-provider.example"
$env:LEAP2LAUNCH_SMTP_PORT = "587"
$env:LEAP2LAUNCH_SMTP_USERNAME = "your-smtp-username"
$env:LEAP2LAUNCH_SMTP_PASSWORD = "your-provider-app-password"
$env:LEAP2LAUNCH_FROM_EMAIL = "verified-sender@your-domain.example"
$env:LEAP2LAUNCH_SECRET_KEY = "set-a-long-random-secret"
python app.py
```

For port 465, implicit TLS is used. Without SMTP configuration, the application deliberately does not mark new accounts verified and does not reveal verification/reset codes in the browser. Configure a real email provider before public deployment. Also set a strong secret key, use HTTPS, configure secure cookies behind TLS, add CSRF protection, account lockout/rate limits, logging/monitoring, backup/restore and a privacy/retention policy before production.

## Career discovery
`/career-discovery` ranks starter pathways based on declared interests, preferred categories and self-reported skills. It is a transparent keyword-based baseline, not yet an advanced AI recommender. A production version should combine a maintained occupation/qualification graph, validated assessments specific to each field, user-controlled profile data, skill-gap evidence, source-grounded recommendations and explanations. Do not infer sensitive traits or promise jobs/admission outcomes.

## Run and test
Install `requirements.txt` in a virtual environment, configure SMTP, then run `python app.py`. Check `/build-status`, `/career-explorer`, `/career-discovery`, `/signup` and `/login`. No actual email can be delivered until SMTP is configured. This local source package is not a hosted live website.

## Open learning library
`/open-library` provides a source-linked starter directory of legal open-learning repositories. The platform must not bulk-upload books, PDFs, images or course content without item-level permission/license review. Keep the license, attribution, source URL and review date with every hosted resource.

Account settings also support changing an email only after the user confirms a code sent to the new address; the existing email remains active until confirmation. Multiple saved roles can be selected as an active workspace.

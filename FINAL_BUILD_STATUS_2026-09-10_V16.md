# Leap2Launch v16 — Final enhancement pass

Added in v16:
- Secure forgot-password flow with hashed, 30-minute reset tokens and single-use invalidation.
- Local SIH demo reset-link display (no SMTP dependency); production deployment should send the same reset URL through a transactional email provider.
- Skill Passport freshness layer: Fresh / Refresh soon / Stale based on latest verification/evidence timestamp.
- Explicit Claim → Demonstrate → Evidence → Human Verify → Refresh trust flow in the Skill Passport.
- New My World game: AI Collaboration Lab, focused on prompt quality, independent verification, critical thinking and responsible AI use.
- AI Collaboration Lab has distinct progressive Foundation/Challenge/Mastery content.
- Static validation: app.py compiles and all Jinja templates parse.

Runtime note: full Windows/PyCharm browser E2E testing still needs to be run in the user's local environment.

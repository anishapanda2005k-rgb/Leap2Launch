# Live data and demo-data retirement (V26 patch)

- Removed automatic creation of Demo Student/Faculty/Industry/Admin accounts, their synthetic evidence trail, and demo job/internship listings from startup seeding.
- Disabled the legacy SIH Demo Lab route and removed its navigation link.
- Disabled automatic synthetic challenge seeding; industry challenges are now created by signed-in company/admin accounts.
- Added challenge creator ownership and notifications when a student submits a solution. Solutions are stored as submissions; skill verification must remain pending until a real reviewer checks evidence.
- Added authenticated polling endpoints for connection chat, mentorship chat, and unread notification counts. Chat screens poll every 2.5 seconds; unread counts poll every 5 seconds. This is near-real-time polling, not WebSocket push.
- Existing databases may already contain historical demo records from older versions. This patch stops new seeding but does not automatically delete rows from a user's existing database, because deleting linked records blindly could remove real user data. Review and purge legacy demo rows explicitly before production deployment.
- Real external jobs, internships, company accounts, email delivery, and multi-user availability require real user accounts, deployment, database persistence and configured SMTP. No external vacancy or user data is fabricated by this patch.
- Runtime/browser tests still need to be run in an environment with the dependencies in requirements.txt installed.

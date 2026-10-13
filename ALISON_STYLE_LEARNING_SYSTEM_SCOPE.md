# Learning Studio expansion — V26

This implements original Leap2Launch features inspired by common self-paced learning platforms. It does not copy Alison branding, proprietary course text, question banks, or visual design.

## Included in this build
- Search/filter the existing course catalogue by keyword and domain.
- Enroll in a course; enrollment is stored per signed-in account.
- My Learning dashboard for enrolled courses, progress, saved pathways, and completion records.
- Save/unsave courses for later.
- Topic-by-topic external resource links and assessments using the existing topic/question bank.
- Progress summaries based on topic assessments; a topic counts as passed at 70% or above.
- Learner ratings/reviews limited to enrolled learners, with one review per account/course.
- Downloadable Leap2Launch completion PDF after all mapped topics pass at 70% or above.

## Important distinctions
- The catalogue is the existing starter catalogue, not a complete copy of Alison's global course library.
- External course content remains on its provider's site; this build does not scrape or republish paid/copyrighted course material.
- The generated PDF is a Leap2Launch platform completion record, not an accredited credential or an Alison certificate.
- A course with no topic map cannot earn a completion record until reviewed topic content and assessments are added.
- Runtime integration tests must be run on Windows with dependencies installed before treating the build as production-ready.

## Manual test checklist
1. Sign in with a non-demo account.
2. Open `/courses`; search and filter courses.
3. Enroll; confirm the course appears in `/learning-dashboard`.
4. Save a second course; confirm it appears in Saved for later; remove it.
5. Open a course, submit topic tests, retry a failed test, and verify progress persists after logout/login.
6. Confirm certificate route is denied until every topic passes; then download and inspect the PDF.
7. Submit a review as an enrolled learner; confirm rating/review uniqueness and that a non-enrolled user is denied.
8. Test on the existing database after taking a backup, then on a clean database.

## A–Z external learning directory expansion (12 October 2026)
- Added a separate `external_learning_resources` catalogue alongside the existing Leap2Launch course/progress system.
- Seeded 66 official provider/course-directory/resource entries spanning 45 subject labels, including yoga and AYUSH, nutrition and dietetics, health, nursing/allied health, veterinary science, pharmacy, cybersecurity, software, AI/data, aerospace/aeronautics, space research, astronomy, archaeology/heritage, law, business, finance, education, agriculture, design, arts, languages, climate, architecture, vocational trades, maritime, sports and more.
- External resources are searchable by keyword and filterable by domain on the existing `/courses` page. Resource cards show provider, type, access conditions, certificate caveats and a link to the official provider.
- Repeated provider URLs may appear under more than one subject because one official catalogue can serve multiple disciplines. Catalogue rows are unique by subject label + title.
- These are official catalogue/resource discovery links, not a claim to have imported every course available on the internet. Current availability, dates, eligibility, exam requirements and certificate fees must be checked on each provider page. A free learning experience does not always mean a free certificate.
- External course content remains hosted by its provider; no third-party videos, PDFs, quizzes or proprietary course text are copied into Leap2Launch.

## Verification note
- `app.py` and `learning_resource_catalog.py` passed Python bytecode compilation in the build environment.
- The resource seeding helper was tested against a fresh SQLite database for repeatable insertion and broad subject coverage.
- Full Flask route/browser integration testing could not run in the build environment because Flask is not installed there. Install the listed requirements and follow the manual workflow checklist above before treating this build as production-ready.

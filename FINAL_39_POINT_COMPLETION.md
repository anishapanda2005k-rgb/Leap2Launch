# Leap2Launch — 39-point completion checklist

1. Startup/error handling — retained working Flask entry point and fixed template/runtime references.
2. Route/template audit — all template `url_for()` references resolve to Python functions; Jinja parse check passes.
3. 12-language architecture — persistent language selector plus full-page translation layer.
4. Accessibility — high contrast, large text, reduced motion, focus, simplified/easy mode, keyboard focus, dyslexia-friendly, TTS and voice-navigation support.
5. Student dashboard flow — profile → assessment → skill map → gap → learning → proof → verification → portfolio → opportunity.
6. Profile system — student/faculty/company role separation and profile storage.
7. Academic programme skill catalogue — UG/PG coverage including BA/MA/BSc/MSc/BCom/MCom/BBA/MBA/BCA/BTech/MTech/BPharm/MPharm/PharmD and engineering/science specialisations.
8. Skill selection persistence — selectable skills save to student profile and skill_profiles.
9. Skill map — capability scores, targets, evidence and verification signals.
10. Dynamic skill-gap graph — programme-aware required skills, current/target/gap/priority and snapshot storage.
11. Skill Passport — dedicated evidence-backed passport plus refreshable gap snapshot and proof timeline.
12. Skill assessment — department-aware assessment with stored attempts and continuous profile updates.
13. Adaptive assessment — weak/recent performance used to prioritise question selection and progressive difficulty data.
14. Aptitude catalogue — quantitative, reasoning and verbal topic coverage with practice history.
15. Aptitude learning/test flow — topic → questions → score/explanation → skill signal.
16. Soft-skills catalogue — communication, leadership, teamwork, workplace and thinking scenarios.
17. Soft-skills learning/test flow — scenario practice → score/history → skill signal.
18. Department-specific assessment — Biotechnology, Computer Science and BBA plus programme-aware skill expansion.
19. Course catalogue — scalable course records and programme-specific tracks.
20. External learning resources — providers/resources are labelled as external/open; Leap2Launch is not presented as course provider.
21. Visual learning roadmap — course → topic → resource → practice/test → demonstration → verification.
22. Games Hub — single catalogue with department/skill mappings.
23. Playable game layer — interactive timed decision arena for web games plus interactive PCR/Delivery and browser Pharma Rescue.
24. Game performance metrics — time, mistakes, accuracy, score, level, decisions.
25. Game-to-evidence — gameplay creates pending evidence signals; never auto-verifies a skill.
26. Leap Points/rewards — bounded points, leaderboard and redemption thresholds.
27. Verification workflow — Pending/Verified/Rejected/Needs Changes with verifier, score, notes and date.
28. Verification appeals — student appeal storage and faculty/admin resolution flow.
29. Individual Learning Plan — generated from weak skills and linked to course resources with progress tracking.
30. Mastery — mastery scores, review quality, interval and next-review scheduling.
31. Industry opportunity posting — company/admin role restrictions for jobs, internships and challenges.
32. Intelligent matching — match %, matched skills, missing skills and explanation, persisted in opportunity_matches.
33. Mentorship lifecycle — request/update plus scheduled session and feedback support.
34. Verified portfolio — portfolio data, proof timeline and downloadable PDF/README.
35. Resume Builder — editable headline/summary/interests and evidence-aware PDF output.
36. ATS analyzer — target-role keyword alignment with matched/missing skills and stored analysis.
37. Outcomes + notifications + analytics — application/outcome lifecycle, notifications, analytics endpoints and exportable summary.
38. Security/governance — password hashing, protected routes, encrypted backup support, audit logs, upload validation and role controls.
39. Final audit/package — static Python compile, Jinja parse, endpoint reference audit, artifact cleanup, then consolidated ZIP.

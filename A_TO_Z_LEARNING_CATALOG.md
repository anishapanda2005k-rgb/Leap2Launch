# Leap2Launch A–Z Learning Directory

This directory is designed to help learners discover official course catalogues and learning resources across many disciplines. It complements, rather than replaces, Leap2Launch's own enrolled-course progress, assessment and completion-record features.

## Coverage

The seed now contains 121 learning-resource entries under 64 subject labels, including 55 individual course/resource pages checked against official provider pages on 2026-10-12. The expanded set adds direct course pages across statistics and research software, climate and sustainability, forensic science, business communication, zoology/ecology, metagenomics, chemistry, politics and social sciences, law, education, entrepreneurship, food science, archaeology/Egyptology, aerospace engineering/CAD, aeronautics, and exoplanet science. The database records availability notes, estimated duration, fee/access notes, certificate conditions and the date an individual course page was checked. It includes general university catalogues and specialist sources for computing/IT, cybersecurity, programming, data science and AI, health/public health, nutrition/dietetics, yoga/AYUSH, medicine, dentistry, veterinary and animal sciences, agriculture, pharmacy, nursing/allied health, space research, astronomy, aerospace/aeronautics, archaeology/heritage, law/public policy, psychology/social sciences, education, business, finance, arts/design, languages, climate/environment, architecture/planning, vocational trades, hospitality/tourism, GIS/geospatial science, biology/biotechnology, mathematics/statistics, sports, aviation, maritime/ocean studies, journalism/media, music/performing arts, fashion/textiles, public administration, geology, library/information science, food technology and career skills.

## How it works

- Sign in and open **Courses**.
- Search a topic (for example, `yoga`, `nutrition`, `cybersecurity`, `aerospace`, `space research`, or `archaeology`) or select a subject label.
- Use the external resource card to open the official provider's catalogue or learning page in a new tab.
- Review course dates, prerequisites, fees, accessibility, exam arrangements and certificate rules on the provider's own site before enrolling.

## Important distinctions

- The directory is a curated starting set, not a promise that every individual course in every field has been indexed. Provider catalogues can contain hundreds or thousands of changing offerings; ongoing curation is needed for a genuinely comprehensive catalogue.
- “Free learning” and “free certificate” are not interchangeable. Some providers charge for exams, graded work, labs or verified credentials.
- External courses are not represented as accredited Leap2Launch courses. A Leap2Launch completion record, where available for an internal course, is distinct from the external provider's certificate.
- The platform links to providers instead of copying content without permission.
- Individual course/resource-page checks recorded on 2026-10-12 reflect what the official page displayed at that time. Prices and access conditions can change; check the linked page before enrolling. Provider catalogue entries are not individually verified course listings and display that limitation. Some direct entries are open course materials or educational resources rather than certificate-bearing online courses.
- For courses listed as free audit with a paid certificate, the learner may study without paying but must pay if they choose the verified credential; prices shown are the values visible on the provider page at review time and may change.
- For regulated professions (including dietetics, clinical healthcare, yoga instruction and allied health), short online courses do not replace accredited degrees, supervised practice, registration or legal licensure requirements.


## Link maintenance workflow

- Run `python CHECK_LEARNING_LINKS.py` to generate `learning_link_audit.csv` for the current external links.
- The checker follows redirects, tries GET if HEAD is blocked, and labels blocked responses for manual review rather than treating them automatically as broken.
- Run `python VERIFY_LEARNING_LINK_AUDIT.py` for offline classification tests.
- Do not remove or mark a provider link inactive from one automated failure alone; confirm it in a normal browser.
- The catalogue also links to SWAYAM Plus, the Ministry of Education / IIT Madras industry-aligned learning platform. Its catalogue includes both free and paid programmes, so each course's price and delivery mode must be checked.

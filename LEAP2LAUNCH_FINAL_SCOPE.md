# Leap2Launch — Final SIH Scope

Product: Leap2Launch
Tagline: Demonstrate • Verify • Connect
Core: From “I know this” → “I can prove it.”
SIH PS: Portal for Academia - Industry collaboration for Skill Mapping, Internships and Placement
SIH ID: 26044

This package is the consolidated implementation baseline. It retains the existing application and incorporates the final agreed product direction: evidence-backed skills, adaptive assessment, learning and course catalogue, proof-of-work, verification, downloadable portfolio, resume generation, industry matching, faculty development, rewards/leaderboards, accessibility, security/privacy, AI Companion, lifecycle/outcome tracking and governance.

## Newly consolidated in this package
- Downloadable Leap2Launch Verified Portfolio PDF: `/portfolio/download`
- Leap Points and rewards page: `/rewards`
- Leaderboards page: `/leaderboards`
- Pharmacy Rescue game source: `game_sources/pharma_rescue.py`
- Pharmacy game web entry page: `/games/pharmacy/pharma-rescue`
- Extended game-result storage and Leap Points recording API: `/games/record`
- Environment-driven secret key support
- ReportLab and Pygame dependencies
- Branding cleanup from SkillQuest to Leap2Launch in source/templates

## Game integration model
GAME → PERFORMANCE → SKILL SIGNAL → EVIDENCE → REWARDS → LEADERBOARD → PROFILE

The other previously discussed game files must be supplied in their original form before their mechanics can be integrated. This package intentionally does not fabricate missing game source files.

## Critical end-to-end flows
1. Assessment → Skill Gap → Learning → Reassessment
2. Project/Game/Challenge → Evidence → Verification → Skill
3. Profile → Verified Portfolio → PDF → Company
4. Company demand → Matching → Opportunity → Application → Feedback
5. Faculty development → Certificate → Verification → Faculty growth

Run with the project's virtual environment and install `requirements.txt` before launch.

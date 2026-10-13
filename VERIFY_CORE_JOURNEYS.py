"""Static route/table coverage checks for the six Leap2Launch product priorities."""
import os, re, sys
ROOT=os.path.dirname(os.path.abspath(__file__))
source=open(os.path.join(ROOT,'app.py'),encoding='utf-8').read()
routes=set(re.findall(r"@app\.(?:route|get|post)\(['\"]([^'\"]+)",source))
checks={
 'Adaptive career discovery': ['/career-discovery','/career-explorer','/career-assessment/<slug>','/ai-companion'],
 'Skill-gap and evidence workflow': ['/skill-gaps','/skill-evidence','/verify-skills','/skill-gaps/export'],
 'Interactive simulations and game-to-proof': ['/games','/games/game-to-proof','/games/game-to-proof/submit','/challenge','/challenge-result'],
 'Learning Studio': ['/courses','/course/<int:course_id>/enroll','/course/<path:course_name>/learn','/course/<path:course_name>/certificate'],
 'Academia-industry community': ['/opportunities','/connections','/mentorship','/industry-challenges','/notifications','/opportunity/<int:opportunity_id>/apply'],
 'Real persistence and communication primitives': ['/api/connections/chat/<int:connection_id>/messages','/api/mentorship/chat/<int:request_id>/messages','/api/notifications/unread-count']
}
for area, required in checks.items():
    missing=[r for r in required if r not in routes]
    if missing:
        print('FAIL:',area,'missing routes:',', '.join(missing)); raise SystemExit(1)
    print('PASS:',area,'—',len(required),'required routes found')
for table in ['skill_evidence','skill_verification','course_enrollments','learning_plans','notifications','connection_requests','opportunities']:
    if table not in source:
        print('FAIL: missing persistence reference',table); raise SystemExit(1)
print('PASS: core persistence references found')
print('LIMIT: source-level route presence is not proof that every workflow passes browser/E2E tests.')

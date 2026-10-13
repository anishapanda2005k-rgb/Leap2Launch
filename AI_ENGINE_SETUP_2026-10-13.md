# Leap2Launch AI Engine — setup and limitations (13 October 2026)

## What changed

- The AI Companion now supports an optional **OpenAI-compatible Chat Completions API** without adding another Python dependency. The API key remains server-side.
- The model receives a purpose-built system prompt for career guidance, learning plans, skill evidence, regulated careers, uncertainty and privacy.
- Normal AI Companion chats can include the last few turns so follow-up questions retain context.
- Career Discovery now asks about degree/stage, preferred direction, interests, current experience and the learner's goal before making recommendations.
- When a provider is configured and reachable, it creates a personalised pathway report and 4-week starter plan. Without a key or if the provider call fails, the app falls back to explicit local guidance rather than claiming it used a large language model.
- The non-AI Career Discovery page now includes a four-week roadmap and labels the relative match score as a heuristic, not a probability of success.

## Configure a provider (optional)

The project deliberately ships **without an API key**. Do not commit a key to Git, paste it into a web page, or send it in chat.

On Windows, open **Edit environment variables for your account** and add these user variables, then close and reopen the terminal before starting the app:

- `LEAP2LAUNCH_AI_API_KEY` — secret key from the provider account.
- `LEAP2LAUNCH_AI_BASE_URL` — optional; defaults to `https://api.openai.com/v1`. For another OpenAI-compatible provider, use its documented API base URL.
- `LEAP2LAUNCH_AI_MODEL` — optional; defaults to `gpt-4o-mini`. Set a model actually available to your provider account. A more capable model may improve reasoning but can cost more and respond more slowly.

The endpoint used is `<base URL>/chat/completions`, unless the configured base URL already ends with `/chat/completions`.

**Before enabling it:** check provider pricing, data-retention terms, and whether external processing is permitted for your deployment. Set spending limits where available. The app sends the current question, a limited set of relevant profile skill fields, and recent chat turns; it does not need passwords or account secrets. Do not enter highly sensitive personal information.

## What “as strong as ChatGPT” means here

Code alone cannot turn a local rule-based chatbot into a frontier model. This change makes Leap2Launch capable of using a strong model **when the project owner configures and pays for/has access to one**, then supplies it with a careful platform-specific prompt and relevant context. Quality, latency, availability, privacy, and price depend on the chosen provider/model. With no API key, it remains a deterministic fallback, not a ChatGPT-equivalent model.

## Important limits

- No live web search/retrieval is performed by this API adapter. The model must not invent current salaries, vacancies, course status, or admission rules; the prompt explicitly requires current claims to be verified.
- The model does not autonomously enrol students, submit applications, verify skills, send messages, or update records. Those require separate explicit platform workflows.
- API output is not a verified credential or professional judgement. Regulated-career requirements must be checked with the relevant official regulator.
- Runtime/API integration must be tested in the target Windows environment with a permitted provider key before production use.


## Retrieval grounding update (13 October 2026)

AI Companion and Career Discovery now attach a small set of locally stored career-catalogue records selected by keyword relevance. The records include title, category, description, pathways, skills and starter activities, plus matched terms. This is lightweight lexical retrieval, not embeddings, semantic search or live web retrieval. It helps the model reason from the platform's actual catalogue without sending the whole catalogue on every request. Run `python VERIFY_AI_RETRIEVAL.py` for offline behavioral checks.

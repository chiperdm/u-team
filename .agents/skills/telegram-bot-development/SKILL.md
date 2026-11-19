---
name: telegram-bot-development
description: "Build and harden Telegram bots (pyTelegramBotAPI, aiogram, python-telegram-bot, grammY/Telegraf): polling vs webhook, handlers and persistent conversation state, inline keyboards and callbacks, quiz/screening flows, admin controls, SQLite storage, rate limits and flood handling, MarkdownV2 escaping, secrets, deployment and logging. Use for any Telegram bot, beta-tester recruiting bot, support/quiz/notification bot, or when a bot hangs, loses state, duplicates replies or gets 429/409 errors."
domain: backend
---

# Telegram bots

## Choose a library and mode
- Python: **aiogram 3** (async, FSM), **python-telegram-bot** (v20+ async), **pyTelegramBotAPI** (simple, sync/async). Node: **grammY** (modern) or Telegraf. Use what the project already has.
- **Long polling** (`getUpdates`): simplest, works anywhere with outbound HTTPS (Termux, PythonAnywhere-style hosts, home server). **Webhook**: lower latency/idle cost, needs HTTPS endpoint and a web server; set a secret token (`X-Telegram-Bot-Api-Secret-Token`) and verify it.
- Only ONE consumer per token: running two instances gives `409 Conflict: terminated by other getUpdates request`. Stop the old process before starting a new one; a webhook and polling cannot coexist (`deleteWebhook`).

## Skeleton (pyTelegramBotAPI)
```python
import os, sqlite3, telebot
from telebot import types
TOKEN = os.environ["BOT_TOKEN"]; ADMINS = {int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x}
bot = telebot.TeleBot(TOKEN, parse_mode=None, threaded=True)   # parse_mode None: escape explicitly when you enable it

db = sqlite3.connect("bot.db", check_same_thread=False, isolation_level=None)
db.execute("PRAGMA journal_mode=WAL"); db.execute("PRAGMA busy_timeout=5000")
db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, step TEXT, score INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")

@bot.message_handler(commands=["start"])
def start(m):
    db.execute("INSERT OR IGNORE INTO users(id, username, step) VALUES(?,?,?)", (m.from_user.id, m.from_user.username, "q1"))
    kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Begin", callback_data="quiz:start"))
    bot.send_message(m.chat.id, "Welcome! Ready for a short quiz?", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("quiz:"))
def on_cb(c):
    bot.answer_callback_query(c.id)                    # ALWAYS answer, or the button spins
    ...

bot.infinity_polling(timeout=20, long_polling_timeout=20, skip_pending=True)
```
Parameterized SQL only (`?`), never f-strings with user data (`security-injection-xss`).

## State for multi-step flows (quiz, screening, forms)
Keep the **step in the database** (`users.step`, answers table), not only in memory: in-memory `register_next_step_handler` state is lost on restart/redeploy and breaks users mid-flow. Make each handler idempotent (re-pressing a button must not double count): store `(user_id, question_id)` with a unique constraint (`api-idempotency`). Provide `/cancel` and `/restart`. Validate callback data (whitelist question ids/options).

## Inline keyboards and callbacks
`callback_data` max 64 bytes: use short codes (`q:3:b`), not text. Edit the existing message (`edit_message_text`) instead of sending a new one per step to keep chats clean. Deep links: `https://t.me/<bot>?start=<payload>` (payload up to 64 chars, `A-Za-z0-9_-`).

## Admin features
Authorize by numeric Telegram user id from env (`ADMIN_IDS`), never by username or text password in chat. Admin commands: `/stats`, `/export` (CSV of non-sensitive fields), `/broadcast` (confirm first; send slowly), `/ban`. Admin log channel: send events (new user, finished quiz) but **never tokens, full message content or personal data beyond need**; rate limit log messages.

## Limits and flood control
Approximately: 1 message/second per chat, 20 messages/minute per group, ~30 messages/second overall for broadcasts. On `429 Too Many Requests` read `retry_after` and sleep; broadcasts: queue + `time.sleep(0.05)` between sends + retry. Handle `403 Forbidden: bot was blocked by the user` (mark user inactive, don't retry). Check these limits in the official Bot API docs.

## Formatting
Plain text by default. If using `MarkdownV2`, escape `_ * [ ] ( ) ~ ` > # + - = | { } . !` in user content; or use HTML parse mode with `html.escape()`. Unescaped user text causes `400 can't parse entities`.

## Files and media
Use `file_id` to resend; downloading limit for bots is 20 MB via `getFile`; validate user uploads (type/size) before processing (`security-file-upload`).

## Security
Token only in env/secret manager; if leaked, revoke via @BotFather (`/revoke`) immediately (`security-secrets-logging`). Verify webhook secret token. Don't execute user-provided text. Rate limit expensive commands per user. Minimize stored personal data; offer `/delete_me`; tell users what you collect. Group bots: privacy mode, check `chat.type`, handle `my_chat_member` updates.

## Deploy
Polling bot as a Background Worker/service, systemd unit with `Restart=always`, Docker with `restart: unless-stopped` (`devops-docker-nginx`, `devops-render-deploy`; web services that sleep are unsuitable for polling). Persist SQLite on a volume or use Postgres; back it up. Log to stdout in structured form; global exception handler so one bad update does not kill the loop (`bot.infinity_polling(logger_level=...)`, `try/except` around handler bodies with logging); handle `SIGTERM`.

## Verify: tests
Use a separate test bot token; unit-test pure logic (scoring, step transitions); simulate updates by calling handlers with fake `Message` objects, or use the library's test utilities; smoke test `/start` end-to-end after each deploy; test restart mid-quiz resumes correctly; test blocked-user and 429 paths with fakes.

## Pitfalls
- Two instances running -> 409 and duplicate replies.
- Blocking handlers (slow HTTP/LLM calls) stalling polling: use threads/async, timeouts (`llm-integration-safety`).
- Storing quiz progress in a Python dict.
- Forgetting `answer_callback_query`.
- Hardcoding the token in the repo.

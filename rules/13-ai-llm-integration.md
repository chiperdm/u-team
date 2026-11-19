# AI / LLM Integration Standard
- Provider keys live server-side (or are user-supplied and stored in secure storage); never in APKs, bundles or HTML.
- All model-visible external content (messages, web pages, notifications, files, tool results) is untrusted data.
- Tools are allowlisted with validated arguments; irreversible, costly or outward-facing actions require explicit human confirmation.
- Model output is validated against a schema before use and never executed or interpolated into shell/SQL/HTML.
- Timeouts, bounded retries with backoff, model fallback, per-user quotas and spend alerts are mandatory.
- Prompts and transcripts are not logged by default; data minimization and disclosure of what leaves the device.
- A golden-prompt eval set (including injection and ru/kk/en cases) runs on every prompt/model change.

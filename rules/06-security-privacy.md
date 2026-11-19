# Security and Privacy
- Enforce authorization on the server/database boundary, not only in the UI.
- Review object ownership, role checks, session expiry, OTP replay, rate limits, storage policies, and logs.
- Prefer platform cryptographic primitives; never invent cryptographic algorithms.
- Keep secrets out of source, prompts, logs, screenshots, and reports.
- Minimize collection and retention of personal data.
- Security agents default to read-only review; remediation is a separate scoped task.

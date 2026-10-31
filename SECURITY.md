# Security and privacy

exHacker is under active development. Local tests and dependency audits provide evidence for specific behaviors; they do not certify the application or the infrastructure hosting it.

## Reporting a vulnerability

Use the repository's private vulnerability-reporting channel if enabled. Otherwise contact the maintainer through the verified [GitHub profile](https://github.com/Muneer320) to arrange a private report. Do not include API keys, workspace keys, private project exports, or exploitable details in a public issue. If a key leaks, revoke it with its issuer; deleting a message or Git commit does not revoke a credential.

## Current access model

- The browser generates a random 256-bit workspace bearer key and stores it in localStorage. The database stores its SHA-256 hash as the owner scope.
- All project routes, history, chat, exports, and mutations check that scope. Another browser without the key cannot access those resources by guessing a project ID.
- Possession of the key grants workspace access. Copy it privately through **Projects → Workspace access & recovery**. There is no email recovery, OAuth, team membership, key-rotation UI, or granular collaborator access today.
- Clearing browser storage without saving the key loses access. Browser extensions, XSS, or a compromised device can read it. LocalStorage persistence is intentional for this workspace token and must not be confused with the memory-only AI keys.

Per-workspace quotas can be bypassed by creating a new key or deleting projects. They are convenience limits, not a public-service abuse or billing boundary. Use perimeter rate/concurrency limits and provider-side spending controls.

## Data and external processing

The database persists the project intake, team names/skills, research sources/snippets, decisions, generated documents, history, and chat. An unsent intake draft is stored in the browser. Full current context and saved conversation are sent to the configured AI provider when answering live chat; project text is also used in web-search queries. Avoid confidential or regulated information unless your deployment and selected providers are approved for it.

BYOK is implemented with short-lived owner-bound backend RAM leases. The dedicated form clears on submission; browser storage contains no provider key. Jobs hold only routing metadata and an opaque lease reference. Provider calls use fixed HTTPS endpoints and request-scoped clients without authenticated-client caches, redirects, or environment-proxy inheritance. Expiry/removal cancels active AI calls; a restart requires credentials again. Operator AI mode is explicit and never a BYOK fallback. Tavily stays operator-managed. [BYOK architecture](docs/BYOK.md) documents precise lifecycle, recovery, tests and limitations. Never paste keys into ordinary project fields, which persist.

Application responses use private/no-store caching. Request bodies are bounded before JSON processing in both the proxy and API, including chunked requests. Untrusted Markdown does not enable raw HTML execution, links are sanitized, and images are displayed as deliberate external links rather than fetched automatically. Mermaid uses strict rendering. External fonts are currently loaded from Google Fonts; external link clicks and font requests have their own network/privacy implications.

Prompts instruct models to treat source snippets and project data as untrusted, and generated artifacts are schema-validated. These measures do not prove immunity to prompt injection or guarantee factual/technical correctness. Retrieved evidence is incomplete. Generated requirements and setup instructions need human review.

## Operations

Use HTTPS; protect database credentials, backups, exports, and logs. Restrict direct database/backend access. Runtime containers use non-root users, but their host remains a trusted boundary. Do not log authorization headers, full request bodies, AI keys, or SDK debug payloads. Unexpected application errors log only safe identifiers/types; provider error bodies are discarded and formatters redact known keys. Infrastructure, custom logging and debug tooling remain trusted boundaries. Set retention and access controls accordingly.

No third-party analytics or session-replay integration is configured by this repository. Adding one requires a privacy review, when handling BYOK. Logging/tracing configured by an operator or hosting platform is outside the code's guarantees.

Run `npm audit` and audit Python/container dependencies regularly. A clean advisory report is time-specific and does not rule out unknown vulnerabilities. Test upgrades rather than suppressing findings or blindly forcing incompatible versions.

The approved scoped-transport replacement removes LiteLLM and its vulnerable transitive filelock dependency. The latest locked-runtime Python and frontend audits report no known advisories; consult [verification evidence](docs/VERIFICATION.md) for the date and scope. This does not establish container OS or hosted-infrastructure safety.

BYOK requires one persistent API process with its embedded worker. No separate-process credential broker, multi-replica sharing or durable user secret store exists. Enforce HTTPS on public connections, protect private backend links, disable credential body/header capture and crash dumps, and review swap/hibernation policies. Memory-only means no intentional application persistence; Python/HTTP buffers and a trusted host cannot promise physical byte zeroization. Provider data policies still apply.

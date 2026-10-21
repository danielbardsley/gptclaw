# Non-secret configuration

`GPTCLAW_PROJECT_ID` is the only runtime environment input. The provider sets it
from the validated manifest ID; default for in-process tests is `example-api`.
It must be a lowercase slug of at most 48 characters. Base path is derived as
`/projects/<id>/`. No dotenv file is created or read; no host environment is forwarded.

Typed `Settings` also defines request_limit (60, valid 1–1000) and window_seconds
(60, valid 0.1–3600), passed explicitly when constructing the app. The limiter
uses one constant-memory process counter, resets at the window or process reload,
and exempts liveness/readiness/docs. It is a development admission demonstration.

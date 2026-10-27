# Component guidance

Operate this component through the parent project and `--component api`.
Do not start it independently. Dependency/format mutations require the group stopped.
Use locked dependencies in the reviewed exact container. Preserve unrelated source.
Read `docs/python-standards.md` before Python changes; keep thin typed routes,
injected domain services, safe metadata logs and at least 80% statement/branch
coverage. Use Black/isort/Ruff/mypy/pytest/Bandit/audit gates via group verify.

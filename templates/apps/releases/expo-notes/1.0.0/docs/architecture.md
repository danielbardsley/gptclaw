# Native notes architecture

Notebook owns list/editor/error state, NotesClient owns bounded typed HTTP requests,
and the public generated config names one explicit development backend. API/DB,
Metro and installed client are independently observed. OpenAPI-derived model/client
output is checked by checks/contract.cjs against contract/openapi.json; changing
Python models requires regenerating OpenAPI and updating the reviewed contract.
The repository-owned generator is versioned with this immutable starter and has
no downloaded tool dependencies. Retain notes and operational support intentionally;
remove unrelated starter demos. No server secrets belong in any native artifact.

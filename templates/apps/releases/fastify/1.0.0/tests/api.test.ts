import { test } from "node:test";
import assert from "node:assert/strict";
import { createApp } from "../src/app.ts";
import { settings } from "../src/settings.ts";
import { normalize } from "../src/service.ts";

test("settings refuse invalid identities and mismatched paths", async () => {
  for (const id of ["", "../x", "A", "a".repeat(49), "x/y", "x\n"])
    assert.throws(() => settings(id));
  await assert.rejects(
    createApp({ projectId: "test-api", basePath: "/foreign" }),
  );
  assert.equal(settings("test-api").basePath, "/projects/test-api");
});
test("prefix-aware schemas, validation, docs and health", async (t) => {
  const app = await createApp(settings("test-api"));
  t.after(() => app.close());
  const base = "/projects/test-api";
  for (const path of ["/live", "/ready"])
    assert.equal((await app.inject(base + path)).statusCode, 200);
  const good = await app.inject({
    method: "POST",
    url: base + "/api/v1/echo",
    payload: { message: "  hello   world " },
  });
  assert.deepEqual(good.json(), { message: "hello world" });
  for (const payload of [
    {},
    { message: 3 },
    { message: "" },
    { message: " ".repeat(3) },
    { message: "x".repeat(1001) },
    { message: "x", extra: true },
  ]) {
    const bad = await app.inject({
      method: "POST",
      url: base + "/api/v1/echo",
      payload,
    });
    assert.equal(bad.statusCode, 400);
    assert.ok(bad.json().error);
  }
  assert.equal(
    (
      await app.inject({
        method: "POST",
        url: base + "/api/v1/echo",
        payload: "{",
        headers: { "content-type": "application/json" },
      })
    ).statusCode,
    400,
  );
  assert.equal(
    (
      await app.inject({
        method: "POST",
        url: base + "/api/v1/echo",
        payload: { message: "x".repeat(20000) },
      })
    ).statusCode,
    413,
  );
  const list = await app.inject(base + "/api/v1/examples?offset=1&limit=1");
  assert.deepEqual(list.json(), {
    items: [{ id: 2, name: "Second example" }],
    total: 3,
    offset: 1,
    limit: 1,
  });
  assert.equal(
    (await app.inject(base + "/api/v1/examples")).json().items.length,
    3,
  );
  assert.deepEqual(
    (await app.inject(base + "/api/v1/examples?offset=999999")).json().items,
    [],
  );
  for (const query of [
    "limit=0",
    "limit=101",
    "offset=-1",
    "limit=x",
    "unknown=x",
  ])
    assert.equal(
      (await app.inject(base + "/api/v1/examples?" + query)).statusCode,
      400,
    );
  for (const url of ["/ready", "/projects/other/ready", base + "/missing"])
    assert.equal((await app.inject(url)).statusCode, 404);
  const spec = (await app.inject(base + "/openapi.json")).json();
  assert.equal(spec.openapi, "3.0.3");
  assert.deepEqual(spec.servers, [{ url: base }]);
  assert.ok(spec.paths["/api/v1/echo"]);
  assert.equal(spec.paths["/api/v1/echo"].post.operationId, "echo");
  const docs = await app.inject(base + "/docs/");
  assert.equal(docs.statusCode, 200);
  assert.match(docs.body, /swagger-ui/);
  assert.doesNotMatch(docs.body, /https:\/\/(?:unpkg|cdn)/);
  for (const path of [
    "/docs/static/swagger-ui-bundle.js",
    "/docs/static/swagger-ui.css",
    "/docs/json",
  ])
    assert.equal((await app.inject(base + path)).statusCode, 200);
});
test("domain normalization handles whitespace and rejects empty content", () => {
  assert.equal(normalize(" one\n two "), "one two");
  assert.throws(() => normalize("   "));
});

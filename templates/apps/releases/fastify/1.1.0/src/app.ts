import Fastify, { type FastifyError } from "fastify";
import swagger from "@fastify/swagger";
import swaggerUi from "@fastify/swagger-ui";
import { settings, type Settings } from "./settings.ts";
import { examples, normalize } from "./service.ts";

const errorSchema = {
  type: "object",
  required: ["error"],
  properties: { error: { type: "string" } },
  additionalProperties: false,
};
export async function createApp(config: Settings = settings()) {
  // Revalidate supplied configuration too. Never trust a caller-provided prefix.
  const { basePath } = settings(config.projectId);
  if (config.basePath !== basePath) throw new Error("Invalid basePath");
  const app = Fastify({
    logger: false,
    trustProxy: false,
    bodyLimit: 16384,
    ajv: { customOptions: { removeAdditional: false, coerceTypes: false } },
  });
  await app.register(swagger, {
    openapi: {
      info: { title: "Synthetic TypeScript API", version: "1.0.0" },
      servers: [{ url: basePath }],
    },
    transform: ({ schema, url }) => ({
      schema,
      url: url.startsWith(basePath) ? url.slice(basePath.length) : url,
    }),
  });
  app.get(
    `${basePath}/live`,
    {
      schema: {
        operationId: "liveness",
        response: {
          200: {
            type: "object",
            required: ["status"],
            properties: { status: { const: "alive" } },
          },
        },
      },
    },
    async () => ({ status: "alive" }),
  );
  app.get(
    `${basePath}/ready`,
    {
      schema: {
        operationId: "readiness",
        response: {
          200: {
            type: "object",
            required: ["status"],
            properties: { status: { const: "ready" } },
          },
        },
      },
    },
    async () => ({ status: "ready" }),
  );
  app.post<{ Body: { message: string } }>(
    `${basePath}/api/v1/echo`,
    {
      schema: {
        operationId: "echo",
        body: {
          type: "object",
          required: ["message"],
          additionalProperties: false,
          properties: {
            message: { type: "string", minLength: 1, maxLength: 1000 },
          },
        },
        response: {
          200: {
            type: "object",
            required: ["message"],
            additionalProperties: false,
            properties: { message: { type: "string" } },
          },
          400: errorSchema,
        },
      },
    },
    async (request, reply) => {
      try {
        return { message: normalize(request.body.message) };
      } catch {
        return reply.code(400).send({ error: "Message must contain text" });
      }
    },
  );
  app.get<{ Querystring: { offset?: string; limit?: string } }>(
    `${basePath}/api/v1/examples`,
    {
      schema: {
        operationId: "listExamples",
        querystring: {
          type: "object",
          additionalProperties: false,
          properties: {
            offset: { type: "string", pattern: "^(0|[1-9][0-9]{0,5})$" },
            limit: { type: "string", pattern: "^([1-9]|[1-9][0-9]|100)$" },
          },
        },
        response: {
          200: {
            type: "object",
            required: ["items", "total", "offset", "limit"],
            properties: {
              items: {
                type: "array",
                items: {
                  type: "object",
                  required: ["id", "name"],
                  properties: {
                    id: { type: "integer" },
                    name: { type: "string" },
                  },
                },
              },
              total: { type: "integer" },
              offset: { type: "integer" },
              limit: { type: "integer" },
            },
          },
          400: errorSchema,
        },
      },
    },
    async (request) =>
      examples(
        Number(request.query.offset ?? 0),
        Number(request.query.limit ?? 20),
      ),
  );
  app.setErrorHandler<FastifyError>((error, _request, reply) => {
    const status = error.validation
      ? 400
      : typeof error.statusCode === "number" &&
          error.statusCode >= 400 &&
          error.statusCode < 500
        ? error.statusCode
        : 500;
    return reply.code(status).send({
      error:
        status === 400
          ? "Invalid request"
          : status === 413
            ? "Request too large"
            : "Request failed",
    });
  });
  app.setNotFoundHandler((_request, reply) =>
    reply.code(404).send({ error: "Not found" }),
  );
  await app.register(swaggerUi, {
    routePrefix: `${basePath}/docs`,
    staticCSP: true,
  });
  app.get(`${basePath}/openapi.json`, { schema: { hide: true } }, async () =>
    app.swagger(),
  );
  await app.ready();
  return app;
}

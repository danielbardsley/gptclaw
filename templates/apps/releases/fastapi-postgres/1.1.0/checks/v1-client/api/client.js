"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.NotesClient = exports.ApiError = void 0;
const backend_generated_1 = require("../config/backend.generated");
const contract_1 = require("./contract");
class ApiError extends Error {
    kind;
    constructor(kind) {
        super({
            setup: 'Connect this notebook to its Python backend first.',
            validation: 'Check your title and note length, then try again.',
            missing: 'This note no longer exists. Refresh your notebook.',
            unavailable: 'Your notebook is out of reach. Check the connection and refresh.',
            uncertain: 'The server may have received your change. Refresh saved notes before trying again.',
        }[kind]);
        this.kind = kind;
    }
}
exports.ApiError = ApiError;
class NotesClient {
    config;
    send;
    constructor(config = backend_generated_1.backend, send = globalThis.fetch) {
        this.config = config;
        this.send = send;
    }
    async request(path, method = 'GET', body) {
        if (!this.config.enabled)
            throw new ApiError('setup');
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 15_000);
        try {
            const response = await this.send(this.config.apiUrl + path, {
                method,
                signal: controller.signal,
                headers: {
                    Accept: 'application/json',
                    ...(body ? { 'Content-Type': 'application/json' } : {}),
                },
                ...(body ? { body: JSON.stringify(body) } : {}),
                redirect: 'error',
            });
            if (!response.ok)
                throw new ApiError(response.status === 422
                    ? 'validation'
                    : response.status === 404
                        ? 'missing'
                        : method === 'GET'
                            ? 'unavailable'
                            : 'uncertain');
            return (response.status === 204 ? undefined : await response.json());
        }
        catch (error) {
            if (error instanceof ApiError)
                throw error;
            throw new ApiError(method === 'GET' ? 'unavailable' : 'uncertain');
        }
        finally {
            clearTimeout(timer);
        }
    }
    list(offset = 0) {
        return this.request(`${contract_1.endpoints.collection}?limit=20&offset=${offset}`);
    }
    get(id) {
        return this.request(`${contract_1.endpoints.collection}/${encodeURIComponent(id)}`);
    }
    save(input, id) {
        return this.request(id
            ? `${contract_1.endpoints.collection}/${encodeURIComponent(id)}`
            : contract_1.endpoints.collection, id ? 'PUT' : 'POST', input);
    }
    remove(id) {
        return this.request(`${contract_1.endpoints.collection}/${encodeURIComponent(id)}`, 'DELETE');
    }
}
exports.NotesClient = NotesClient;

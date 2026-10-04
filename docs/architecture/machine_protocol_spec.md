# v1.9 Phase 1: Machine-Operable Protocol Specification

**Status:** DRAFT (Architecture Review)  
**Target:** TinPyUI v1.9

## 1. Principles and Scope

The TinPyUI Machine Protocol v1 defines a stable, deterministic, language-agnostic interface for tools interacting with the TinPyUI ecosystem.

**Architectural Rule:** AI is a consumer of this protocol, not the definition of it.
The protocol is designed as a foundational API for Language Servers (LSP), Continuous Integration (CI), IDE extensions, deployment pipelines, and autonomous agents.

It communicates strictly via structured JSON over `stdin`/`stdout` using a JSON-RPC 2.0-like envelope.
**Crucial Constraint:** `stdout` MUST contain only protocol messages. All human-readable logs, debug information, or fatal crash traces MUST be routed to `stderr`.

This ensures the protocol is **transport/session agnostic**. It can be executed as a one-shot process (`tinui agent check`) or as a persistent daemon. The protocol schema remains identical in both paradigms.

### Session Lifecycle Model

The protocol defines a logical session lifecycle regardless of execution mode:

1. `initialize`
2. `update_document` (optional, for virtual/in-memory buffers)
3. `query` (optional, semantic interrogations)
4. `check` / `build`
5. `close_document` (optional)
6. `shutdown`

*   **One-shot execution** compresses this into: `initialize` → `check` → exit.
*   **Persistent execution** keeps the transport open, allowing multiple `update_document` and `query` interactions.

**Session Ownership Constraint:** Virtual-document state exists only within the lifetime of the protocol session/transport stream and is discarded when that session terminates. One-shot CLI invocations do not share memory and cannot preserve in-memory state after exit.

---

## 2. Protocol Capability Handshake (Initialization)

Consumers must be able to query what a specific version of the compiler supports without guessing or breaking. This is the required first step of any session.

### `tinui agent initialize` (or `initialize` JSON-RPC method)
Returns a machine-readable JSON object of supported features, protocol version, and tinui version.

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "1.0",
    "tinuiVersion": "1.9.0",
    "capabilities": [
      "context",
      "schema",
      "diagnostics",
      "graph",
      "build",
      "repair",
      "virtual_documents",
      "semantic_query"
    ]
  }
}
```

---

## 3. Request/Response Envelopes

To maintain compatibility with LSP and streaming tooling, all commands are structured as JSON-RPC 2.0 envelopes.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "build",
  "params": {
    "uri": "file:///project/pages/index.tin",
    "entry": "pages/index.tin",
    "target": "dist"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true,
    "metrics": { "nodes": 142, "binary_size_bytes": 10240 }
  }
}
```

---

## 4. JSON Diagnostics & 5. Stable Error Codes

The compiler emits structured telemetry instead of raw stderr text. This allows for automated analysis.

Error codes (e.g., `TIN-0012`) must be stable and immutable. If the semantic meaning of an error changes, a new code must be issued.

*   `TIN-0000` to `TIN-0999`: Syntax & Parser Errors
*   `TIN-1000` to `TIN-1999`: Semantic / Type Check Errors
*   `TIN-2000` to `TIN-2999`: Linking & Project Graph Errors
*   `TIN-3000` to `TIN-3999`: ABI / Runtime Metdata Errors
*   `TIN-8000` to `TIN-8999`: Security / Honeypot Guard Violations

---

## 6. File / Line / Column / AST References

Diagnostics must trace exactly back to the source map.

```json
{
  "file": "components/Button.tin",
  "line": 14,
  "column": 9,
  "ast_node": "AttributeDefinition"
}
```
*Position Semantics Constraint: All protocol fields representing lines and characters MUST be zero-based. For encoding, "character" strictly denotes UTF-16 code units (matching standard LSP defaults).*

---

## 7. Project Graph

Tools need to understand the relationship between components to intelligently orchestrate incremental compilation and impact analysis.

### `tinui agent graph`
**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "root": "main.tin",
    "components": [
      {
        "id": "Header",
        "file": "components/Header.tin",
        "dependencies": ["components/Logo.tin", "components/Nav.tin"]
      }
    ]
  }
}
```

---

## 7.5 Request Cancellation

The protocol supports asynchronous cancellation of long-running requests to protect agent CPU/Memory from thrashing during rapid document edits or aborted queries.

Agents that support cancellation MUST broadcast `"cancellation"` in their `initialize` response capabilities.

### `$/cancelRequest` method

The client may issue a Notification (a request without an `id`) to terminate a specific ongoing request.

**Notification:**
```json
{
  "jsonrpc": "2.0",
  "method": "$/cancelRequest",
  "params": {
    "id": 42
  }
}
```

### Cancellation Contract

1. **Relation to JSON-RPC IDs**: The `id` parameter MUST exactly match the `id` of the JSON-RPC request to be cancelled. It can be a `string` or `number`.
2. **Cancellable Operations**: `check`, `build`, and all `query` methods MUST be cancellable. Lifecycle methods (`initialize`, `shutdown`, `update_document`, `close_document`) are strictly non-cancellable.
3. **Best-Effort Delivery**: Cancellation is explicitly **best-effort**. The client cannot assume the server will halt execution immediately.
4. **Stable Error Semantics**: If the server successfully aborts a request before generating a result, it MUST return an error response for that request `id` with the stable Protocol Error Code: `-32800` ("Request Cancelled").
5. **Arrival Before Execution**: If cancellation arrives before the worker begins executing the payload (e.g. queued in the dispatcher), the dispatcher MUST drop the request immediately and reply with `-32800`.
6. **Arrival During Execution**: If execution has already begun, the worker MUST terminate early if safely possible and reply with `-32800`.
7. **Arrival After Completion**: If cancellation arrives after the request has finished (or if the `id` is unknown), the server MUST silently ignore the cancellation notification. It MUST NOT return an error for the `$/cancelRequest` notification itself.
8. **Document Version Safety**: Cancelling a `check` or `query` for document version `N` simply yields a `-32800` response. It MUST NOT corrupt or invalidate future queries for version `N+1`.

---

## 8. Build, Check, Run, Test Operations

Operations shift from procedural terminal commands to declarative job requests.

*   `check`: Perform full AST, semantic, and ABI validation. Returns `Diagnostic[]`. Does not emit `.bin`.
*   `build`: Execute `check`, then generate `app.ir.bin`, `app.ir.json`, and static assets.
*   `run`: Starts the local dev server. Streams progress and binds to an SSE endpoint.
*   `test`: Discovers `.test.tin` or python logic, executes tests, and returns xUnit/JSON test reports.

### Virtual Documents & VFS Model

Commands accepting file targets (e.g., `check`, `build`, `update_document`) support a `source` parameter representing an unsaved, in-memory editor buffer. 
When `source` is provided, a `version` integer MUST also be included to track document progression. The compiler MUST prioritize this `source` over the physical disk contents of `uri`. 
Any queries or checks referencing a stale document version will produce a stable Protocol Error (Code: `-32002`, "Stale Document Version").

```json
{
  "method": "check",
  "params": {
    "uri": "file:///project/pages/login.tin",
    "source": "component Main():\n    Text(text=\"Unsaved changes\")",
    "version": 17
  }
}
```

### Formal Lifecycle Methods

To manage virtual documents, clients may use explicit lifecycle methods:
*   `update_document`: Syncs an unsaved `source` and `version` into the session VFS.
*   `close_document`: Discards the VFS buffer for a given `uri`, reverting to disk backing.
*   `shutdown`: Gracefully terminates the session and purges all VFS state.

### Semantic Queries

Semantic interrogation of the AST uses a unified `query` method, parameterized by `kind`.

```json
{
  "method": "query",
  "params": {
    "kind": "hover",
    "document": "file:///project/pages/login.tin",
    "position": { "line": 14, "character": 8 }
  }
}
```
**Supported Kinds & Response Schemas:**
*   `hover`: Returns `HoverResponse` containing markdown `contents` and a `range` covering the hovered token, alongside the document `version`.
*   `definition`: Returns `DefinitionResponse` containing the `uri` and `range` of the symbol's definition, alongside the document `version`.
*   `completion`: Returns `CompletionResponse` containing an array of `items` (each having `label`, `kind`, `detail`, `documentation`), alongside the document `version`.

*Note: Unsupported `kind` values MUST produce a JSON-RPC method not found error or a specific protocol error.*

---

## 9. Machine-Readable Progress & Status

Long-running operations (like `build --mobile` or `run`) must emit progress non-interactively.

```json
{
  "jsonrpc": "2.0",
  "method": "progress",
  "params": {
    "token": "build_task_1",
    "status": "report",
    "percentage": 45,
    "message": "Generating Swift application harness..."
  }
}
```

---

## 10. Repair Suggestions (LSP TextEdit Adapter)

When the compiler detects a rigid, well-understood failure (e.g., misspelled attribute or deprecated syntax), it MUST provide a `repair_suggestion`. 

TinPyUI Diagnostics are proprietary to the framework, but the nested `edits` object natively adopts the **LSP `TextEdit` schema**. This makes IDE and Agent consumption frictionless without making the entire protocol dependent on LSP.

```json
"repair_suggestion": {
  "description": "Replace ':' with '='",
  "edits": [
    {
      "range": {
        "start": { "line": 14, "character": 23 },
        "end": { "line": 14, "character": 24 }
      },
      "newText": "="
    }
  ],
  "is_deterministic": true
}
```
*Agents and IDEs can apply `is_deterministic: true` fixes automatically without user prompt.*

---

## 11. Protocol Versioning & 12. Backward Compatibility

The protocol is explicitly versioned independently of the framework runtime.
*   Protocol v1 expects TinPyUI Runtime ABI v4.
*   Changes to the schema (adding keys) are allowed in minor protocol bumps.
*   Removing keys or restructuring the JSON-RPC envelope requires a major protocol version bump.

Consumers should always query `tinui agent capabilities` to assert `protocol_version` before sending operational commands.

---

## 13. Security Boundaries

*   **Sandboxing**: The `tinui agent` commands operate entirely on static analysis and determinism. `tinui agent check` and `graph` MUST NOT execute arbitrary Python or `.tin` state evaluations.
*   **Arbitrary Execution**: Only `run` and `test` are permitted to execute side-effects or instantiate the runtime.
*   **Path Traversal**: All `file` references returned in diagnostics or requested in `build` must be rigidly bounded to the project workspace root.

---

## Ambiguities Resolved

*   **Transport Layer**: Locked to `stdin/stdout` streaming JSON-RPC. `stdout` is exclusively for JSON; `stderr` is for human logging.
*   **Stateful vs Stateless**: Locked to be **session agnostic**. One-shot CLI execution is the v1.9 normative behavior, but persistent sessions use the exact same schema.
*   **Repair Suggestion Format**: Locked to the LSP `TextEdit` standard, but encapsulated within the TinPyUI Diagnostic model to prevent protocol dependency on LSP.

---

## Appendix A: Non-Normative Performance Targets

These targets serve as implementation guidance for toolbuilders and backend developers; they are not rigid protocol guarantees.
*   **Initialization:** < 50ms
*   **Semantic Queries (`hover`, `completion`):** < 50ms latency (highly cached, in-memory)
*   **Incremental Check (VFS):** < 100ms
*   **Full Build:** Dependent on project size, but should stream progress events if > 500ms.

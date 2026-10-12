# A.6 Branch-Sensitive Data-Flow Analysis Test Suite

This directory contains executable `.tin` examples that validate Phase A.6 branch-sensitive data-flow analysis, type narrowing, and environment isolation using existing public TinPyUI syntax.

## Coverage Matrix

| Test File | Capability Tested | Verification Target |
|:---|:---|:---|
| `01_declarative_conditional.tin` | Basic `if / else` Conditional | Single-level declarative conditional structure, branch isolation, and merging |
| `02_nested_conditional.tin` | Nested Conditionals | Hierarchical `FlowEnvironment` child scoping and deterministic scope exit |
| `03_conflicting_branches.tin` | Branch Isolation | Non-leakage of facts between sibling branches (`TrueBranch` vs `FalseBranch`) |
| `04_any_vs_unknown.tin` | Type Narrowing (`Any` vs `Unknown`) | Sound narrowing of dynamic expressions under explicit equality guards |
| `05_state_derived_flow.tin` | State-Derived Data Flow | Resolution of state-derived dependencies within declarative UI branches |
| `06_cross_component_context.tin` | Cross-Component Context | Type validation for component invocations within branch scopes |

## Compilation & Verification

All examples are valid TinPyUI syntax and can be verified via the CLI:

```bash
go run main.go check examples/a6/01_declarative_conditional.tin
go run main.go check examples/a6/02_nested_conditional.tin
go run main.go check examples/a6/03_conflicting_branches.tin
go run main.go check examples/a6/04_any_vs_unknown.tin
go run main.go check examples/a6/05_state_derived_flow.tin
go run main.go check examples/a6/06_cross_component_context.tin
```

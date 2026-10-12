# A.6 Scope Decision & Architecture Audit

## 1. Existing Capabilities
The public TinPyUI syntax strictly separates declarative rendering from imperative state mutation:
- **Declarative Control-Flow**: Branching exists purely in the UI rendering tree via `ConditionalNode` (`if`/`else`).
- **Imperative Mutations**: State mutations only exist as linear, flat arrays of `MutationNode` inside `DefNode` blocks.
- **State Semantics**: Component state variables are immutable during rendering passes.
- **Data-Flow Engine**: Resolves topological dependencies statically, mapping values from declarations to component usage sites.

## 2. What "Branch-Sensitive Data Flow" Actually Means for TinPyUI
In a traditional imperative language, data-flow branching focuses on variables mutating conditionally and then merging (e.g., PHI nodes in SSA form).
However, in TinPyUI's declarative rendering model, **state variables do not mutate during a branch, and UI paths do not merge data**. Instead, branch-sensitive data-flow means **Type Narrowing and Contextual Fact Propagation**:
- When the analyzer enters an `if condition > 10:` branch, the `FlowEnvironment` can record a new localized fact: `condition` is strictly numeric inside this UI scope.
- Inside the branch, any component relying on `condition` leverages this narrowed type fact.
- Once the branch ends, the `FlowEnvironment` simply pops, reverting to the parent environment. There is no complex "variable merge" because variables were never mutated.

## 3. Existing Syntax That Can Exercise It
We can thoroughly test A.6 using the existing `ConditionalNode` in the UI tree without inventing new syntax:
```tin
Component UserCard(age: Any):
    // Data-flow currently sees 'age' as Any.

    if age > 18:
        // Inside this branch, A.6 FlowEnvironment narrows 'age' to Int/Float.
        AdultContent(verified_age=age) // Type checker passes safely
    else:
        // Type narrowing propagates here as well.
        ChildContent(verified_age=age)
```
This perfectly exercises branch environments, `FlowEnvironment` isolation, conditional divergence, and scope popping, completely using existing syntax.

## 4. Whether Conditional Mutation is Truly Required
**NO.** Conditional state mutation inside `def` blocks is NOT required for A.6.
Assuming that A.6 needed conditional mutations was a conceptual error stemming from confusing imperative control-flow analysis with declarative data-flow analysis. TinPyUI can achieve robust, branch-sensitive type and data-flow facts exclusively using its existing declarative `ConditionalNode` structures.

## 5. Option A vs Option B Comparison

### Option A: Expand Syntax for Conditional Mutations Now
- **Architectural Correctness**: Low. Conflates data-flow analysis with imperative CFG generation.
- **Scope**: Massive expansion.
- **Compiler Complexity**: Requires rewriting the Parser, AST, IR Generator, and WASM runtime.
- **Release Risk**: Very High. Threatens the stability of the v1.8 release.

### Option B: Semantic Analysis of Existing UI Branches Only
- **Architectural Correctness**: High. Aligns perfectly with TinPyUI's declarative design philosophy.
- **Scope**: Tightly bounded to static analysis (`dataflow_analyzer.go` and `type_engine.go`).
- **Compiler Complexity**: Minimal. Pushing/popping `FlowEnvironment` maps requires zero structural AST/IR changes.
- **Release Risk**: Zero runtime risk, as Execution IR and WASM remain untouched.

## 6. Recommended Phase Boundary
A.6 should strictly adopt **Option B**. It must remain a purely semantic phase focused on `FlowEnvironment` scoping, type narrowing, and branch-aware diagnostics applied to existing `ConditionalNode` UI trees.

## 7. Proposed Future Phase (Deferred)
**Phase C.1 (or A.8): Executable Control-Flow & Conditional Mutations**
If TinPyUI ever requires imperative conditional logic (e.g., `if` inside `def`), it must be designed as a dedicated phase. This phase would strictly focus on Parser/AST expansion, CFG basic block generation, Execution IR jumps, and WASM runtime integration.

## 8. Exact A.6 Implementation Scope
- Implement `FlowEnvironment` stack pushing/popping inside `dataflow_analyzer.go` when visiting `ConditionalNode`.
- Implement Type Narrowing (e.g., if a condition compares an `Any` state to an `Int`, narrow that state to `Int` within the `FlowEnvironment` branch).
- Update caching to key off the active `FlowEnvironment` ID to prevent cross-branch cache pollution.
- Improve diagnostics to report localized type facts (e.g., "Variable 'age' is inferred as Int inside this branch").

## 9. Exact Deferred Scope
- NO conditional state mutation syntax.
- NO parser changes to `DefNode`.
- NO CFG execution semantics or loops.
- NO Execution IR or WASM modifications.
- NO complex branch-merging PHI nodes for mutated variables.

## 10. Final Authorization Recommendation
RECOMMENDATION: PROCEED WITH A.6 WITHOUT LANGUAGE EXTENSION

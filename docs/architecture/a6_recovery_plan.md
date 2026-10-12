# A.6 Recovery Plan

## 1. Last Known-Good Baseline
The baseline is the state of the repository immediately preceding the failed A.6 implementation. This encompasses the completion of A.5.2 (Advanced Data-Flow Propagation), where the compiler accurately resolved n-ary dependencies, cycles, and Any vs. Unknown types without introducing conditional mutations.

## 2. Failed Implementation Changes
The failed A.6 implementation incorrectly conflated declarative data-flow analysis with imperative control-flow generation. It introduced:
- `TrueBranch` and `FalseBranch` recursive slices inside `MutationNode` (`ast.go`).
- Conditional mutation parsing logic inside `def` blocks (`parser.go`).
- Recursive evaluation of conditional mutations in semantic and type analyzers (`semantic_analyzer.go`, `type_analyzer.go`).
- `FlowEnvironment` and deterministic `mergeTypes` applied to state mutations rather than declarative UI trees (`dataflow_analyzer.go`).
- Unauthorized Execution IR injection of `OpCreateConditional` inside the mutation instruction stream (`generator.go`).
- Invalid tests and `.tin` examples validating the unauthorized syntax.

## 3. KEEP Changes
No functional changes from the failed A.6 implementation should be kept, as they were all structurally applied to the wrong architectural boundary (mutations).
However, all legitimate pre-A.6 functionality MUST be strictly preserved, including:
- `Component` and `PropDecl` structures in `ast.go` (A.4.6).
- All semantic graph relationships and symbol indexing in `semantic_analyzer.go`.
- Expression semantics, literal inference, and strict widening rules in `type_engine.go` and `type_analyzer.go` (A.5.1).
- N-ary data-flow dependency tracking, cycle detection, and `Any`/`Unknown` resolution in `dataflow_analyzer.go` (A.5.2).

## 4. REMOVE Changes
The following unauthorized changes must be precisely removed:
- **ast.go**: Remove `ConditionVar`, `ConditionOp`, `ConditionVal`, `TrueBranch`, and `FalseBranch` from `MutationNode`.
- **parser.go**: Remove `parseIfMutation` and `parseMutationBlock`. Restore `parseDefStatement` to its flat, linear array parsing loop.
- **type_analyzer.go**: Remove the recursive `evaluateMutations` closure. Restore the flat iteration over `def.Mutations`.
- **semantic_analyzer.go**: Remove the recursive `processMutations` closure. Restore the flat iteration over `mut.Mutations`.
- **generator.go**: Remove the recursive `gen` closure and the `OpCreateConditional` injection. Restore flat iteration over `def.Mutations`.
- **dataflow_analyzer.go**: Remove the mutation-based `evaluateMutations` logic and `mergeTypes`. (The `FlowEnvironment` concept will be redesigned for UI traversal).
- **Tests**: Remove `TestDataFlowAnalyzerBranches` from `dataflow_analyzer_test.go`. Delete `a6_example_test.go` and `examples/a6/branch_analysis.tin`.

## 5. REVIEW Changes
- **dataflow_analyzer.go**: The `FlowEnvironment` struct definition itself. It is conceptually useful but needs to be decoupled from mutations and applied to `ConditionalNode` AST traversal.

## 6. Previous Phase Functionality That Must Be Preserved
- **A.4.6**: Component `Props`, cross-file component signatures, and semantic workspaces.
- **A.5.1 & A.5.2**: The Type Engine's exact rules for expressions, strict assignment rules (no state reassignment widening), and topological state resolution.
- **IR & WASM**: The Execution IR format must remain exactly as it was, and WASM runtime behavior must not change.
- **Tests**: The Python 104/104 baseline and all Go tests for pre-A.6 features.

## 7. Correct A.6 Architecture
A.6 must operate strictly on the EXISTING `ConditionalNode` inside the declarative UI tree (`RootNodes`).
The correct architecture is:
1. `DataFlowAnalyzer` visits `RootNodes`.
2. Upon encountering a `ConditionalNode`, it creates a localized `FlowEnvironment` derived from the parent scope.
3. It performs Type Narrowing on the condition variables (e.g., if `x > 10`, `x` is narrowed to `Int`/`Float` inside the true branch).
4. Any expressions evaluated within the true/false UI branches leverage the narrowed facts from the `FlowEnvironment`.
5. Upon exiting the branch, the `FlowEnvironment` is popped, restoring the parent's type knowledge.
There is no branch merging for mutated variables, because state is not mutated in the declarative UI.

## 8. FlowEnvironment Design
A minimal `FlowEnvironment`:
- Holds a pointer to its parent `FlowEnvironment`.
- Contains a local map of `TypeResult` overrides (type facts).
- `Get(key)` checks the local map; if missing, delegates to the parent.
- Does NOT mutate the global Semantic Workspace or the canonical Semantic Graph.
- Does NOT affect Execution IR.

## 9. Type Narrowing Rules
Narrowing must be based on the existing Type Engine capabilities.
- **Condition: `var > val` or `var < val`**
  - Fact: `var` is numeric.
  - Narrowing: If `var` is `Any`, narrow to `TypeFloat` (or union of Int/Float if supported, else `Any` with diagnostic). Since TinPyUI treats implicit numeric bounds as `Float` for maximum compatibility, it should narrow to `Float`, or defer to the Type Engine's `InferExpression`.
- **Condition: `var == true/false`**
  - Fact: `var` is `TypeBool` (or `Any` -> `TypeBool`).
- **Scope**: Narrowed types apply only to the `TrueBranch` of the `ConditionalNode`. The `FalseBranch` may infer the inverse (if safely applicable).
- **Exit Behavior**: The narrowed environment is discarded after the AST visitor leaves the `ConditionalNode`.

## 10. Existing `.tin` Test Matrix
The following tests must be implemented using existing public syntax:

1. **Type Narrowing on Any**
   - **Source**: `state dynamic: external_data` -> `if dynamic > 10:` -> `<Text text={dynamic} />`
   - **Expected Analysis**: `dynamic` is narrowed from `Any` to a numeric type inside the true branch.
   - **Requires New Syntax**: No.

2. **Branch Isolation**
   - **Source**: `state untyped: {val}` -> `if untyped == true:` -> `<A val={untyped} />` -> `else:` -> `<B val={untyped} />`
   - **Expected Analysis**: `untyped` is narrowed to `TypeBool` in the true branch, but remains `Any` in the false branch.
   - **Requires New Syntax**: No.

3. **Nested Branches**
   - **Source**: Nested `ConditionalNode` elements.
   - **Expected Analysis**: `FlowEnvironment` correctly inherits and stacks narrowing facts.
   - **Requires New Syntax**: No.

## 11. Execution Boundary
- A.6 analysis MUST NOT alter generated execution behavior.
- The same `.tin` source must produce the EXACT same Execution IR and WASM semantics as before.
- A.6 only enriches static type knowledge, data-flow facts, diagnostics, LSP, and Machine Protocol capabilities.

## 12. Recovery Steps
1. **Identify**: Confirm the exact legitimate pre-A.6 lines to preserve in `ast.go`, `parser.go`, `semantic_analyzer.go`, `type_analyzer.go`, and `generator.go`.
2. **Remove Logic**: Remove all recursive mutation logic, `parseIfMutation`, and `TrueBranch`/`FalseBranch` fields from `MutationNode`.
3. **Remove Files**: Delete `a6_example_test.go` and `examples/a6/branch_analysis.tin`. Remove the `TestDataFlowAnalyzerBranches` test.
4. **Restore**: Ensure the iteration logic in all compiler phases correctly processes `DefNode.Mutations` as a flat array.
5. **Verify Baseline**: Run all Go tests to ensure A.5.2 functionality is intact and no build errors exist.
6. **Implement Correct A.6**: Introduce `FlowEnvironment` strictly for `RootNodes` UI traversal in `dataflow_analyzer.go`.
7. **Create Tests**: Create valid `.tin` examples using `ConditionalNode` as per the test matrix.
8. **Final Validation**: Run full tests and perform an independent audit.

## 13. Verification Gates
Before A.6 implementation can proceed, the repository must return to:
- A.5.2 PASS
- Go tests PASS
- Python 104/104 PASS
- Existing `.tin` examples PASS
- Execution IR unchanged
- WASM unchanged
- No unauthorized syntax exists in the parser or AST.

## 14. Implementation Authorization Conditions
NO recovery implementation is authorized by this audit.
The exact diff removal must be performed and verified against the A.5.2 baseline before new A.6 work begins.

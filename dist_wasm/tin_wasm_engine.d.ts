declare namespace wasm_bindgen {
	/* tslint:disable */
	/* eslint-disable */
	export function main_js(): void;
	export function BootTinUI(ir_json: string): string;
	export function TinUIMutateState(key: string, new_value: string): void;
	export function TinUIDispatchApi(action: string): void;
	export function TinUISnapshot(): number;
	export function TinUIRestore(idx: number): boolean;
	export function TinUIReloadShader(canvas_id: string, fragment_code: string): boolean;
	export function TinUICompileShader(fragment_code: string): boolean;
	
}

declare type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

declare interface InitOutput {
  readonly memory: WebAssembly.Memory;
  readonly BootTinUI: (a: number, b: number, c: number) => void;
  readonly TinUICompileShader: (a: number, b: number) => number;
  readonly TinUIDispatchApi: (a: number, b: number, c: number) => void;
  readonly TinUIMutateState: (a: number, b: number, c: number, d: number, e: number) => void;
  readonly TinUIReloadShader: (a: number, b: number, c: number, d: number) => number;
  readonly TinUIRestore: (a: number, b: number) => void;
  readonly TinUISnapshot: () => number;
  readonly main_js: () => void;
  readonly __wbindgen_export_0: (a: number) => void;
  readonly __wbindgen_export_1: (a: number, b: number) => number;
  readonly __wbindgen_export_2: (a: number, b: number, c: number, d: number) => number;
  readonly __wbindgen_export_3: WebAssembly.Table;
  readonly __wbindgen_add_to_stack_pointer: (a: number) => number;
  readonly __wbindgen_export_4: (a: number, b: number, c: number) => void;
  readonly __wbindgen_export_5: (a: number, b: number, c: number) => void;
  readonly __wbindgen_export_6: (a: number, b: number) => void;
  readonly __wbindgen_start: () => void;
}

/**
* If `module_or_path` is {RequestInfo} or {URL}, makes a request and
* for everything else, calls `WebAssembly.instantiate` directly.
*
* @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
*
* @returns {Promise<InitOutput>}
*/
declare function wasm_bindgen (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;

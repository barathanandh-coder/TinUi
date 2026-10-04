use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::{Document, Element, HtmlElement, Window};

pub mod types;
pub mod reactive;
pub mod shader;
pub mod dom;

use types::{IRBlueprint, ENGINE_CSS};
use reactive::*;
use dom::*;
use shader::*;

#[wasm_bindgen(start)]
pub fn main_js() -> Result<(), JsValue> {
    init_reactive();
    init_dom_store();

    // Attach global hooks to window for backward compatibility
    let window = web_sys::window().expect("global window not found");
    let global_obj = js_sys::Reflect::get(&window, &JsValue::from_str("window"))?;

    // Set engine signature
    js_sys::Reflect::set(&global_obj, &JsValue::from_str("__TIN_ENGINE__"), &JsValue::from_str("Rust-WASM-v1.8.0"))?;

    Ok(())
}

#[wasm_bindgen(js_name = BootTinUI)]
pub fn boot_tin_ui(ir_json: &str) -> Result<String, JsValue> {
    init_reactive();
    init_dom_store();

    let window = web_sys::window().ok_or_else(|| JsValue::from_str("Window not found"))?;
    let doc = window.document().ok_or_else(|| JsValue::from_str("Document not found"))?;

    let blueprint: IRBlueprint = serde_json::from_str(ir_json)
        .map_err(|e| JsValue::from_str(&format!("JSON Parse Error: {:?}", e)))?;

    set_dynamic_mutations(blueprint.mutations);

    // Inject engine CSS
    if let Ok(style_el) = doc.create_element("style") {
        style_el.set_inner_html(ENGINE_CSS);
        if let Some(head) = doc.head() {
            let _ = head.append_child(&style_el);
        }
    }

    // Identify root container
    let root_el = if let Some(r) = doc.get_element_by_id("tinui-root") {
        r.set_inner_html("");
        r
    } else if let Some(b) = doc.body() {
        b.into()
    } else {
        return Err(JsValue::from_str("No document body found"));
    };

    set_dom_node(0, root_el);

    // Render nodes
    for inst in &blueprint.nodes {
        execute_instruction(inst, &doc, None);
    }

    // Hydrate input listeners and actions
    setup_event_delegation(&doc)?;
    setup_scroll_listeners(&window)?;

    Ok("TinUI Rust WASM Engine Booted".to_string())
}

#[wasm_bindgen(js_name = TinUIMutateState)]
pub fn tin_ui_mutate_state(key: &str, new_value: &str) -> Result<(), JsValue> {
    mutate_state_internal(key, new_value);

    let window = web_sys::window().ok_or_else(|| JsValue::from_str("Window not found"))?;
    let doc = window.document().ok_or_else(|| JsValue::from_str("Document not found"))?;

    flush_patches(&doc);
    Ok(())
}

#[wasm_bindgen(js_name = TinUIDispatchApi)]
pub fn tin_ui_dispatch_api(action: &str) -> Result<(), JsValue> {
    web_sys::console::log_1(&JsValue::from_str(&format!("[TinUI Rust Engine] Dispatch API action: {}", action)));
    Ok(())
}

#[wasm_bindgen(js_name = TinUISnapshot)]
pub fn tin_ui_snapshot() -> usize {
    take_snapshot_internal()
}

#[wasm_bindgen(js_name = TinUIRestore)]
pub fn tin_ui_restore(idx: usize) -> Result<bool, JsValue> {
    let success = restore_snapshot_internal(idx);
    if success {
        let window = web_sys::window().ok_or_else(|| JsValue::from_str("Window not found"))?;
        let doc = window.document().ok_or_else(|| JsValue::from_str("Document not found"))?;
        flush_patches(&doc);
    }
    Ok(success)
}

#[wasm_bindgen(js_name = TinUIReloadShader)]
pub fn tin_ui_reload_shader(canvas_id: &str, fragment_code: &str) -> bool {
    let window = match web_sys::window() {
        Some(w) => w,
        None => return false,
    };
    let doc = match window.document() {
        Some(d) => d,
        None => return false,
    };
    let el = match doc.get_element_by_id(canvas_id) {
        Some(e) => e,
        None => return false,
    };
    if let Ok(canvas) = el.dyn_into::<web_sys::HtmlCanvasElement>() {
        reload_webgl_shader(&canvas, fragment_code)
    } else {
        false
    }
}

#[wasm_bindgen(js_name = TinUICompileShader)]
pub fn tin_ui_compile_shader(fragment_code: &str) -> bool {
    let window = match web_sys::window() {
        Some(w) => w,
        None => return false,
    };
    let doc = match window.document() {
        Some(d) => d,
        None => return false,
    };
    let canvas = match doc.create_element("canvas") {
        Ok(c) => c,
        Err(_) => return false,
    };
    let canvas: web_sys::HtmlCanvasElement = match canvas.dyn_into() {
        Ok(c) => c,
        Err(_) => return false,
    };
    let gl_context = match canvas.get_context("webgl") {
        Ok(Some(ctx)) => ctx,
        _ => return false,
    };
    let gl: web_sys::WebGlRenderingContext = match gl_context.dyn_into() {
        Ok(g) => g,
        Err(_) => return false,
    };

    let frag_src = ensure_precision(fragment_code);
    match compile_shader(&gl, web_sys::WebGlRenderingContext::FRAGMENT_SHADER, &frag_src) {
        Ok(s) => {
            gl.delete_shader(Some(&s));
            true
        }
        Err(_) => false,
    }
}

fn setup_event_delegation(doc: &Document) -> Result<(), JsValue> {
    let click_closure = Closure::wrap(Box::new(move |event: web_sys::MouseEvent| {
        if let Some(target) = event.target() {
            if let Ok(el) = target.dyn_into::<Element>() {
                if let Some(action) = el.get_attribute("data-action") {
                    let window = web_sys::window().unwrap();
                    let doc = window.document().unwrap();

                    let mut matched = false;
                    DYNAMIC_MUTATIONS.with(|mutations_guard| {
                        let map = mutations_guard.borrow();
                        if let Some(instructions) = map.get(&action) {
                            matched = true;
                            for inst in instructions {
                                execute_instruction(inst, &doc, None);
                            }
                            flush_patches(&doc);
                        }
                    });

                    if matched {
                        return;
                    }

                    // Simple state increment fallback e.g. "counter += 1"
                    if action.contains("+=") {
                        let parts: Vec<&str> = action.split("+=").collect();
                        if parts.len() == 2 {
                            let key = parts[0].trim();
                            let current_str = get_state_str(key);
                            let current_int = current_str.parse::<i64>().unwrap_or(0);
                            let add_int = parts[1].trim().parse::<i64>().unwrap_or(1);
                            let new_val = (current_int + add_int).to_string();
                            mutate_state_internal(key, &new_val);
                            flush_patches(&doc);
                        }
                    }
                }
            }
        }
    }) as Box<dyn FnMut(_)>);

    doc.add_event_listener_with_callback("click", click_closure.as_ref().unchecked_ref())?;
    click_closure.forget();

    let input_closure = Closure::wrap(Box::new(move |event: web_sys::Event| {
        if let Some(target) = event.target() {
            if let Ok(input_el) = target.dyn_into::<web_sys::HtmlInputElement>() {
                if let Some(bind_key) = input_el.get_attribute("data-bind") {
                    let val = input_el.value();
                    mutate_state_internal(&bind_key, &val);
                    let window = web_sys::window().unwrap();
                    let doc = window.document().unwrap();
                    flush_patches(&doc);
                }
            }
        }
    }) as Box<dyn FnMut(_)>);

    doc.add_event_listener_with_callback("input", input_closure.as_ref().unchecked_ref())?;
    input_closure.forget();

    Ok(())
}

fn setup_scroll_listeners(window: &Window) -> Result<(), JsValue> {
    let scroll_closure = Closure::wrap(Box::new(move || {
        if let Some(window) = web_sys::window() {
            if let Ok(scroll_y) = window.scroll_y() {
                PARALLAX_NODES.with(|pn_guard| {
                    let nodes = pn_guard.borrow();
                    for p in nodes.iter() {
                        if let Some(el) = get_dom_node(p.id) {
                            if let Ok(html_el) = el.dyn_into::<HtmlElement>() {
                                let offset = scroll_y * p.speed;
                                let _ = html_el.style().set_property("transform", &format!("translateY({:.2}px)", offset));
                            }
                        }
                    }
                });
            }
        }
    }) as Box<dyn FnMut()>);

    window.add_event_listener_with_callback("scroll", scroll_closure.as_ref().unchecked_ref())?;
    scroll_closure.forget();

    Ok(())
}

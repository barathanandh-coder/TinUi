use wasm_bindgen::JsCast;
use web_sys::{Document, Element, HtmlElement, HtmlInputElement};
use std::collections::HashMap;
use std::cell::RefCell;

use crate::types::*;
use crate::reactive::*;
use crate::shader::init_webgl_shader;

thread_local! {
    pub static DOM_REFS: RefCell<HashMap<i32, Element>> = RefCell::new(HashMap::new());
    pub static DYNAMIC_MUTATIONS: RefCell<HashMap<String, Vec<Instruction>>> = RefCell::new(HashMap::new());
    pub static TEXT_BINDINGS: RefCell<HashMap<i32, TextBinding>> = RefCell::new(HashMap::new());
    pub static CONDITIONAL_BINDINGS: RefCell<HashMap<i32, ConditionalBinding>> = RefCell::new(HashMap::new());
    pub static LIST_BINDINGS: RefCell<HashMap<i32, ListBinding>> = RefCell::new(HashMap::new());
    pub static LOADING_BINDINGS: RefCell<HashMap<i32, LoadingBinding>> = RefCell::new(HashMap::new());
    pub static PARALLAX_NODES: RefCell<Vec<ParallaxNode>> = RefCell::new(Vec::new());
}

pub fn init_dom_store() {
    // Thread-locals auto-initialize
}

pub fn get_dom_node(id: i32) -> Option<Element> {
    DOM_REFS.with(|refs| refs.borrow().get(&id).cloned())
}

pub fn set_dom_node(id: i32, el: Element) {
    DOM_REFS.with(|refs| {
        refs.borrow_mut().insert(id, el);
    });
}

pub fn set_dynamic_mutations(mutations: HashMap<String, Vec<Instruction>>) {
    DYNAMIC_MUTATIONS.with(|m| {
        *m.borrow_mut() = mutations;
    });
}

pub fn execute_instruction(inst: &Instruction, doc: &Document, scope: Option<&HashMap<String, String>>) {
    match inst.op.as_str() {
        "CREATE_NODE" => {
            let tag = inst.tag.as_deref().unwrap_or("div");
            if let Ok(el) = doc.create_element(tag) {
                if let Some(id) = inst.id {
                    let _ = el.set_attribute("id", &format!("tin-node-{}", id));
                    if inst.is_hidden {
                        if let Ok(html_el) = el.clone().dyn_into::<HtmlElement>() {
                            let _ = html_el.style().set_property("display", "none");
                        }
                    }
                    set_dom_node(id, el);
                }
            }
        }
        "DECLARE_STATE" => {
            if let (Some(key), Some(st_type), Some(init_val)) = (&inst.key, &inst.prop_type, &inst.initial) {
                register_state(key, st_type, init_val);
            }
        }
        "BIND_TEXT" => {
            if let Some(id) = inst.id {
                let template = inst.template.clone().unwrap_or_default();
                let state_keys = inst.state_keys.clone();
                let initial_text = format_template(&template, &state_keys, scope);

                TEXT_BINDINGS.with(|tb| {
                    tb.borrow_mut().insert(id, TextBinding {
                        template,
                        state_keys,
                        scope: scope.cloned(),
                    });
                });

                if let Some(el) = get_dom_node(id) {
                    if let Ok(html_el) = el.dyn_into::<HtmlElement>() {
                        html_el.set_inner_text(&initial_text);
                    }
                }
            }
        }
        "SET_TEXT" => {
            if let (Some(id), Some(val)) = (inst.id, &inst.value) {
                if let Some(el) = get_dom_node(id) {
                    let tag = el.tag_name().to_uppercase();
                    if ["BUTTON", "P", "SPAN", "A", "H1", "H2", "H3", "H4", "H5", "H6"].contains(&tag.as_str()) {
                        el.set_text_content(Some(val));
                    } else if let Ok(html_el) = el.dyn_into::<HtmlElement>() {
                        html_el.set_inner_text(val);
                    }
                }
            }
        }
        "SET_ATTRIBUTE" => {
            if let (Some(id), Some(k), Some(v)) = (inst.id, &inst.key, &inst.value) {
                if let Some(el) = get_dom_node(id) {
                    let _ = el.set_attribute(k, v);
                    if k == "style" {
                        if let Ok(html_el) = el.clone().dyn_into::<HtmlElement>() {
                            let _ = html_el.style().set_property("cssText", v);
                        }
                    }
                    if k == "data-shader-code" {
                        if let Ok(canvas) = el.clone().dyn_into::<web_sys::HtmlCanvasElement>() {
                            let _ = init_webgl_shader(canvas, v);
                        }
                    }
                    if k == "data-parallax-speed" {
                        if let Ok(speed) = v.parse::<f64>() {
                            PARALLAX_NODES.with(|pn| {
                                pn.borrow_mut().push(ParallaxNode { id, speed });
                            });
                        }
                    }
                }
            }
        }
        "APPEND_CHILD" => {
            if let (Some(parent_id), Some(child_id)) = (inst.parent, inst.child) {
                if let (Some(parent_el), Some(child_el)) = (get_dom_node(parent_id), get_dom_node(child_id)) {
                    let _ = parent_el.append_child(&child_el);
                }
            }
        }
        "ADD_EVENT" => {
            if let (Some(id), Some(mutation)) = (inst.id, &inst.mutation) {
                if let Some(el) = get_dom_node(id) {
                    let _ = el.set_attribute("data-action", mutation);
                }
            }
        }
        "BIND_INPUT" => {
            if let (Some(id), Some(state_key)) = (inst.id, &inst.state_key) {
                if let Some(el) = get_dom_node(id) {
                    let _ = el.set_attribute("data-bind", state_key);
                    let val = get_state_str(state_key);
                    if let Ok(input_el) = el.dyn_into::<HtmlInputElement>() {
                        input_el.set_value(&val);
                    }
                }
            }
        }
        "BIND_LOADING" => {
            if let (Some(id), Some(state_key)) = (inst.id, &inst.state_key) {
                let loader_type = inst.tag.clone().unwrap_or_else(|| "spinner".into());
                let loader_speed = inst.value.clone().unwrap_or_else(|| "1s".into());
                LOADING_BINDINGS.with(|lb| {
                    lb.borrow_mut().insert(id, LoadingBinding {
                        state_key: state_key.clone(),
                        loader_type,
                        loader_speed,
                    });
                });
            }
        }
        "CREATE_CONDITIONAL" => {
            if let (Some(id), Some(parent_id), Some(state_key), Some(op), Some(cmp)) = 
                (inst.id, inst.parent, &inst.state_key, &inst.operator, &inst.compare_val) 
            {
                if let Ok(anchor) = doc.create_element("div") {
                    let _ = anchor.set_attribute("style", "display: contents;");
                    set_dom_node(id, anchor.clone());

                    if let Some(parent_el) = get_dom_node(parent_id) {
                        let _ = parent_el.append_child(&anchor);
                    }

                    let initial_bool = eval_condition(state_key, op, cmp);
                    let binding = ConditionalBinding {
                        state_key: state_key.clone(),
                        operator: op.clone(),
                        compare_val: cmp.clone(),
                        true_branch: inst.true_branch.clone(),
                        false_branch: inst.false_branch.clone(),
                        current_bool: initial_bool,
                    };

                    CONDITIONAL_BINDINGS.with(|cb| {
                        cb.borrow_mut().insert(id, binding);
                    });

                    let branch = if initial_bool { &inst.true_branch } else { &inst.false_branch };
                    for child_inst in branch {
                        let mut copy = child_inst.clone();
                        copy.parent = Some(id);
                        execute_instruction(&copy, doc, scope);
                    }
                }
            }
        }
        "RENDER_LIST" => {
            if let (Some(id), Some(parent_id), Some(iter_key), Some(iter_name)) = 
                (inst.id, inst.parent, &inst.iterable_key, &inst.iterator_name)
            {
                if let Ok(anchor) = doc.create_element("div") {
                    let _ = anchor.set_attribute("style", "display: contents;");
                    set_dom_node(id, anchor.clone());

                    if let Some(parent_el) = get_dom_node(parent_id) {
                        let _ = parent_el.append_child(&anchor);
                    }

                    let binding = ListBinding {
                        iterable_key: iter_key.clone(),
                        iterator_name: iter_name.clone(),
                        loop_template: inst.loop_template.clone(),
                    };

                    LIST_BINDINGS.with(|lb| {
                        lb.borrow_mut().insert(id, binding);
                    });

                    render_list_dom(id, doc);
                }
            }
        }
        _ => {}
    }
}

pub fn render_list_dom(anchor_id: i32, doc: &Document) {
    let binding = LIST_BINDINGS.with(|lb| lb.borrow().get(&anchor_id).cloned());

    let binding = match binding {
        Some(b) => b,
        None => return,
    };

    let raw_json = get_state_str(&binding.iterable_key);
    let items: Vec<serde_json::Value> = serde_json::from_str(&raw_json).unwrap_or_default();

    if let Some(anchor) = get_dom_node(anchor_id) {
        anchor.set_inner_html("");

        for item in items {
            let mut local_scope = HashMap::new();
            if let Some(obj) = item.as_object() {
                for (k, v) in obj {
                    let val_str = if let Some(s) = v.as_str() {
                        s.to_string()
                    } else {
                        v.to_string()
                    };
                    local_scope.insert(format!("{}.{}", binding.iterator_name, k), val_str);
                }
            } else {
                let val_str = if let Some(s) = item.as_str() {
                    s.to_string()
                } else {
                    item.to_string()
                };
                local_scope.insert(binding.iterator_name.clone(), val_str);
            }

            for child_inst in &binding.loop_template {
                let mut copy = child_inst.clone();
                copy.parent = Some(anchor_id);
                execute_instruction(&copy, doc, Some(&local_scope));
            }
        }
    }
}

pub fn flush_patches(doc: &Document) {
    // 1. Flush text bindings
    let text_bindings: Vec<(i32, TextBinding)> = TEXT_BINDINGS.with(|tb| {
        tb.borrow().iter().map(|(k, v)| (*k, v.clone())).collect()
    });

    for (id, binding) in text_bindings {
        let should_update = binding.state_keys.iter().any(|k| is_dirty(k));
        if should_update {
            let updated_text = format_template(&binding.template, &binding.state_keys, binding.scope.as_ref());
            if let Some(el) = get_dom_node(id) {
                if let Ok(html_el) = el.dyn_into::<HtmlElement>() {
                    html_el.set_inner_text(&updated_text);
                }
            }
        }
    }

    // 2. Flush conditional bindings
    let conditional_bindings: Vec<(i32, ConditionalBinding)> = CONDITIONAL_BINDINGS.with(|cb| {
        cb.borrow().iter().map(|(k, v)| (*k, v.clone())).collect()
    });

    for (id, mut binding) in conditional_bindings {
        if is_dirty(&binding.state_key) {
            let new_bool = eval_condition(&binding.state_key, &binding.operator, &binding.compare_val);
            if new_bool != binding.current_bool {
                binding.current_bool = new_bool;
                if let Some(anchor) = get_dom_node(id) {
                    anchor.set_inner_html("");
                    let branch = if new_bool { &binding.true_branch } else { &binding.false_branch };
                    for child_inst in branch {
                        let mut copy = child_inst.clone();
                        copy.parent = Some(id);
                        execute_instruction(&copy, doc, None);
                    }
                }
                CONDITIONAL_BINDINGS.with(|cb| {
                    cb.borrow_mut().insert(id, binding);
                });
            }
        }
    }

    // 3. Flush list bindings
    let list_bindings: Vec<(i32, ListBinding)> = LIST_BINDINGS.with(|lb| {
        lb.borrow().iter().map(|(k, v)| (*k, v.clone())).collect()
    });

    for (id, binding) in list_bindings {
        if is_dirty(&binding.iterable_key) {
            render_list_dom(id, doc);
        }
    }

    clear_all_dirty_bits();
}

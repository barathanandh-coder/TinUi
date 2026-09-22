use std::collections::{HashMap, HashSet};
use std::cell::RefCell;
use crate::types::StateEntry;

thread_local! {
    pub static STATE_REGISTRY: RefCell<HashMap<String, StateEntry>> = RefCell::new(HashMap::new());
    pub static DIRTY_KEYS: RefCell<HashSet<String>> = RefCell::new(HashSet::new());
    pub static STATE_HISTORY: RefCell<Vec<HashMap<String, StateEntry>>> = RefCell::new(Vec::new());
}

pub fn init_reactive() {
    // Thread-locals auto-initialize
}

pub fn register_state(key: &str, state_type: &str, initial: &str) {
    let int_val = if state_type == "int" {
        initial.parse::<i64>().unwrap_or(0)
    } else {
        0
    };
    STATE_REGISTRY.with(|reg| {
        reg.borrow_mut().insert(
            key.to_string(),
            StateEntry {
                state_type: state_type.to_string(),
                str_val: initial.to_string(),
                int_val,
            },
        );
    });
}

pub fn get_state_str(key: &str) -> String {
    STATE_REGISTRY.with(|reg| {
        reg.borrow().get(key).map(|e| e.str_val.clone()).unwrap_or_default()
    })
}

pub fn mutate_state_internal(key: &str, new_value: &str) {
    STATE_REGISTRY.with(|reg| {
        let mut map = reg.borrow_mut();
        if let Some(entry) = map.get_mut(key) {
            entry.str_val = new_value.to_string();
            if entry.state_type == "int" {
                if let Ok(v) = new_value.parse::<i64>() {
                    entry.int_val = v;
                }
            }
        } else {
            map.insert(
                key.to_string(),
                StateEntry {
                    state_type: "string".to_string(),
                    str_val: new_value.to_string(),
                    int_val: 0,
                },
            );
        }
    });

    DIRTY_KEYS.with(|dirty| {
        dirty.borrow_mut().insert(key.to_string());
    });
}

pub fn is_dirty(key: &str) -> bool {
    DIRTY_KEYS.with(|dirty| dirty.borrow().contains(key))
}

pub fn clear_all_dirty_bits() {
    DIRTY_KEYS.with(|dirty| dirty.borrow_mut().clear());
}

pub fn format_template(template: &str, keys: &[String], scope: Option<&HashMap<String, String>>) -> String {
    let mut result = template.to_string();

    // 1. Interpolate local scope (loops)
    if let Some(s) = scope {
        for (k, v) in s {
            let placeholder = format!("{{{}}}", k);
            result = result.replace(&placeholder, v);
        }
    }

    // 2. Interpolate global state keys
    STATE_REGISTRY.with(|reg| {
        let map = reg.borrow();
        for key in keys {
            let placeholder = format!("{{{}}}", key);
            let val = if let Some(entry) = map.get(key) {
                entry.str_val.as_str()
            } else {
                ""
            };
            result = result.replace(&placeholder, val);
        }
    });

    result
}

pub fn eval_condition(state_key: &str, operator: &str, compare_val_str: &str) -> bool {
    let entry = STATE_REGISTRY.with(|reg| reg.borrow().get(state_key).cloned());

    let entry = match entry {
        Some(e) => e,
        None => return false,
    };

    if entry.state_type == "int" {
        let current = entry.int_val;
        let compare = compare_val_str.parse::<i64>().unwrap_or(0);
        match operator {
            ">" => current > compare,
            "<" => current < compare,
            ">=" => current >= compare,
            "<=" => current <= compare,
            "==" => current == compare,
            "!=" => current != compare,
            _ => false,
        }
    } else if entry.state_type == "bool" {
        let current = entry.str_val == "true";
        let compare = compare_val_str == "true";
        match operator {
            "==" => current == compare,
            "!=" => current != compare,
            _ => false,
        }
    } else {
        match operator {
            "==" => entry.str_val == compare_val_str,
            "!=" => entry.str_val != compare_val_str,
            _ => false,
        }
    }
}

pub fn take_snapshot_internal() -> usize {
    let current_state = STATE_REGISTRY.with(|reg| reg.borrow().clone());
    STATE_HISTORY.with(|hist| {
        let mut h = hist.borrow_mut();
        h.push(current_state);
        h.len() - 1
    })
}

pub fn restore_snapshot_internal(idx: usize) -> bool {
    let target = STATE_HISTORY.with(|hist| hist.borrow().get(idx).cloned());
    if let Some(state) = target {
        STATE_REGISTRY.with(|reg| {
            *reg.borrow_mut() = state;
        });
        true
    } else {
        false
    }
}

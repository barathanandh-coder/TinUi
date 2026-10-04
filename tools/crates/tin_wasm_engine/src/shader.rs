use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::{HtmlCanvasElement, WebGlRenderingContext as GL, WebGlShader, WebGlProgram, WebGlBuffer};
use std::collections::HashMap;
use std::cell::RefCell;

pub const DEFAULT_VERTEX_SHADER: &str = r#"
attribute vec2 position;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
}
"#;

pub struct ShaderInstance {
    pub canvas: HtmlCanvasElement,
    pub gl: GL,
    pub program: WebGlProgram,
    pub quad_buffer: WebGlBuffer,
    pub pos_attrib: u32,
    pub time_loc: Option<web_sys::WebGlUniformLocation>,
    pub res_loc: Option<web_sys::WebGlUniformLocation>,
    pub mouse_loc: Option<web_sys::WebGlUniformLocation>,
    pub start_time: f64,
}

thread_local! {
    pub static ACTIVE_SHADERS: RefCell<HashMap<String, ShaderInstance>> = RefCell::new(HashMap::new());
}

pub fn ensure_precision(code: &str) -> String {
    if !code.contains("precision ") {
        format!("precision highp float;\n{}", code)
    } else {
        code.to_string()
    }
}

pub fn compile_shader(gl: &GL, shader_type: u32, source: &str) -> Result<WebGlShader, String> {
    let shader = gl
        .create_shader(shader_type)
        .ok_or_else(|| "Unable to create shader object".to_string())?;

    gl.shader_source(&shader, source);
    gl.compile_shader(&shader);

    if gl
        .get_shader_parameter(&shader, GL::COMPILE_STATUS)
        .as_bool()
        .unwrap_or(false)
    {
        Ok(shader)
    } else {
        let log = gl.get_shader_info_log(&shader).unwrap_or_else(|| "Unknown error".into());
        gl.delete_shader(Some(&shader));
        Err(format!("Shader compile failed: {}", log))
    }
}

pub fn link_program(gl: &GL, vert: &WebGlShader, frag: &WebGlShader) -> Result<WebGlProgram, String> {
    let program = gl
        .create_program()
        .ok_or_else(|| "Unable to create shader program".to_string())?;

    gl.attach_shader(&program, vert);
    gl.attach_shader(&program, frag);
    gl.link_program(&program);

    if gl
        .get_program_parameter(&program, GL::LINK_STATUS)
        .as_bool()
        .unwrap_or(false)
    {
        Ok(program)
    } else {
        let log = gl.get_program_info_log(&program).unwrap_or_else(|| "Unknown link error".into());
        gl.delete_program(Some(&program));
        Err(format!("Shader link failed: {}", log))
    }
}

pub fn create_quad_buffer(gl: &GL) -> Result<WebGlBuffer, String> {
    let buffer = gl
        .create_buffer()
        .ok_or_else(|| "Failed to create quad buffer".to_string())?;

    gl.bind_buffer(GL::ARRAY_BUFFER, Some(&buffer));

    let vertices: [f32; 12] = [
        -1.0, -1.0,
         1.0, -1.0,
        -1.0,  1.0,
        -1.0,  1.0,
         1.0, -1.0,
         1.0,  1.0,
    ];

    unsafe {
        let vert_array = js_sys::Float32Array::view(&vertices);
        gl.buffer_data_with_array_buffer_view(GL::ARRAY_BUFFER, &vert_array, GL::STATIC_DRAW);
    }

    Ok(buffer)
}

pub fn init_webgl_shader(canvas: HtmlCanvasElement, fragment_code: &str) -> Result<(), String> {
    let gl_context = canvas
        .get_context("webgl")
        .map_err(|e| format!("{:?}", e))?
        .or_else(|| canvas.get_context("experimental-webgl").ok().flatten())
        .ok_or_else(|| "WebGL not supported".to_string())?;

    let gl: GL = gl_context.dyn_into().map_err(|_| "Failed to cast to WebGLRenderingContext")?;

    let vert = compile_shader(&gl, GL::VERTEX_SHADER, DEFAULT_VERTEX_SHADER)?;
    let frag_src = ensure_precision(fragment_code);
    let frag = compile_shader(&gl, GL::FRAGMENT_SHADER, &frag_src)?;
    let program = link_program(&gl, &vert, &frag)?;

    let quad = create_quad_buffer(&gl)?;
    let pos_loc = gl.get_attrib_location(&program, "position");
    if pos_loc >= 0 {
        gl.enable_vertex_attrib_array(pos_loc as u32);
        gl.vertex_attrib_pointer_with_i32(pos_loc as u32, 2, GL::FLOAT, false, 0, 0);
    }

    let time_loc = gl.get_uniform_location(&program, "u_time");
    let res_loc = gl.get_uniform_location(&program, "u_resolution");
    let mouse_loc = gl.get_uniform_location(&program, "u_mouse");

    let window = web_sys::window().unwrap();
    let performance = window.performance().unwrap();
    let start_time = performance.now();

    let canvas_id = canvas.id();
    let key = if canvas_id.is_empty() {
        format!("canvas_{:?}", start_time)
    } else {
        canvas_id
    };

    let instance = ShaderInstance {
        canvas,
        gl,
        program,
        quad_buffer: quad,
        pos_attrib: if pos_loc >= 0 { pos_loc as u32 } else { 0 },
        time_loc,
        res_loc,
        mouse_loc,
        start_time,
    };

    ACTIVE_SHADERS.with(|shaders| {
        shaders.borrow_mut().insert(key.clone(), instance);
    });

    start_render_loop(key);

    Ok(())
}

fn start_render_loop(key: String) {
    use std::rc::Rc;

    let f: Rc<RefCell<Option<Closure<dyn FnMut()>>>> = Rc::new(RefCell::new(None));
    let g = f.clone();

    let key_clone = key.clone();
    *g.borrow_mut() = Some(Closure::wrap(Box::new(move || {
        let mut remove = false;

        ACTIVE_SHADERS.with(|shaders| {
            let map = shaders.borrow();
            if let Some(inst) = map.get(&key_clone) {
                let gl = &inst.gl;
                let width = inst.canvas.width() as f32;
                let height = inst.canvas.height() as f32;

                gl.viewport(0, 0, width as i32, height as i32);
                gl.use_program(Some(&inst.program));

                if let Some(res) = &inst.res_loc {
                    gl.uniform2f(Some(res), width, height);
                }

                if let Some(tl) = &inst.time_loc {
                    if let Some(window) = web_sys::window() {
                        if let Some(perf) = window.performance() {
                            let elapsed = ((perf.now() - inst.start_time) / 1000.0) as f32;
                            gl.uniform1f(Some(tl), elapsed);
                        }
                    }
                }

                gl.bind_buffer(GL::ARRAY_BUFFER, Some(&inst.quad_buffer));
                gl.draw_arrays(GL::TRIANGLES, 0, 6);
            } else {
                remove = true;
            }
        });

        if !remove {
            if let Some(window) = web_sys::window() {
                let _ = window.request_animation_frame(
                    f.borrow().as_ref().unwrap().as_ref().unchecked_ref(),
                );
            }
        }
    }) as Box<dyn FnMut()>));

    if let Some(window) = web_sys::window() {
        let _ = window.request_animation_frame(
            g.borrow().as_ref().unwrap().as_ref().unchecked_ref(),
        );
    }
}

pub fn reload_webgl_shader(canvas: &HtmlCanvasElement, fragment_code: &str) -> bool {
    let gl_context = match canvas.get_context("webgl") {
        Ok(Some(ctx)) => ctx,
        _ => return false,
    };
    let gl: GL = match gl_context.dyn_into() {
        Ok(gl) => gl,
        Err(_) => return false,
    };

    let vert = match compile_shader(&gl, GL::VERTEX_SHADER, DEFAULT_VERTEX_SHADER) {
        Ok(s) => s,
        Err(_) => return false,
    };
    let frag_src = ensure_precision(fragment_code);
    let frag = match compile_shader(&gl, GL::FRAGMENT_SHADER, &frag_src) {
        Ok(s) => s,
        Err(_) => return false,
    };
    let program = match link_program(&gl, &vert, &frag) {
        Ok(p) => p,
        Err(_) => return false,
    };

    let canvas_id = canvas.id();
    ACTIVE_SHADERS.with(|shaders| {
        let mut map = shaders.borrow_mut();
        if let Some(inst) = map.get_mut(&canvas_id) {
            inst.program = program;
            inst.time_loc = gl.get_uniform_location(&inst.program, "u_time");
            inst.res_loc = gl.get_uniform_location(&inst.program, "u_resolution");
            inst.mouse_loc = gl.get_uniform_location(&inst.program, "u_mouse");
            true
        } else {
            false
        }
    })
}

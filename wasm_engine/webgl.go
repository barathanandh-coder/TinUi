package main

import (
	"fmt"
	"strings"
	"syscall/js"
)

// Default vertex shader: covers the entire canvas with a quad
const defaultVertexShader = `
attribute vec2 position;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
}
`

// initWebGLShader sets up the WebGL context, compiles the shader program, and starts the render loop.
func initWebGLShader(canvas js.Value, fragmentCode string) {
	window := js.Global().Get("window")

	// Get WebGL context
	gl := canvas.Call("getContext", "webgl")
	if gl.IsNull() || gl.IsUndefined() {
		gl = canvas.Call("getContext", "experimental-webgl")
		if gl.IsNull() || gl.IsUndefined() {
			fmt.Println("WebGL not supported in this browser.")
			return
		}
	}

	fullFragmentShader := fragmentCode
	if !strings.Contains(fragmentCode, "precision") {
		fullFragmentShader = "precision highp float;\n" + fullFragmentShader
	}
	if !strings.Contains(fragmentCode, "uniform float u_time;") {
		fullFragmentShader = "uniform float u_time;\n" + fullFragmentShader
	}
	if !strings.Contains(fragmentCode, "uniform vec2 u_resolution;") {
		fullFragmentShader = "uniform vec2 u_resolution;\n" + fullFragmentShader
	}

	// Compile shaders
	program := createProgram(gl, defaultVertexShader, fullFragmentShader)
	if program.IsNull() {
		return // compilation failed
	}

	gl.Call("useProgram", program)

	// Look up uniform locations
	uTimeLoc := gl.Call("getUniformLocation", program, "u_time")
	uResolutionLoc := gl.Call("getUniformLocation", program, "u_resolution")

	// Create a buffer for the full-screen quad (two triangles)
	positionBuffer := gl.Call("createBuffer")
	gl.Call("bindBuffer", gl.Get("ARRAY_BUFFER"), positionBuffer)

	// Quad vertices
	vertices := []interface{}{
		-1.0, -1.0,
		 1.0, -1.0,
		-1.0,  1.0,
		-1.0,  1.0,
		 1.0, -1.0,
		 1.0,  1.0,
	}

	// Convert Go slice to Float32Array for JS WebGL
	float32Array := js.Global().Get("Float32Array").New(len(vertices))
	for i, v := range vertices {
		float32Array.SetIndex(i, v)
	}
	gl.Call("bufferData", gl.Get("ARRAY_BUFFER"), float32Array, gl.Get("STATIC_DRAW"))

	// Bind the position attribute
	positionLocation := gl.Call("getAttribLocation", program, "position")
	gl.Call("enableVertexAttribArray", positionLocation)
	gl.Call("vertexAttribPointer", positionLocation, 2, gl.Get("FLOAT"), false, 0, 0)

	// Render loop
	var render js.Func
	startTime := window.Get("performance").Call("now").Float()

	render = js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		// Stop if canvas is removed from DOM
		if !canvas.Get("isConnected").Bool() {
			render.Release()
			return nil
		}

		// Ensure canvas rendering size matches display size
		rect := canvas.Call("getBoundingClientRect")
		width := rect.Get("width").Float()
		height := rect.Get("height").Float()
		
		// Set internal resolution if it differs
		if canvas.Get("width").Float() != width || canvas.Get("height").Float() != height {
			canvas.Set("width", width)
			canvas.Set("height", height)
			gl.Call("viewport", 0, 0, width, height)
		}

		// Calculate elapsed time in seconds
		currentTime := window.Get("performance").Call("now").Float()
		elapsed := (currentTime - startTime) / 1000.0

		// Update uniforms
		gl.Call("uniform1f", uTimeLoc, elapsed)
		gl.Call("uniform2f", uResolutionLoc, width, height)

		// Draw the quad
		gl.Call("drawArrays", gl.Get("TRIANGLES"), 0, 6)

		// Request next frame
		window.Call("requestAnimationFrame", render)
		return nil
	})

	// Start loop
	window.Call("requestAnimationFrame", render)
}

func createProgram(gl js.Value, vertexSrc, fragmentSrc string) js.Value {
	vertexShader := compileShader(gl, gl.Get("VERTEX_SHADER"), vertexSrc)
	if vertexShader.IsNull() {
		return js.Null()
	}

	fragmentShader := compileShader(gl, gl.Get("FRAGMENT_SHADER"), fragmentSrc)
	if fragmentShader.IsNull() {
		return js.Null()
	}

	program := gl.Call("createProgram")
	gl.Call("attachShader", program, vertexShader)
	gl.Call("attachShader", program, fragmentShader)
	gl.Call("linkProgram", program)

	success := gl.Call("getProgramParameter", program, gl.Get("LINK_STATUS")).Bool()
	if !success {
		fmt.Println("WebGL Program Link Error:", gl.Call("getProgramInfoLog", program).String())
		gl.Call("deleteProgram", program)
		return js.Null()
	}

	return program
}

func compileShader(gl js.Value, shaderType js.Value, source string) js.Value {
	shader := gl.Call("createShader", shaderType)
	gl.Call("shaderSource", shader, source)
	gl.Call("compileShader", shader)

	success := gl.Call("getShaderParameter", shader, gl.Get("COMPILE_STATUS")).Bool()
	if !success {
		fmt.Println("WebGL Shader Compile Error:", gl.Call("getShaderInfoLog", shader).String())
		gl.Call("deleteShader", shader)
		return js.Null()
	}

	return shader
}

//go:build js && wasm

// Package main provides the Hardware Abstraction Layer (HAL) for WebGPU & WebGL2.
package main

import (
	"syscall/js"
)

// HardwareBackend represents the active graphics backend in the browser/webview.
type HardwareBackend uint8

const (
	BackendWebGL1 HardwareBackend = 1
	BackendWebGL2 HardwareBackend = 2
	BackendWebGPU HardwareBackend = 3
)

// HALContext holds active hardware rendering context information.
type HALContext struct {
	Backend      HardwareBackend
	Device       js.Value
	Adapter      js.Value
	Queue        js.Value
	Canvas       js.Value
	Context      js.Value
	IsSupported  bool
	AdapterInfo  string
}

var ActiveHAL HALContext

// InitHardwareAcceleration initializes WebGPU with automatic fallback to WebGL2 and WebGL1.
func InitHardwareAcceleration(canvas js.Value) HALContext {
	window := js.Global().Get("window")
	navigator := window.Get("navigator")

	hal := HALContext{
		Canvas:      canvas,
		IsSupported: false,
	}

	// 1. Attempt WebGPU initialization
	gpu := navigator.Get("gpu")
	if !gpu.IsUndefined() && !gpu.IsNull() {
		hal.Backend = BackendWebGPU
		hal.Context = canvas.Call("getContext", "webgpu")
		if !hal.Context.IsNull() && !hal.Context.IsUndefined() {
			hal.IsSupported = true
			hal.AdapterInfo = "WebGPU Accelerated Device"
			ActiveHAL = hal
			return hal
		}
	}

	// 2. Fallback to WebGL 2.0
	gl2 := canvas.Call("getContext", "webgl2")
	if !gl2.IsNull() && !gl2.IsUndefined() {
		hal.Backend = BackendWebGL2
		hal.Context = gl2
		hal.IsSupported = true
		hal.AdapterInfo = "WebGL 2.0 Hardware Context"
		ActiveHAL = hal
		return hal
	}

	// 3. Fallback to WebGL 1.0
	gl1 := canvas.Call("getContext", "webgl")
	if gl1.IsNull() || gl1.IsUndefined() {
		gl1 = canvas.Call("getContext", "experimental-webgl")
	}
	if !gl1.IsNull() && !gl1.IsUndefined() {
		hal.Backend = BackendWebGL1
		hal.Context = gl1
		hal.IsSupported = true
		hal.AdapterInfo = "WebGL 1.0 Fallback Context"
		ActiveHAL = hal
		return hal
	}

	hal.AdapterInfo = "Software Canvas Fallback"
	ActiveHAL = hal
	return hal
}

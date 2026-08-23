//go:build js && wasm

// Package main provides the Zero-Copy Platform Channel Bridge (v1.6)
// Exposing Native OS hardware features (Haptics, Location, Clipboard, System Theme).
package main

import (
	"syscall/js"
)

// PlatformBridge handles native hardware dispatch from WASM to browser/native OS shell.
type PlatformBridge struct{}

var GlobalPlatformBridge PlatformBridge

// Vibrate triggers native haptic vibration if supported by device hardware.
func (p *PlatformBridge) Vibrate(patternMS int) bool {
	navigator := js.Global().Get("navigator")
	if vibrate := navigator.Get("vibrate"); !vibrate.IsUndefined() && !vibrate.IsNull() {
		navigator.Call("vibrate", patternMS)
		return true
	}
	return false
}

// CopyClipboard copies text to the native operating system clipboard.
func (p *PlatformBridge) CopyClipboard(text string) {
	navigator := js.Global().Get("navigator")
	if clipboard := navigator.Get("clipboard"); !clipboard.IsUndefined() && !clipboard.IsNull() {
		clipboard.Call("writeText", text)
	}
}

// GetSystemTheme queries whether the operating system is in dark mode.
func (p *PlatformBridge) GetSystemTheme() string {
	window := js.Global().Get("window")
	matchMedia := window.Get("matchMedia")
	if !matchMedia.IsUndefined() && !matchMedia.IsNull() {
		res := window.Call("matchMedia", "(prefers-color-scheme: dark)")
		if res.Get("matches").Bool() {
			return "dark"
		}
	}
	return "light"
}

package main

import (
	"math"
	"math/rand"
	"syscall/js"
)

func initNativeCanvas(container js.Value, backgroundType string) {
	document := js.Global().Get("document")
	canvas := document.Call("createElement", "canvas")
	canvas.Get("style").Set("position", "absolute")
	canvas.Get("style").Set("top", "0")
	canvas.Get("style").Set("left", "0")
	canvas.Get("style").Set("width", "100%")
	canvas.Get("style").Set("height", "100%")
	canvas.Get("style").Set("z-index", "0")
	canvas.Get("style").Set("pointer-events", "none")
	
	container.Call("insertBefore", canvas, container.Get("firstChild"))
	
	ctx := canvas.Call("getContext", "2d")
	window := js.Global().Get("window")
	
	resize := func() {
		rect := container.Call("getBoundingClientRect")
		width := rect.Get("width").Float()
		height := rect.Get("height").Float()
		if width == 0 { width = window.Get("innerWidth").Float() }
		if height == 0 { height = 400 } // fallback
		canvas.Set("width", width)
		canvas.Set("height", height)
	}
	resize()
	var resizeListener js.Func
	resizeListener = js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		if !canvas.Get("isConnected").Bool() {
			window.Call("removeEventListener", "resize", resizeListener)
			resizeListener.Release()
			return nil
		}
		resize()
		return nil
	})
	window.Call("addEventListener", "resize", resizeListener)
	
	if backgroundType == "cyber-grid" {
		startCyberGridLoop(ctx, canvas, window)
	} else if backgroundType == "particle-net" {
		startParticleLoop(ctx, canvas, window)
	}
}

func startCyberGridLoop(ctx js.Value, canvas js.Value, window js.Value) {
	var render js.Func
	offset := 0.0
	
	render = js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		if !canvas.Get("isConnected").Bool() {
			render.Release()
			return nil
		}
		
		w := canvas.Get("width").Float()
		h := canvas.Get("height").Float()
		
		ctx.Set("fillStyle", "#0a0b10")
		ctx.Call("fillRect", 0, 0, w, h)
		
		ctx.Set("strokeStyle", "rgba(0, 242, 254, 0.15)")
		ctx.Set("lineWidth", 1)
		
		offset += 0.5
		if offset > 40 {
			offset = 0
		}
		
		ctx.Call("beginPath")
		for x := 0.0; x < w; x += 40 {
			ctx.Call("moveTo", x, 0)
			ctx.Call("lineTo", x, h)
		}
		for y := offset; y < h; y += 40 {
			ctx.Call("moveTo", 0, y)
			ctx.Call("lineTo", w, y)
		}
		ctx.Call("stroke")
		
		window.Call("requestAnimationFrame", render)
		return nil
	})
	
	window.Call("requestAnimationFrame", render)
}

func startParticleLoop(ctx js.Value, canvas js.Value, window js.Value) {
	type Particle struct {
		X, Y, Vx, Vy float64
	}
	var particles []Particle
	for i := 0; i < 60; i++ {
		particles = append(particles, Particle{
			X: rand.Float64() * 2000,
			Y: rand.Float64() * 1000,
			Vx: (rand.Float64() - 0.5) * 1.5,
			Vy: (rand.Float64() - 0.5) * 1.5,
		})
	}
	
	var render js.Func
	render = js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		if !canvas.Get("isConnected").Bool() {
			render.Release()
			return nil
		}
		
		w := canvas.Get("width").Float()
		h := canvas.Get("height").Float()
		
		ctx.Set("fillStyle", "#0a0b10")
		ctx.Call("fillRect", 0, 0, w, h)
		
		ctx.Set("fillStyle", "rgba(155, 81, 224, 0.8)")
		for i := range particles {
			p := &particles[i]
			p.X += p.Vx
			p.Y += p.Vy
			
			if p.X < 0 || p.X > w { p.Vx *= -1 }
			if p.Y < 0 || p.Y > h { p.Vy *= -1 }
			
			ctx.Call("beginPath")
			ctx.Call("arc", p.X, p.Y, 2, 0, math.Pi*2)
			ctx.Call("fill")
		}
		
		window.Call("requestAnimationFrame", render)
		return nil
	})
	
	window.Call("requestAnimationFrame", render)
}

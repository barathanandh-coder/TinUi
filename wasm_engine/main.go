//go:build js && wasm

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"syscall/js"
	"time"
	"unsafe"
)

type Instruction struct {
	Op          string        `json:"op"`
	ID          int           `json:"id,omitempty"`
	Tag         string        `json:"tag,omitempty"`
	Parent      int           `json:"parent,omitempty"`
	Child       int           `json:"child,omitempty"`
	Key         string        `json:"key,omitempty"`
	Value       string        `json:"value,omitempty"`
	Type        string        `json:"type,omitempty"`
	Initial     string        `json:"initial,omitempty"`
	Template    string        `json:"template,omitempty"`
	StateKeys   []string      `json:"state_keys,omitempty"`
	Event       string        `json:"event,omitempty"`
	Mutation    string        `json:"mutation,omitempty"`
	IsHidden    bool          `json:"is_hidden,omitempty"`
	StateKey    string        `json:"state_key,omitempty"`
	Operator    string        `json:"operator,omitempty"`
	CompareVal  string        `json:"compare_val,omitempty"`
	TrueBranch  []Instruction `json:"true_branch,omitempty"`
	FalseBranch []Instruction `json:"false_branch,omitempty"`

	IterableKey  string        `json:"iterable_key,omitempty"`
	IteratorName string        `json:"iterator_name,omitempty"`
	LoopTemplate []Instruction `json:"loop_template,omitempty"`
}

type LoadingBinding struct {
	StateKey    string
	LoaderType  string
	LoaderSpeed string
}

type ParallaxNode struct {
	ID    int
	Speed float64
}

var domRefs = make(map[int]js.Value)
var DynamicMutations map[string][]Instruction
var LoadingBindings = make(map[int]*LoadingBinding)
var ParallaxNodes []ParallaxNode

var earlyObserver js.Value
var centerObserver js.Value
var lateObserver js.Value

var lastActivityTime time.Time
var activityMutex sync.Mutex

func updateActivity() {
	activityMutex.Lock()
	lastActivityTime = time.Now()
	activityMutex.Unlock()
}

const engineCSS = `
/* Micro-interactions */
[data-hover-effect="lift"]:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
[data-hover-effect="glow"]:hover { box-shadow: 0 0 15px rgba(255,255,255,0.3); }
[data-hover-effect="scale"]:hover { transform: scale(1.05); }
[data-hover-effect="shift-right"]:hover { transform: translateX(4px); }
[data-hover-effect="dim"]:hover { opacity: 0.7; }

[data-click-effect="press"]:active { transform: scale(0.95); }
[data-click-effect="ripple"]:active { opacity: 0.5; }
[data-click-effect="snap"]:active { transform: scale(0.9); transition: 0.05s !important; }
[data-click-effect="recoil"]:active { transform: translateX(-4px); }

/* Loaders */
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
.tin-loading-skeleton {
	color: transparent !important;
	background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%);
	background-size: 200% 100%;
	animation: shimmer 1.5s infinite linear;
	pointer-events: none;
}
.tin-loading-skeleton * { visibility: hidden !important; }

.tin-loading-shimmer {
	position: relative;
	overflow: hidden;
}
.tin-loading-shimmer::after {
	content: "";
	position: absolute;
	top: 0; left: 0; width: 100%; height: 100%;
	background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
	animation: shimmer 1.2s infinite;
}

.tin-loading-blur-overlay {
	filter: blur(4px);
	pointer-events: none;
	opacity: 0.6;
}

@keyframes spin { to { transform: rotate(360deg); } }
.tin-loading-spinner {
	position: relative;
	color: transparent !important;
	pointer-events: none;
}
.tin-loading-spinner * { visibility: hidden !important; }
.tin-loading-spinner::after {
	content: "";
	position: absolute;
	top: calc(50% - 10px); left: calc(50% - 10px);
	width: 20px; height: 20px;
	border: 2px solid rgba(255,255,255,0.3);
	border-top-color: #fff;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

/* Scroll Reveals */
[data-scroll-reveal] {
	opacity: 0;
	transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
[data-scroll-reveal="fade-up"] { transform: translateY(40px); }
[data-scroll-reveal="zoom-in"] { transform: scale(0.9); }
[data-scroll-reveal="slide-left"] { transform: translateX(-40px); }
[data-scroll-reveal="slide-right"] { transform: translateX(40px); }
[data-scroll-reveal="assemble"] { transform: translateY(20px) scale(0.95) rotateX(10deg); transform-origin: center bottom; perspective: 1000px; }

[data-scroll-reveal].tin-revealed {
	opacity: 1;
	transform: translate(0) scale(1) rotateX(0);
}

/* Parallax */
[data-parallax-speed] {
    will-change: transform;
}

/* Text Cycle Effects */
.tin-cycle-typewriter { animation: typewriter 0.5s steps(20, end); white-space: nowrap; overflow: hidden; display: inline-block; }
@keyframes typewriter { from { width: 0; } to { width: 100%; } }

.tin-cycle-flip-up { animation: flipUp 0.5s ease-out; display: inline-block; }
@keyframes flipUp { from { transform: rotateX(-90deg); opacity: 0; } to { transform: rotateX(0); opacity: 1; } }

.tin-cycle-glitch-swap { animation: glitch 0.3s linear; display: inline-block; }
@keyframes glitch { 
  0% { transform: translate(0); } 
  20% { transform: translate(-2px, 2px); } 
  40% { transform: translate(-2px, -2px); } 
  60% { transform: translate(2px, 2px); } 
  80% { transform: translate(2px, -2px); } 
  100% { transform: translate(0); } 
}

/* Choreography */
@keyframes cascade-down { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes stagger-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes explode-out { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }

/* Attention Effects */
.tin-attention-heartbeat { animation: heartbeat 1s ease-in-out; }
@keyframes heartbeat {
  0% { transform: scale(1); }
  14% { transform: scale(1.1); }
  28% { transform: scale(1); }
  42% { transform: scale(1.1); }
  70% { transform: scale(1); }
}

.tin-attention-bounce { animation: bounce 1s cubic-bezier(0.28, 0.84, 0.42, 1); }
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.tin-attention-pulse { animation: attentionPulse 1.2s cubic-bezier(0.4, 0, 0.6, 1); }
@keyframes attentionPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.05); }
}

.tin-attention-shimmer-border { position: relative; }
.tin-attention-shimmer-border::after {
  content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
  background-size: 200% 100%;
  animation: shimmerBorder 1s linear forwards;
  z-index: -1; border-radius: inherit; pointer-events: none;
}
@keyframes shimmerBorder { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }

.tin-attention-glitch { animation: glitchAttn 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) both; }
@keyframes glitchAttn {
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
}

/* Transitions */
.tin-transition-out { pointer-events: none; }
.tin-transition-in { z-index: 10; }

.tin-anim-fade-in { animation: fadeIn forwards; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.tin-anim-fade-out { animation: fadeOut forwards; }
@keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }

.tin-anim-slide-from-right { animation: slideFromRight forwards; }
@keyframes slideFromRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
.tin-anim-slide-to-left { animation: slideToLeft forwards; }
@keyframes slideToLeft { from { transform: translateX(0); opacity: 1; } to { transform: translateX(-100%); opacity: 0; } }

.tin-anim-scale-up { animation: scaleUp forwards; }
@keyframes scaleUp { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.tin-anim-scale-down { animation: scaleDown forwards; }
@keyframes scaleDown { from { transform: scale(1); opacity: 1; } to { transform: scale(0.9); opacity: 0; } }
`

func main() {
	InitInputBuffer()
	js.Global().Set("BootTinUI", js.FuncOf(bootEngine))

	// Error Boundary
	js.Global().Set("onerror", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		document := js.Global().Get("document")
		errorDiv := document.Call("createElement", "div")
		errorDiv.Set("id", "tinui-error-boundary")
		errorDiv.Call("setAttribute", "style", "position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(255, 0, 0, 0.9); color: white; z-index: 999999; padding: 40px; font-family: monospace; overflow-y: auto; box-sizing: border-box;")

		msg := ""
		if len(args) > 0 {
			msg += args[0].String() + "\n"
		}
		if len(args) > 1 {
			msg += "Source: " + args[1].String() + "\n"
		}
		if len(args) > 2 {
			msg += "Line: " + args[2].String() + "\n"
		}
		if len(args) > 4 && !args[4].IsUndefined() && !args[4].IsNull() {
			if stack := args[4].Get("stack"); !stack.IsUndefined() {
				msg += "\n" + stack.String()
			}
		}

		errorHTML := "<h1>Runtime Error</h1><pre style='white-space: pre-wrap; font-size: 14px;'>" + msg + "</pre>"
		errorDiv.Set("innerHTML", errorHTML)

		document.Get("body").Call("appendChild", errorDiv)
		return nil
	}))

	// Phase 4: Expose the direct state mutator for text inputs
	js.Global().Set("TinUIMutateState", js.FuncOf(mutateState))

	// Expose the network dispatcher hook
	js.Global().Set("TinUIDispatchApi", js.FuncOf(dispatchApi))

	js.Global().Set("TinUISnapshot", js.FuncOf(takeSnapshot))
	js.Global().Set("TinUIRestore", js.FuncOf(restoreSnapshot))

	// Dynamic Shader Hot-Reload & Diagnostics API
	js.Global().Set("reloadShader", js.FuncOf(jsReloadShader))
	js.Global().Set("TinUIReloadShader", js.FuncOf(jsReloadShader))
	js.Global().Set("TinUICompileShader", js.FuncOf(jsCompileShaderTest))

	<-make(chan struct{})
}

var stateHistory []map[string]*StateEntry

func takeSnapshot(this js.Value, args []js.Value) interface{} {
	snapshot := make(map[string]*StateEntry)

	for key, value := range StateRegistry {
		// Deep copy the StateEntry
		newEntry := &StateEntry{
			Type:   value.Type,
			IntVal: value.IntVal,
			StrVal: value.StrVal,
		}

		if value.ArrayVal != nil {
			newArray := make([]string, len(value.ArrayVal))
			copy(newArray, value.ArrayVal)
			newEntry.ArrayVal = newArray
		}

		snapshot[key] = newEntry
	}

	stateHistory = append(stateHistory, snapshot)

	js.Global().Get("console").Call("log", "[TinUI] Snapshot saved. Total in memory:", len(stateHistory))

	return nil
}

func restoreSnapshot(this js.Value, args []js.Value) interface{} {
	if len(stateHistory) == 0 {
		js.Global().Get("console").Call("warn", "[TinUI] No snapshots available to restore.")
		return nil
	}

	// Pop the last snapshot
	lastIndex := len(stateHistory) - 1
	snapshot := stateHistory[lastIndex]
	stateHistory = stateHistory[:lastIndex]

	// Overwrite current state
	StateRegistry = snapshot

	// Force a complete re-render by marking all keys dirty
	for key := range StateRegistry {
		markDirty(key)
	}
	flushPatches()

	js.Global().Get("console").Call("log", "[TinUI] State restored. Remaining snapshots:", len(stateHistory))

	return nil
}

func bootEngine(this js.Value, args []js.Value) interface{} {
	irJSON := args[0].String()

	type IRBlueprint struct {
		Mutations map[string][]Instruction `json:"mutations"`
		Nodes     []Instruction            `json:"nodes"`
	}
	var blueprint IRBlueprint
	json.Unmarshal([]byte(irJSON), &blueprint)

	DynamicMutations = blueprint.Mutations

	document := js.Global().Get("document")

	// Inject Engine CSS
	styleEl := document.Call("createElement", "style")
	styleEl.Set("innerHTML", engineCSS)
	document.Get("head").Call("appendChild", styleEl)

	// Setup Intersection Observers
	observerCb := js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		entries := args[0]
		for i := 0; i < entries.Length(); i++ {
			entry := entries.Index(i)
			if entry.Get("isIntersecting").Bool() {
				target := entry.Get("target")
				target.Get("classList").Call("add", "tin-revealed")
			}
		}
		return nil
	})

	createObserver := func(threshold float64) js.Value {
		opts := js.Global().Get("Object").New()
		opts.Set("threshold", threshold)
		return js.Global().Get("IntersectionObserver").New(observerCb, opts)
	}

	earlyObserver = createObserver(0.1)
	centerObserver = createObserver(0.5)
	lateObserver = createObserver(0.9)

	// Setup Parallax Scroll Loop
	window := js.Global().Get("window")

	lastActivityTime = time.Now()
	activityCb := js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		updateActivity()
		return nil
	})
	window.Call("addEventListener", "mousemove", activityCb)
	window.Call("addEventListener", "scroll", activityCb)
	window.Call("addEventListener", "keydown", activityCb)

	window.Call("addEventListener", "scroll", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		scrollY := window.Get("scrollY").Float()
		for _, pNode := range ParallaxNodes {
			offset := scrollY * pNode.Speed
			// Translate visually
			domRefs[pNode.ID].Get("style").Set("transform", fmt.Sprintf("translateY(%fpx)", offset))
		}
		return nil
	}))

	rootEl := document.Call("getElementById", "tinui-root")
	if !rootEl.IsNull() && !rootEl.IsUndefined() {
		rootEl.Set("innerHTML", "")
		domRefs[0] = rootEl
	} else {
		domRefs[0] = document.Get("body")
	}

	for _, inst := range blueprint.Nodes {
		executeInstruction(inst, document, nil)
	}

	// Trigger initial load states
	for nodeID, binding := range LoadingBindings {
		applyLoadingState(nodeID, binding)
	}

	// Trigger Text Cycling
	document.Call("querySelectorAll", "[data-text-cycle]").Call("forEach", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		el := args[0]
		cycleData := el.Call("getAttribute", "data-text-cycle").String()
		var words []string
		if err := json.Unmarshal([]byte(cycleData), &words); err == nil && len(words) > 0 {
			effect := el.Call("getAttribute", "data-cycle-effect").String()

			go func() {
				idx := 0
				ticker := time.NewTicker(2 * time.Second)
				for range ticker.C {
					idx = (idx + 1) % len(words)
					el.Set("innerText", words[idx])
					el.Get("classList").Call("remove", "tin-cycle-"+effect)
					el.Get("offsetHeight") // trigger reflow
					el.Get("classList").Call("add", "tin-cycle-"+effect)
				}
			}()
		}
		return nil
	}))

	// Trigger Choreography
	document.Call("querySelectorAll", "[data-entrance-choreography]").Call("forEach", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		container := args[0]
		choreo := container.Call("getAttribute", "data-entrance-choreography").String()
		children := container.Get("children")
		for i := 0; i < children.Length(); i++ {
			child := children.Index(i)
			delay := float64(i) * 0.15
			child.Get("style").Set("animation", fmt.Sprintf("%s 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards", choreo))
			child.Get("style").Set("animationDelay", fmt.Sprintf("%fs", delay))
			child.Get("style").Set("opacity", "0")
		}
		return nil
	}))

	// Initialize Hero Canvas Backgrounds
	document.Call("querySelectorAll", "[data-hero-background]").Call("forEach", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		container := args[0]
		bgType := container.Call("getAttribute", "data-hero-background").String()
		initNativeCanvas(container, bgType)
		return nil
	}))

	// Setup Attention Animations
	document.Call("querySelectorAll", "[data-attention-effect]").Call("forEach", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		el := args[0]
		effect := el.Call("getAttribute", "data-attention-effect").String()

		intervalStr := "frequent"
		if val := el.Call("getAttribute", "data-attention-interval"); !val.IsNull() && !val.IsUndefined() {
			intervalStr = val.String()
		}

		triggerStr := "on-load"
		if val := el.Call("getAttribute", "data-attention-trigger"); !val.IsNull() && !val.IsUndefined() {
			triggerStr = val.String()
		}

		var duration time.Duration
		switch intervalStr {
		case "frequent":
			duration = 3 * time.Second
		case "moderate":
			duration = 7 * time.Second
		case "rare":
			duration = 15 * time.Second
		default:
			duration = 3 * time.Second
		}

		go func() {
			ticker := time.NewTicker(duration)
			for range ticker.C {
				fire := true
				if triggerStr == "on-idle" {
					activityMutex.Lock()
					idleTime := time.Since(lastActivityTime)
					activityMutex.Unlock()
					if idleTime < 5*time.Second {
						fire = false
					}
				}

				if fire {
					el.Get("classList").Call("remove", "tin-attention-"+effect)
					el.Get("offsetHeight") // trigger reflow
					el.Get("classList").Call("add", "tin-attention-"+effect)

					// Auto remove after animation completes
					go func() {
						time.Sleep(1200 * time.Millisecond)
						el.Get("classList").Call("remove", "tin-attention-"+effect)
					}()
				}
			}
		}()
		return nil
	}))

	// Setup Routing
	var activeRoutePath string
	activeRoutePath = window.Get("location").Get("pathname").String()
	if activeRoutePath == "" || activeRoutePath == "/index.html" {
		activeRoutePath = "/"
	}

	hasMatchingRoute := false
	document.Call("querySelectorAll", "[data-route-path]").Call("forEach", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		route := args[0]
		path := route.Call("getAttribute", "data-route-path").String()
		if path == activeRoutePath {
			hasMatchingRoute = true
			route.Get("style").Set("display", "block")
		} else {
			route.Get("style").Set("display", "none")
		}
		return nil
	}))

	// If current URL didn't match any route, fallback to default route or first route
	if !hasMatchingRoute {
		firstRoute := document.Call("querySelector", "[data-default-route='true']")
		if firstRoute.IsNull() || firstRoute.IsUndefined() {
			firstRoute = document.Call("querySelector", "[data-route-path]")
		}
		if !firstRoute.IsNull() && !firstRoute.IsUndefined() {
			firstRoute.Get("style").Set("display", "block")
			activeRoutePath = firstRoute.Call("getAttribute", "data-route-path").String()
		}
	}

	navigate := func(newPath string) {
		if newPath == activeRoutePath {
			return
		}

		router := document.Call("querySelector", "[data-transition-duration]")
		if router.IsNull() {
			activeRoutePath = newPath
			return
		}

		durStr := router.Call("getAttribute", "data-transition-duration").String()
		var durMs time.Duration
		switch durStr {
		case "snappy":
			durMs = 200 * time.Millisecond
		case "smooth":
			durMs = 400 * time.Millisecond
		case "cinematic":
			durMs = 800 * time.Millisecond
		default:
			durMs = 400 * time.Millisecond
		}

		durCss := fmt.Sprintf("%dms", durMs.Milliseconds())

		var outRoute, inRoute js.Value
		document.Call("querySelectorAll", "[data-route-path]").Call("forEach", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
			r := args[0]
			p := r.Call("getAttribute", "data-route-path").String()
			if p == activeRoutePath {
				outRoute = r
			} else if p == newPath {
				inRoute = r
			}
			return nil
		}))

		tOut := router.Call("getAttribute", "data-transition-out").String()
		tIn := router.Call("getAttribute", "data-transition-in").String()

		activeRoutePath = newPath

		if !outRoute.IsUndefined() && !outRoute.IsNull() {
			destroyStrat := outRoute.Call("getAttribute", "data-destroy-strategy")
			strat := ""
			if !destroyStrat.IsNull() {
				strat = destroyStrat.String()
			}

			if strat == "immediate" {
				cleanupDOMNode(outRoute)
				outRoute.Call("remove")
			} else {
				outRoute.Get("style").Set("animationDuration", durCss)
				outRoute.Get("classList").Call("add", "tin-transition-out")
				outRoute.Get("classList").Call("add", "tin-anim-"+tOut)

				go func(route js.Value, classOut string, st string) {
					time.Sleep(durMs)
					if st == "after-animation" {
						cleanupDOMNode(route)
						route.Call("remove")
					} else {
						route.Get("style").Set("display", "none")
						route.Get("classList").Call("remove", "tin-transition-out")
						route.Get("classList").Call("remove", "tin-anim-"+classOut)
					}
				}(outRoute, tOut, strat)
			}
		}

		if !inRoute.IsUndefined() && !inRoute.IsNull() {
			inRoute.Get("style").Set("display", "block")
			inRoute.Get("style").Set("animationDuration", durCss)
			inRoute.Get("classList").Call("add", "tin-transition-in")
			inRoute.Get("classList").Call("add", "tin-anim-"+tIn)

			go func(route js.Value, classIn string) {
				time.Sleep(durMs)
				route.Get("classList").Call("remove", "tin-transition-in")
				route.Get("classList").Call("remove", "tin-anim-"+classIn)
			}(inRoute, tIn)
		}
	}

	document.Call("addEventListener", "click", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		e := args[0]

		// 1. Check for data-action (Internal Event Dispatcher)
		actionTarget := e.Get("target")
		for !actionTarget.IsNull() && !actionTarget.IsUndefined() {
			actionAttr := actionTarget.Call("getAttribute", "data-action")
			if !actionAttr.IsNull() && !actionAttr.IsUndefined() {
				actionName := actionAttr.String()
				// Invoke natively within Go memory
				handleEvent(js.Null(), []js.Value{js.ValueOf(actionName)})
				break
			}
			actionTarget = actionTarget.Get("parentElement")
		}

		// 2. Check for Navigation (Router)
		navTarget := e.Get("target")
		for !navTarget.IsNull() && !navTarget.IsUndefined() && navTarget.Get("tagName").String() != "A" {
			navTarget = navTarget.Get("parentElement")
		}

		if !navTarget.IsNull() && !navTarget.IsUndefined() {
			href := navTarget.Call("getAttribute", "href")
			if !href.IsNull() && !href.IsUndefined() {
				path := href.String()
				if path != "" && path[0] == '/' {
					e.Call("preventDefault")
					window.Get("history").Call("pushState", nil, "", path)
					navigate(path)
				}
			}
		}
		return nil
	}))

	window.Call("addEventListener", "popstate", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		navigate(window.Get("location").Get("pathname").String())
		return nil
	}))

	return "Milestone 2 Engine Booted"
}

func executeInstruction(inst Instruction, document js.Value, scope map[string]interface{}) {
	switch inst.Op {
	case "CREATE_NODE":
		var el js.Value
		el = document.Call("createElement", inst.Tag)
		el.Call("setAttribute", "id", fmt.Sprintf("tin-node-%d", inst.ID))
		if inst.IsHidden {
			el.Get("style").Set("display", "none")
		}
		domRefs[inst.ID] = el

	case "DECLARE_STATE":
		RegisterState(inst.Key, inst.Type, inst.Initial)

	case "BIND_TEXT":
		// 1. Save the relationship so we can update it later
		Bindings[inst.ID] = TextBinding{
			Template:  inst.Template,
			StateKeys: inst.StateKeys,
			Scope:     scope,
		}

		// 2. Perform the initial render
		initialText := FormatTemplate(inst.Template, inst.StateKeys, scope)
		domRefs[inst.ID].Set("innerText", initialText)

	case "SET_TEXT":
		if el, ok := domRefs[inst.ID]; ok && !el.IsNull() && !el.IsUndefined() {
			tag := el.Get("tagName").String()
			if tag == "BUTTON" || tag == "P" || tag == "SPAN" || tag == "A" || tag == "H1" || tag == "H2" || tag == "H3" || tag == "H4" || tag == "H5" || tag == "H6" {
				el.Set("textContent", inst.Value)
			} else {
				el.Set("innerText", inst.Value)
			}
		}

	case "SET_ATTRIBUTE":
		if el, ok := domRefs[inst.ID]; ok && !el.IsNull() && !el.IsUndefined() {
			el.Call("setAttribute", inst.Key, inst.Value)
			if inst.Key == "style" {
				el.Get("style").Set("cssText", inst.Value)
			}
			if inst.Key == "data-shader-code" {
				initWebGLShader(el, inst.Value)
			}
			if inst.Key == "data-scroll-reveal" {
				offsetAttr := el.Call("getAttribute", "data-reveal-offset")
				offset := "center"
				if !offsetAttr.IsNull() && !offsetAttr.IsUndefined() {
					offset = offsetAttr.String()
				}
				if offset == "early" {
					earlyObserver.Call("observe", el)
				} else if offset == "late" {
					lateObserver.Call("observe", el)
				} else {
					centerObserver.Call("observe", el)
				}
			}
			if inst.Key == "data-parallax-speed" {
				if speed, err := strconv.ParseFloat(inst.Value, 64); err == nil {
					ParallaxNodes = append(ParallaxNodes, ParallaxNode{ID: inst.ID, Speed: speed})
				}
			}
		}

	case "APPEND_CHILD":
		parentEl := domRefs[inst.Parent]
		childEl := domRefs[inst.Child]
		if !parentEl.IsNull() && !parentEl.IsUndefined() && !childEl.IsNull() && !childEl.IsUndefined() {
			parentEl.Call("appendChild", childEl)
		}

	case "ADD_EVENT":
		el := domRefs[inst.ID]
		el.Call("setAttribute", "data-action", inst.Mutation)

	case "BIND_INPUT":
		el := domRefs[inst.ID]

		// 1. Tag the element so the JS Bridge knows which variable this modifies
		el.Call("setAttribute", "data-bind", inst.StateKey)

		// 2. Hydrate the input with the current memory state on boot
		entry, exists := StateRegistry[inst.StateKey]
		if exists && entry != nil {
			el.Set("value", entry.StrVal)
		} else {
			// Auto-register it so we don't panic on nil dereference later
			StateRegistry[inst.StateKey] = &StateEntry{Type: "string", StrVal: ""}
			el.Set("value", "")
		}

	case "BIND_LOADING":
		LoadingBindings[inst.ID] = &LoadingBinding{
			StateKey:    inst.StateKey,
			LoaderType:  inst.Tag,
			LoaderSpeed: inst.Value,
		}

	case "CREATE_CONDITIONAL":
		// 1. Create a stable Anchor Node in the DOM (e.g., <div id="tin-cond-5">)
		anchor := document.Call("createElement", "div")
		// Using display: contents ensures this anchor doesn't ruin CSS flex/grid layouts
		anchor.Call("setAttribute", "style", "display: contents;")
		domRefs[inst.ID] = anchor

		// Attach anchor to parent
		domRefs[inst.Parent].Call("appendChild", anchor)

		// 2. Evaluate the initial state
		initialBool := evalCondition(inst.StateKey, inst.Operator, inst.CompareVal)

		// 3. Register the binding so flushPatches() can watch it
		ConditionalBindings[inst.ID] = &ConditionalBinding{
			StateKey:    inst.StateKey,
			Operator:    inst.Operator,
			CompareVal:  inst.CompareVal,
			TrueBranch:  inst.TrueBranch,
			FalseBranch: inst.FalseBranch,
			CurrentBool: initialBool,
		}

		// 4. Render the initial branch
		branchToRender := inst.FalseBranch
		if initialBool {
			branchToRender = inst.TrueBranch
		}

		for _, branchInst := range branchToRender {
			// Override parent to mount inside the Anchor Node
			branchInst.Parent = inst.ID
			executeInstruction(branchInst, document, scope)
		}

	case "RENDER_LIST":
		// 1. Create a stable Anchor Node in the DOM
		anchor := document.Call("createElement", "div")
		anchor.Call("setAttribute", "style", "display: contents;")
		domRefs[inst.ID] = anchor

		// Attach anchor to parent
		domRefs[inst.Parent].Call("appendChild", anchor)

		// Register the binding so flushPatches() can watch it
		ListBindings[inst.ID] = &ListBinding{
			IterableKey:  inst.IterableKey,
			IteratorName: inst.IteratorName,
			LoopTemplate: inst.LoopTemplate,
		}

		// Render the initial list
		renderListDOM(inst.ID, document)
	}
}

func renderListDOM(anchorID int, document js.Value) {
	binding := ListBindings[anchorID]
	anchor := domRefs[anchorID]

	// Clear anchor
	anchor.Set("innerHTML", "")

	listState := StateRegistry[binding.IterableKey].ArrayVal

	for _, item := range listState {
		localScope := map[string]interface{}{
			binding.IteratorName: item,
		}

		for _, childInst := range binding.LoopTemplate {
			childInst.Parent = anchorID
			executeInstruction(childInst, document, localScope)
		}
	}
}

// mutateState takes (stateKey, newValue) from JS and updates the Arena
func mutateState(this js.Value, args []js.Value) interface{} {
	if len(args) < 2 {
		return nil
	}

	key := args[0].String()
	newValue := args[1].String()

	// 1. Update the Memory Arena
	StateMutex.Lock()
	if entry, exists := StateRegistry[key]; exists {
		entry.StrVal = newValue
		if entry.Type == "int" {
			if v, err := strconv.Atoi(newValue); err == nil {
				entry.IntVal = v
			}
		}
		// 2. Flag the Dirty Bitmap
		markDirty(key)
	} else {
		// If key doesn't exist, create it dynamically for inputs without state declaration
		StateRegistry[key] = &StateEntry{Type: "string", StrVal: newValue}
		// Assuming we don't need a dirty bit for newly injected keys immediately,
		// but we should set it up if it gets bound later.
	}
	StateMutex.Unlock()

	// 3. Recalculate the UI
	flushPatches()

	return nil
}

// 1. The Network Dispatcher Hook
func dispatchApi(this js.Value, args []js.Value) interface{} {
	action := ""
	if len(args) > 0 {
		action = args[0].String()
	}

	endpoint := ""
	requestData := map[string]string{}

	// 2. Securely extract data from the State Tree based on action
	StateMutex.RLock()
	if action == "subscribeBeta" {
		endpoint = "http://localhost:5000/api/subscribe"
		if emailEntry, ok := StateRegistry["email"]; ok {
			requestData["email"] = emailEntry.StrVal
		}
	} else if action == "reportBug" {
		endpoint = "http://localhost:5000/api/report"
		if typeEntry, ok := StateRegistry["report_type"]; ok {
			requestData["type"] = typeEntry.StrVal
		}
		if descEntry, ok := StateRegistry["report_desc"]; ok {
			requestData["desc"] = descEntry.StrVal
		}
	}
	StateMutex.RUnlock()

	if endpoint == "" {
		fmt.Println("[TinPyUI] Unknown dispatch action:", action)
		return nil
	}

	// 3. Marshal the payload into JSON bytes
	jsonPayload, err := json.Marshal(requestData)
	if err != nil {
		fmt.Println("[TinPyUI] Error creating JSON payload:", err)
		return nil
	}

	// 4. Spin up a Go Goroutine to prevent blocking the UI thread
	go func() {
		req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonPayload))
		if err != nil {
			fmt.Println("[TinPyUI] Request creation failed:", err)
			return
		}
		req.Header.Set("Content-Type", "application/json")

		// 5. Execute the network request natively
		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			fmt.Println("[TinPyUI] Network Request Failed:", err)
			return
		}
		defer resp.Body.Close()

		// 6. Handle the server response
		body, _ := ioutil.ReadAll(resp.Body)
		if resp.StatusCode == 200 {
			fmt.Printf("[TinPyUI] Success! Server responded: %s\n", string(body))

			// Natively show the Toast
			StateMutex.Lock()
			if entry, exists := StateRegistry["show_toast"]; exists {
				entry.StrVal = "1"
				entry.IntVal = 1
				markDirty("show_toast")
			}
			StateMutex.Unlock()
			flushPatches()

			// Automatically hide the Toast after 3 seconds
			go func() {
				time.Sleep(3 * time.Second)
				StateMutex.Lock()
				if entry, exists := StateRegistry["show_toast"]; exists {
					entry.StrVal = "0"
					entry.IntVal = 0
					markDirty("show_toast")
				}
				StateMutex.Unlock()
				flushPatches()
			}()

		} else {
			fmt.Printf("[TinPyUI] API Error: %d - %s\n", resp.StatusCode, string(body))
		}
	}()

	return nil
}

// handleEvent is the router for mutations
func handleEvent(this js.Value, args []js.Value) interface{} {
	action := args[0].String()

	if instructions, exists := DynamicMutations[action]; exists {
		for _, inst := range instructions {
			switch inst.Op {
			case "ASSIGN":
				if entry, ok := StateRegistry[inst.StateKey]; ok {
					entry.StrVal = inst.Value
					markDirty(inst.StateKey)
				}
			case "INCREMENT":
				if entry, ok := StateRegistry[inst.StateKey]; ok {
					if val, err := strconv.Atoi(inst.Value); err == nil {
						entry.IntVal += val
						entry.StrVal = strconv.Itoa(entry.IntVal)
						markDirty(inst.StateKey)
					}
				}
			case "DECREMENT":
				if entry, ok := StateRegistry[inst.StateKey]; ok {
					if val, err := strconv.Atoi(inst.Value); err == nil {
						entry.IntVal -= val
						entry.StrVal = strconv.Itoa(entry.IntVal)
						markDirty(inst.StateKey)
					}
				}
			}
		}
	}

	flushPatches()
	return nil
}

// flushPatches scans the UI tree and surgical updates ONLY what changed
func flushPatches() {
	if dirtyBitmap == 0 {
		return
	}

	// Iterate through our active bindings to see if any depend on dirty state
	for nodeID, binding := range Bindings {
		needsUpdate := false

		for _, key := range binding.StateKeys {
			if isDirty(key) {
				needsUpdate = true
				break
			}
		}

		if needsUpdate {
			newText := FormatTemplate(binding.Template, binding.StateKeys, binding.Scope)
			domRefs[nodeID].Set("innerText", newText)
		}
	}

	// Handle Conditional Bindings
	for anchorID, binding := range ConditionalBindings {
		if isDirty(binding.StateKey) {
			newBool := evalCondition(binding.StateKey, binding.Operator, binding.CompareVal)

			// Only update the DOM if the branch actually flipped
			if newBool != binding.CurrentBool {
				binding.CurrentBool = newBool
				anchor := domRefs[anchorID]

				// 1. Surgical Unmount: Wipe the
				// Destroy old children
				children := anchor.Get("children")
				for i := 0; i < children.Length(); i++ {
					cleanupDOMNode(children.Index(i))
				}
				anchor.Set("innerHTML", "")

				// 2. Execute the new branch
				branchToRender := binding.FalseBranch
				if newBool {
					branchToRender = binding.TrueBranch
				}

				document := js.Global().Get("document")
				for _, branchInst := range branchToRender {
					branchInst.Parent = anchorID
					executeInstruction(branchInst, document, nil)
				}
			}
		}
	}

	// Handle List Bindings
	for anchorID, binding := range ListBindings {
		if isDirty(binding.IterableKey) {
			document := js.Global().Get("document")
			renderListDOM(anchorID, document)
		}
	}

	// Handle Loading Bindings
	for nodeID, binding := range LoadingBindings {
		if isDirty(binding.StateKey) {
			applyLoadingState(nodeID, binding)
		}
	}

	clearAllDirtyBits()
}

func applyLoadingState(nodeID int, binding *LoadingBinding) {
	StateMutex.RLock()
	entry := StateRegistry[binding.StateKey]
	isLoading := false
	if entry != nil && entry.StrVal == "true" {
		isLoading = true
	}
	StateMutex.RUnlock()

	el := domRefs[nodeID]
	classList := el.Get("classList")
	className := "tin-loading-" + binding.LoaderType

	if isLoading {
		classList.Call("add", className)
	} else {
		classList.Call("remove", className)
	}
}

func cleanupDOMNode(node js.Value) {
	if node.IsNull() || node.IsUndefined() {
		return
	}
	idAttr := node.Call("getAttribute", "id")
	if !idAttr.IsNull() && idAttr.String() != "" && len(idAttr.String()) > 9 {
		if idStr := idAttr.String()[9:]; idStr != "" {
			if id, err := strconv.Atoi(idStr); err == nil {
				delete(domRefs, id)
			}
		}
	}
	children := node.Get("children")
	for i := 0; i < children.Length(); i++ {
		cleanupDOMNode(children.Index(i))
	}
}


// ============================================================================
// CONSOLIDATED WASM ENGINE HELPERS (State, Input Buffer, Canvas, WebGL, Layout)
// ============================================================================

const EventCapacity = 256
const SlotsPerEvent = 4

type RingBuffer struct {
	Head     int32
	Tail     int32
	Payloads [EventCapacity * SlotsPerEvent]int32
}

var SharedInputBuffer RingBuffer

func InitInputBuffer() {
	ptr := uintptr(unsafe.Pointer(&SharedInputBuffer))
	js.Global().Set("getTinPyBufferPointer", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		return int(ptr)
	}))
}

type StateEntry struct {
	Type     string
	IntVal   int
	StrVal   string
	ArrayVal []string
}

var (
	StateRegistry = make(map[string]*StateEntry)
	StateMutex    sync.RWMutex
	StateIndexMap = make(map[string]int)
	nextStateBit  = 0
	dirtyBitmap uint64 = 0
	Bindings = make(map[int]TextBinding)
)

type TextBinding struct {
	Template  string
	StateKeys []string
	Scope     map[string]interface{}
}

func RegisterState(key, typeHint, initial string) {
	entry := &StateEntry{Type: typeHint}
	if typeHint == "infer" {
		if val, err := strconv.Atoi(initial); err == nil {
			entry.Type = "int"
			entry.IntVal = val
		} else {
			entry.Type = "string"
			entry.StrVal = initial
		}
	}
	if strings.HasPrefix(initial, "[") && strings.HasSuffix(initial, "]") {
		var arr []string
		if err := json.Unmarshal([]byte(initial), &arr); err == nil {
			entry.Type = "array"
			entry.ArrayVal = arr
		}
	}
	StateRegistry[key] = entry
	StateIndexMap[key] = nextStateBit
	nextStateBit++
}

func markDirty(key string) {
	if bit, exists := StateIndexMap[key]; exists {
		dirtyBitmap |= (1 << bit)
	}
}

func isDirty(key string) bool {
	if bit, exists := StateIndexMap[key]; exists {
		return dirtyBitmap&(1<<bit) != 0
	}
	return false
}

func clearAllDirtyBits() {
	dirtyBitmap = 0
}

func FormatTemplate(template string, keys []string, scope map[string]interface{}) string {
	result := template
	for _, key := range keys {
		var valStr string
		if scope != nil {
			if val, exists := scope[key]; exists {
				valStr = val.(string)
			}
		}
		if valStr == "" {
			entry := StateRegistry[key]
			if entry != nil {
				if entry.Type == "int" {
					valStr = strconv.Itoa(entry.IntVal)
				} else {
					valStr = entry.StrVal
				}
			}
		}
		result = strings.Replace(result, "{}", valStr, 1)
	}
	return result
}

func evalCondition(stateKey, operator, compareValStr string) bool {
	entry := StateRegistry[stateKey]
	if entry == nil { return false }
	if entry.Type == "int" {
		compareVal, _ := strconv.Atoi(compareValStr)
		switch operator {
		case ">": return entry.IntVal > compareVal
		case "<": return entry.IntVal < compareVal
		case "==": return entry.IntVal == compareVal
		}
	} else if entry.Type == "string" {
		switch operator {
		case "==": return entry.StrVal == compareValStr
		case "!=": return entry.StrVal != compareValStr
		}
	}
	return false
}

type ConditionalBinding struct {
	StateKey    string
	Operator    string
	CompareVal  string
	TrueBranch  []Instruction
	FalseBranch []Instruction
	CurrentBool bool
}

var ConditionalBindings = make(map[int]*ConditionalBinding)

type ListBinding struct {
	IterableKey  string
	IteratorName string
	LoopTemplate []Instruction
}

var ListBindings = make(map[int]*ListBinding)



type Rect struct {
	X, Y, W, H float32
}

func (a Rect) Intersects(b Rect) bool {
	return a.X < b.X+b.W && a.X+a.W > b.X && a.Y < b.Y+b.H && a.Y+a.H > b.Y
}


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
	window := js.Global().Get("window")

	resize := func() {
		rect := container.Call("getBoundingClientRect")
		width := rect.Get("width").Float()
		height := rect.Get("height").Float()
		if width == 0 { width = window.Get("innerWidth").Float() }
		if height == 0 { height = 400 }
		canvas.Set("width", width)
		canvas.Set("height", height)
	}
	resize()
}

const defaultVertexShader = `
attribute vec2 position;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
}
`

const defaultSDFBoxFragmentShader = `
precision highp float;
uniform vec2 u_resolution;
uniform vec2 u_box_size;
uniform float u_radius;
uniform float u_border_width;
uniform float u_shadow_softness;
uniform vec2 u_shadow_offset;
uniform vec4 u_bg_color;
uniform vec4 u_border_color;
uniform vec4 u_shadow_color;

float sdRoundRect(vec2 p, vec2 b, float r) {
    vec2 d = abs(p) - b + vec2(r);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - r;
}

void main() {
    vec2 uv = gl_FragCoord.xy - (u_resolution.xy * 0.5);
    vec2 half_size = u_box_size * 0.5;
    float box_dist = sdRoundRect(uv, half_size, u_radius);
    float shadow_dist = sdRoundRect(uv - u_shadow_offset, half_size, u_radius);
    float aa = 1.0;
    float shadow_alpha = exp(-max(shadow_dist, 0.0) / max(u_shadow_softness, 0.001)) * u_shadow_color.a;
    vec4 shadow = vec4(u_shadow_color.rgb, shadow_alpha);
    float border_mask = 1.0 - smoothstep(0.0, aa, abs(box_dist + u_border_width * 0.5) - u_border_width * 0.5);
    float box_mask = 1.0 - smoothstep(0.0, aa, box_dist);
    vec4 final_color = mix(vec4(0.0), shadow, shadow.a);
    final_color = mix(final_color, u_bg_color, box_mask * u_bg_color.a);
    final_color = mix(final_color, u_border_color, border_mask * u_border_color.a);
    gl_FragColor = final_color;
}
`

const defaultUberVertexShader = `
attribute vec2 position;
attribute vec2 a_uv;
attribute float a_type;

uniform vec2 u_resolution;

varying float v_type;
varying vec2 v_uv;
varying vec2 v_pos;

void main() {
    v_type = a_type;
    v_uv = a_uv;
    v_pos = position;
    vec2 zeroToOne = position / u_resolution;
    vec2 clipSpace = (zeroToOne * 2.0) - 1.0;
    gl_Position = vec4(clipSpace.x, -clipSpace.y, 0.0, 1.0);
}
`

const defaultUberFragmentShader = `
#ifdef GL_OES_standard_derivatives
#extension GL_OES_standard_derivatives : enable
#endif

precision highp float;

varying float v_type;
varying vec2 v_uv;
varying vec2 v_pos;

uniform sampler2D u_font_atlas;
uniform vec4 u_color;
uniform vec2 u_resolution;
uniform vec2 u_box_size;
uniform float u_radius;
uniform float u_border_width;
uniform vec4 u_border_color;
uniform float u_shadow_softness;
uniform vec2 u_shadow_offset;
uniform vec4 u_shadow_color;

float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

float sdRoundRect(vec2 p, vec2 b, float r) {
    vec2 d = abs(p) - b + vec2(r);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - r;
}

void main() {
    if (v_type < 0.5) {
        vec2 half_size = u_box_size * 0.5;
        float box_dist = sdRoundRect(v_pos, half_size, u_radius);
        float shadow_dist = sdRoundRect(v_pos - u_shadow_offset, half_size, u_radius);
        float aa = 1.0;
        float shadow_alpha = exp(-max(shadow_dist, 0.0) / max(u_shadow_softness, 0.001)) * u_shadow_color.a;
        vec4 shadow = vec4(u_shadow_color.rgb, shadow_alpha);
        float border_mask = 1.0 - smoothstep(0.0, aa, abs(box_dist + u_border_width * 0.5) - u_border_width * 0.5);
        float box_mask = 1.0 - smoothstep(0.0, aa, box_dist);
        vec4 final_color = mix(vec4(0.0), shadow, shadow.a);
        final_color = mix(final_color, u_color, box_mask * u_color.a);
        final_color = mix(final_color, u_border_color, border_mask * u_border_color.a);
        gl_FragColor = final_color;
    } else {
        vec3 msd = texture2D(u_font_atlas, v_uv).rgb;
        float dist = median(msd.r, msd.g, msd.b) - 0.5;
        #ifdef GL_OES_standard_derivatives
        float fw = fwidth(dist);
        #else
        float fw = 0.05;
        #endif
        float opacity = clamp(dist / max(fw, 0.0001) + 0.5, 0.0, 1.0);
        gl_FragColor = vec4(u_color.rgb, u_color.a * opacity);
    }
}
`

// compileShader interrogates the GPU immediately after compilation
// and fires any syntax errors directly to the crash overlay.
func compileShader(gl js.Value, shaderType js.Value, sourceCode string) (js.Value, error) {
	// 1. Create and compile the shader
	shader := gl.Call("createShader", shaderType)
	gl.Call("shaderSource", shader, sourceCode)
	gl.Call("compileShader", shader)

	// 2. Interrogate the GPU: Did compilation succeed?
	success := gl.Call("getShaderParameter", shader, gl.Get("COMPILE_STATUS")).Bool()

	if !success {
		// 3. Extract the exact GLSL syntax error from the GPU memory
		gpuLog := gl.Call("getShaderInfoLog", shader).String()

		// 4. Clean up the broken shader to prevent memory leaks
		gl.Call("deleteShader", shader)

		// 5. Fire this back to the HTML Error Overlay
		if crashFn := js.Global().Get("crash"); !crashFn.IsUndefined() && !crashFn.IsNull() {
			js.Global().Call("crash", "GLSL Compile Error:\n"+gpuLog)
		} else {
			fmt.Printf("[GPU PANIC] GLSL Syntax Error:\n%s\n", gpuLog)
		}

		return js.Null(), fmt.Errorf("shader compile failed: %s", gpuLog)
	}

	return shader, nil
}

// linkProgram validates program linking and logs diagnostics
func linkProgram(gl js.Value, vertexShader js.Value, fragmentShader js.Value) (js.Value, error) {
	shaderProgram := gl.Call("createProgram")
	gl.Call("attachShader", shaderProgram, vertexShader)
	gl.Call("attachShader", shaderProgram, fragmentShader)
	gl.Call("linkProgram", shaderProgram)

	linkSuccess := gl.Call("getProgramParameter", shaderProgram, gl.Get("LINK_STATUS")).Bool()
	if !linkSuccess {
		gpuLog := gl.Call("getProgramInfoLog", shaderProgram).String()
		gl.Call("deleteProgram", shaderProgram)
		if crashFn := js.Global().Get("crash"); !crashFn.IsUndefined() && !crashFn.IsNull() {
			js.Global().Call("crash", "Shader Linking Failed:\n"+gpuLog)
		} else {
			fmt.Printf("[GPU PANIC] Shader Linking Failed:\n%s\n", gpuLog)
		}
		return js.Null(), fmt.Errorf("shader link failed: %s", gpuLog)
	}

	return shaderProgram, nil
}

type WebGLShaderInstance struct {
	Canvas          js.Value
	GL              js.Value
	Program         js.Value
	VertexShader    js.Value
	FragShader      js.Value
	QuadBuffer      js.Value
	PositionLoc     js.Value
	TimeLoc         js.Value
	ResLoc          js.Value
	MouseLoc        js.Value
	BoxSizeLoc      js.Value
	RadiusLoc       js.Value
	BorderWidthLoc  js.Value
	BorderColorLoc  js.Value
	ShadowSoftLoc   js.Value
	ShadowOffsetLoc js.Value
	ShadowColorLoc  js.Value
	BgColorLoc      js.Value
	ColorLoc        js.Value
	AnimFrameFunc   js.Func
	AnimFrameId     js.Value
	StartTime       float64
	MouseX          float32
	MouseY          float32
	IsRunning       bool
}

var activeShaderInstances = make(map[string]*WebGLShaderInstance)

func clearCrashOverlay() {
	document := js.Global().Get("document")
	if document.IsUndefined() || document.IsNull() {
		return
	}
	overlay := document.Call("getElementById", "error-overlay")
	if !overlay.IsNull() && !overlay.IsUndefined() {
		overlay.Get("style").Set("display", "none")
	}
	canvas := document.Call("getElementById", "tin-canvas")
	if !canvas.IsNull() && !canvas.IsUndefined() {
		canvas.Get("style").Set("display", "block")
	}
	root := document.Call("getElementById", "tinui-root")
	if !root.IsNull() && !root.IsUndefined() {
		root.Get("style").Set("display", "block")
	}
}

func createQuadBuffer(gl js.Value) js.Value {
	buffer := gl.Call("createBuffer")
	gl.Call("bindBuffer", gl.Get("ARRAY_BUFFER"), buffer)
	quad := []float32{
		-1.0, -1.0,
		 1.0, -1.0,
		-1.0,  1.0,
		-1.0,  1.0,
		 1.0, -1.0,
		 1.0,  1.0,
	}
	arr := js.Global().Get("Float32Array").New(len(quad))
	for i, v := range quad {
		arr.SetIndex(i, v)
	}
	gl.Call("bufferData", gl.Get("ARRAY_BUFFER"), arr, gl.Get("STATIC_DRAW"))
	return buffer
}

func ensurePrecision(fragmentCode string) string {
	if !strings.Contains(fragmentCode, "precision") {
		return "precision mediump float;\n" + fragmentCode
	}
	return fragmentCode
}

// reloadWebGLShader dynamically hot-reloads a fragment shader without tearing down canvas context
func reloadWebGLShader(canvas js.Value, fragmentCode string) bool {
	canvasId := ""
	if idVal := canvas.Get("id"); !idVal.IsUndefined() && idVal.String() != "" {
		canvasId = idVal.String()
	}

	inst, exists := activeShaderInstances[canvasId]
	if !exists || inst == nil {
		initWebGLShader(canvas, fragmentCode)
		return true
	}

	gl := inst.GL
	preparedCode := ensurePrecision(fragmentCode)
	newFragShader, err := compileShader(gl, gl.Get("FRAGMENT_SHADER"), preparedCode)
	if err != nil {
		fmt.Printf("[GPU PANIC] Dynamic reload rejected fragment shader: %v\n", err)
		return false
	}

	newProgram, err := linkProgram(gl, inst.VertexShader, newFragShader)
	if err != nil {
		gl.Call("deleteShader", newFragShader)
		fmt.Printf("[GPU PANIC] Dynamic reload rejected program link: %v\n", err)
		return false
	}

	// Hot swap active program atomically
	oldProg := inst.Program
	oldFrag := inst.FragShader

	inst.Program = newProgram
	inst.FragShader = newFragShader

	inst.PositionLoc = gl.Call("getAttribLocation", newProgram, "position")
	inst.TimeLoc = gl.Call("getUniformLocation", newProgram, "u_time")
	inst.ResLoc = gl.Call("getUniformLocation", newProgram, "u_resolution")
	inst.MouseLoc = gl.Call("getUniformLocation", newProgram, "u_mouse")

	if !oldProg.IsNull() && !oldProg.IsUndefined() {
		gl.Call("deleteProgram", oldProg)
	}
	if !oldFrag.IsNull() && !oldFrag.IsUndefined() {
		gl.Call("deleteShader", oldFrag)
	}

	clearCrashOverlay()
	fmt.Printf("[GPU HOT-RELOAD] Fragment shader reloaded cleanly on canvas: %s\n", canvasId)
	return true
}

func initWebGLShader(canvas js.Value, fragmentCode string) {
	if canvas.IsNull() || canvas.IsUndefined() {
		return
	}

	canvasId := ""
	if idVal := canvas.Get("id"); !idVal.IsUndefined() && idVal.String() != "" {
		canvasId = idVal.String()
	} else {
		canvasId = fmt.Sprintf("tin_canvas_%d", time.Now().UnixNano())
		canvas.Set("id", canvasId)
	}

	if _, exists := activeShaderInstances[canvasId]; exists {
		reloadWebGLShader(canvas, fragmentCode)
		return
	}

	gl := canvas.Call("getContext", "webgl2")
	if gl.IsNull() || gl.IsUndefined() {
		gl = canvas.Call("getContext", "webgl")
		if gl.IsNull() || gl.IsUndefined() {
			gl = canvas.Call("getContext", "experimental-webgl")
			if gl.IsNull() || gl.IsUndefined() {
				fmt.Println("WebGL not supported in this browser.")
				return
			}
		}
	}

	// 1. Compile Vertex Shader
	vertShader, err := compileShader(gl, gl.Get("VERTEX_SHADER"), defaultVertexShader)
	if err != nil {
		fmt.Printf("[GPU PANIC] Vertex Shader compilation failed: %v\n", err)
		return
	}

	// 2. Compile Fragment Shader
	preparedFrag := ensurePrecision(fragmentCode)
	fragShader, err := compileShader(gl, gl.Get("FRAGMENT_SHADER"), preparedFrag)
	if err != nil {
		gl.Call("deleteShader", vertShader)
		fmt.Printf("[GPU PANIC] Fragment Shader compilation failed: %v\n", err)
		return
	}

	// 3. Link Program
	program, err := linkProgram(gl, vertShader, fragShader)
	if err != nil {
		gl.Call("deleteShader", vertShader)
		gl.Call("deleteShader", fragShader)
		fmt.Printf("[GPU PANIC] Program linking failed: %v\n", err)
		return
	}

	quadBuffer := createQuadBuffer(gl)
	posLoc := gl.Call("getAttribLocation", program, "position")
	timeLoc := gl.Call("getUniformLocation", program, "u_time")
	resLoc := gl.Call("getUniformLocation", program, "u_resolution")
	mouseLoc := gl.Call("getUniformLocation", program, "u_mouse")

	boxSizeLoc := gl.Call("getUniformLocation", program, "u_box_size")
	radiusLoc := gl.Call("getUniformLocation", program, "u_radius")
	borderWidthLoc := gl.Call("getUniformLocation", program, "u_border_width")
	borderColorLoc := gl.Call("getUniformLocation", program, "u_border_color")
	shadowSoftLoc := gl.Call("getUniformLocation", program, "u_shadow_softness")
	shadowOffsetLoc := gl.Call("getUniformLocation", program, "u_shadow_offset")
	shadowColorLoc := gl.Call("getUniformLocation", program, "u_shadow_color")
	bgColorLoc := gl.Call("getUniformLocation", program, "u_bg_color")
	colorLoc := gl.Call("getUniformLocation", program, "u_color")

	inst := &WebGLShaderInstance{
		Canvas:          canvas,
		GL:              gl,
		Program:         program,
		VertexShader:    vertShader,
		FragShader:      fragShader,
		QuadBuffer:      quadBuffer,
		PositionLoc:     posLoc,
		TimeLoc:         timeLoc,
		ResLoc:          resLoc,
		MouseLoc:        mouseLoc,
		BoxSizeLoc:      boxSizeLoc,
		RadiusLoc:       radiusLoc,
		BorderWidthLoc:  borderWidthLoc,
		BorderColorLoc:  borderColorLoc,
		ShadowSoftLoc:   shadowSoftLoc,
		ShadowOffsetLoc: shadowOffsetLoc,
		ShadowColorLoc:  shadowColorLoc,
		BgColorLoc:      bgColorLoc,
		ColorLoc:        colorLoc,
		StartTime:       float64(time.Now().UnixNano()) / 1e9,
		IsRunning:       true,
	}

	mouseCb := js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		if len(args) > 0 {
			evt := args[0]
			inst.MouseX = float32(evt.Get("clientX").Float())
			inst.MouseY = float32(evt.Get("clientY").Float())
		}
		return nil
	})
	canvas.Call("addEventListener", "mousemove", mouseCb)

	window := js.Global().Get("window")
	var renderFrame js.Func
	renderFrame = js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		if !inst.IsRunning {
			return nil
		}

		cWidth := canvas.Get("clientWidth").Float()
		cHeight := canvas.Get("clientHeight").Float()
		if cWidth > 0 && cHeight > 0 {
			if canvas.Get("width").Float() != cWidth || canvas.Get("height").Float() != cHeight {
				canvas.Set("width", cWidth)
				canvas.Set("height", cHeight)
			}
		}

		w := canvas.Get("width").Float()
		h := canvas.Get("height").Float()
		if w <= 0 {
			w = 300
		}
		if h <= 0 {
			h = 150
		}

		gl.Call("viewport", 0, 0, w, h)
		gl.Call("useProgram", inst.Program)

		if !inst.TimeLoc.IsNull() && !inst.TimeLoc.IsUndefined() {
			currentTime := float64(time.Now().UnixNano())/1e9 - inst.StartTime
			gl.Call("uniform1f", inst.TimeLoc, currentTime)
		}
		if !inst.ResLoc.IsNull() && !inst.ResLoc.IsUndefined() {
			gl.Call("uniform2f", inst.ResLoc, w, h)
		}
		if !inst.MouseLoc.IsNull() && !inst.MouseLoc.IsUndefined() {
			gl.Call("uniform2f", inst.MouseLoc, inst.MouseX, inst.MouseY)
		}

		// Mathematical SDF Box Uniforms
		if !inst.BoxSizeLoc.IsNull() && !inst.BoxSizeLoc.IsUndefined() {
			gl.Call("uniform2f", inst.BoxSizeLoc, w*0.8, h*0.6)
		}
		if !inst.RadiusLoc.IsNull() && !inst.RadiusLoc.IsUndefined() {
			gl.Call("uniform1f", inst.RadiusLoc, 24.0)
		}
		if !inst.BorderWidthLoc.IsNull() && !inst.BorderWidthLoc.IsUndefined() {
			gl.Call("uniform1f", inst.BorderWidthLoc, 2.0)
		}
		if !inst.BorderColorLoc.IsNull() && !inst.BorderColorLoc.IsUndefined() {
			gl.Call("uniform4f", inst.BorderColorLoc, 0.0, 0.95, 1.0, 0.8)
		}
		if !inst.ShadowSoftLoc.IsNull() && !inst.ShadowSoftLoc.IsUndefined() {
			gl.Call("uniform1f", inst.ShadowSoftLoc, 16.0)
		}
		if !inst.ShadowOffsetLoc.IsNull() && !inst.ShadowOffsetLoc.IsUndefined() {
			gl.Call("uniform2f", inst.ShadowOffsetLoc, 0.0, 8.0)
		}
		if !inst.ShadowColorLoc.IsNull() && !inst.ShadowColorLoc.IsUndefined() {
			gl.Call("uniform4f", inst.ShadowColorLoc, 0.0, 0.95, 1.0, 0.35)
		}
		if !inst.BgColorLoc.IsNull() && !inst.BgColorLoc.IsUndefined() {
			gl.Call("uniform4f", inst.BgColorLoc, 0.08, 0.09, 0.14, 0.95)
		}
		if !inst.ColorLoc.IsNull() && !inst.ColorLoc.IsUndefined() {
			gl.Call("uniform4f", inst.ColorLoc, 0.08, 0.09, 0.14, 0.95)
		}

		gl.Call("bindBuffer", gl.Get("ARRAY_BUFFER"), inst.QuadBuffer)
		if !inst.PositionLoc.IsNull() && !inst.PositionLoc.IsUndefined() && inst.PositionLoc.Int() >= 0 {
			gl.Call("enableVertexAttribArray", inst.PositionLoc)
			gl.Call("vertexAttribPointer", inst.PositionLoc, 2, gl.Get("FLOAT"), false, 0, 0)
		}

		gl.Call("drawArrays", gl.Get("TRIANGLES"), 0, 6)

		inst.AnimFrameId = window.Call("requestAnimationFrame", renderFrame)
		return nil
	})

	inst.AnimFrameFunc = renderFrame
	activeShaderInstances[canvasId] = inst

	window.Call("requestAnimationFrame", renderFrame)
}

func jsReloadShader(this js.Value, args []js.Value) interface{} {
	if len(args) < 2 {
		fmt.Println("[GPU HOT-RELOAD] Usage: reloadShader(targetCanvasOrId, fragmentCode)")
		return false
	}

	target := args[0]
	code := args[1].String()

	document := js.Global().Get("document")
	var canvas js.Value
	if target.Type() == js.TypeString {
		targetStr := target.String()
		canvas = document.Call("getElementById", targetStr)
		if canvas.IsNull() || canvas.IsUndefined() {
			canvas = document.Call("querySelector", targetStr)
		}
	} else {
		canvas = target
	}

	if canvas.IsNull() || canvas.IsUndefined() {
		fmt.Println("[GPU HOT-RELOAD] Target canvas not found.")
		return false
	}

	return reloadWebGLShader(canvas, code)
}

func jsCompileShaderTest(this js.Value, args []js.Value) interface{} {
	if len(args) < 1 {
		return false
	}
	code := args[0].String()
	document := js.Global().Get("document")
	canvas := document.Call("createElement", "canvas")
	gl := canvas.Call("getContext", "webgl")
	if gl.IsNull() || gl.IsUndefined() {
		gl = canvas.Call("getContext", "experimental-webgl")
	}
	if gl.IsNull() || gl.IsUndefined() {
		return false
	}
	shader, err := compileShader(gl, gl.Get("FRAGMENT_SHADER"), ensurePrecision(code))
	if err != nil {
		return false
	}
	gl.Call("deleteShader", shader)
	return true
}

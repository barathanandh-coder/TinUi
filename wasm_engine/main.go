package main

import (
	"encoding/json"
	"syscall/js"
)

type Instruction struct {
	Op        string   `json:"op"`
	ID        int      `json:"id,omitempty"`
	Tag       string   `json:"tag,omitempty"`
	Parent    int      `json:"parent,omitempty"`
	Child     int      `json:"child,omitempty"`
	Key       string   `json:"key,omitempty"`
	Value     string   `json:"value,omitempty"`
	Type      string   `json:"type,omitempty"`
	Initial   string   `json:"initial,omitempty"`
	Template  string   `json:"template,omitempty"`
	StateKeys []string `json:"state_keys,omitempty"`
	Event     string   `json:"event,omitempty"`
	Mutation  string   `json:"mutation,omitempty"`
	StateKey    string        `json:"state_key,omitempty"`
	Operator    string        `json:"operator,omitempty"`
	CompareVal  string        `json:"compare_val,omitempty"`
	TrueBranch  []Instruction `json:"true_branch,omitempty"`
	FalseBranch []Instruction `json:"false_branch,omitempty"`
}

var domRefs = make(map[int]js.Value)

func main() {
	js.Global().Set("BootTinUI", js.FuncOf(bootEngine))
	js.Global().Set("TinUIDispatch", js.FuncOf(handleEvent)) // For clicks
	
	// Phase 4: Expose the direct state mutator for text inputs
	js.Global().Set("TinUIMutateState", js.FuncOf(mutateState)) 
	
	select {}
}

func bootEngine(this js.Value, args []js.Value) interface{} {
	irJSON := args[0].String()
	var instructions []Instruction
	json.Unmarshal([]byte(irJSON), &instructions)

	document := js.Global().Get("document")
	domRefs[0] = document.Call("getElementById", "tinui-root")

	for _, inst := range instructions {
		executeInstruction(inst, document)
	}

	return "Milestone 2 Engine Booted"
}

func executeInstruction(inst Instruction, document js.Value) {
	switch inst.Op {
	case "CREATE_NODE":
		el := document.Call("createElement", inst.Tag)
		el.Call("setAttribute", "id", "tin-node") // simplified id
		domRefs[inst.ID] = el

	case "DECLARE_STATE":
		RegisterState(inst.Key, inst.Type, inst.Initial)

	case "BIND_TEXT":
		// 1. Save the relationship so we can update it later
		Bindings[inst.ID] = TextBinding{
			Template:  inst.Template,
			StateKeys: inst.StateKeys,
		}

		// 2. Perform the initial render
		initialText := FormatTemplate(inst.Template, inst.StateKeys)
		domRefs[inst.ID].Set("innerText", initialText)

	case "SET_TEXT":
		domRefs[inst.ID].Set("innerText", inst.Value)

	case "SET_ATTRIBUTE":
		domRefs[inst.ID].Call("setAttribute", inst.Key, inst.Value)

	case "APPEND_CHILD":
		domRefs[inst.Parent].Call("appendChild", domRefs[inst.Child])

	case "ADD_EVENT":
		el := domRefs[inst.ID]
		el.Call("setAttribute", "data-action", inst.Mutation)

	case "BIND_INPUT":
		el := domRefs[inst.ID]
		
		// 1. Tag the element so the JS Bridge knows which variable this modifies
		el.Call("setAttribute", "data-bind", inst.StateKey)
		
		// 2. Hydrate the input with the current memory state on boot
		entry := StateRegistry[inst.StateKey]
		el.Set("value", entry.StrVal)

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
			executeInstruction(branchInst, document)
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
	if entry, exists := StateRegistry[key]; exists {
		entry.StrVal = newValue
		// 2. Flag the Dirty Bitmap
		markDirty(key)
	}

	// 3. Recalculate the UI
	flushPatches()
	
	return nil
}

// handleEvent is the router for mutations
func handleEvent(this js.Value, args []js.Value) interface{} {
	action := args[0].String()

	// In a complete compiler, the logic inside 'increment' would be compiled 
	// into Wasm bytecode. For now, we route it explicitly.
	if action == "increment" {
		StateRegistry["count"].IntVal++
		markDirty("count")
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
			newText := FormatTemplate(binding.Template, binding.StateKeys)
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
				
				// 1. Surgical Unmount: Wipe the anchor's children
				anchor.Set("innerHTML", "")

				// 2. Execute the new branch
				branchToRender := binding.FalseBranch
				if newBool {
					branchToRender = binding.TrueBranch
				}
				
				document := js.Global().Get("document")
				for _, branchInst := range branchToRender {
					branchInst.Parent = anchorID
					executeInstruction(branchInst, document)
				}
			}
		}
	}

	clearAllDirtyBits()
}

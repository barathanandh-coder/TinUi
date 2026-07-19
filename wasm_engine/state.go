package main

import (
	"strconv"
	"strings"
	"sync"
)

// StateEntry holds the actual value in Wasm memory
type StateEntry struct {
	Type     string
	IntVal   int
	StrVal   string
	ArrayVal []string
}

var (
	// The core memory storage: maps "count" -> StateEntry
	StateRegistry = make(map[string]*StateEntry)
	StateMutex    sync.RWMutex

	// Maps the variable name to its bit index (e.g., "count" -> 0, "user" -> 1)
	StateIndexMap = make(map[string]int)
	nextStateBit  = 0

	// The 64-bit dirty tracker
	dirtyBitmap uint64 = 0

	// Tracks which DOM Nodes depend on which templates and state keys
	// Maps DOM Node ID -> Binding Definition
	Bindings = make(map[int]TextBinding)
)

type TextBinding struct {
	Template  string
	StateKeys []string
	Scope     map[string]interface{}
}

// RegisterState is called when Wasm hits DECLARE_STATE
func RegisterState(key, typeHint, initial string) {
	entry := &StateEntry{Type: typeHint}

	if typeHint == "infer" {
		// Simple inference for the PoC
		if val, err := strconv.Atoi(initial); err == nil {
			entry.Type = "int"
			entry.IntVal = val
		} else {
			entry.Type = "string"
			entry.StrVal = initial
		}
	}

	if key == "tasks" {
		entry.ArrayVal = []string{"Buy milk", "Walk dog", "Compile Wasm"}
	}

	StateRegistry[key] = entry
	StateIndexMap[key] = nextStateBit
	nextStateBit++
}

// markDirty dynamically looks up the bit index for a variable and flips it
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

// FormatTemplate replaces "{}" in strings with live memory values
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
			if entry.Type == "int" {
				valStr = strconv.Itoa(entry.IntVal)
			} else {
				valStr = entry.StrVal
			}
		}
		// Replace the first occurrence of "{}" with the state value
		result = strings.Replace(result, "{}", valStr, 1)
	}
	return result
}

// Evaluates a simple logical expression: e.g., (score > 5)
func evalCondition(stateKey, operator, compareValStr string) bool {
	entry := StateRegistry[stateKey]
	
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

// Track conditional logic in the registry
type ConditionalBinding struct {
	StateKey    string
	Operator    string
	CompareVal  string
	TrueBranch  []Instruction
	FalseBranch []Instruction
	CurrentBool bool // Tracks if we are currently showing true or false
}

var ConditionalBindings = make(map[int]*ConditionalBinding)

// Track list logic in the registry
type ListBinding struct {
	IterableKey  string
	IteratorName string
	LoopTemplate []Instruction
}

var ListBindings = make(map[int]*ListBinding)


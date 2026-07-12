package main

// Node represents a UI element entirely in Wasm memory
type Node struct {
	ID       int
	Tag      string
	Text     string
	Classes  string
	ParentID int
}

// Arena is a pre-allocated block of linear memory.
// By indexing nodes directly by their ID, lookups are instant O(1).
var Arena = make([]Node, 1024) 
var MaxNodeID = 0

// Allocate reserves a slot in the memory arena for a new component
func Allocate(id int, tag string) *Node {
	if id >= len(Arena) {
		// Panic in Wasm can be caught by JS, but pre-allocating large chunks is safer
		panic("TinUI Arena Out of Memory! Increase initial allocation.")
	}
	
	Arena[id] = Node{
		ID:  id,
		Tag: tag,
	}
	
	if id > MaxNodeID {
		MaxNodeID = id
	}
	
	return &Arena[id]
}

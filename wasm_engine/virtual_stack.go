//go:build js && wasm

// Package main provides the virtualized high-volume list and stack engine (v1.6)
// Supporting 100,000+ items with O(1) memory windowing and sub-millisecond scrolling.
package main

import (
	"math"
)

// VirtualStackItem represents a single virtualized element node.
type VirtualStackItem struct {
	Index  int     `json:"index"`
	Top    float32 `json:"top"`
	Height float32 `json:"height"`
	Data   any     `json:"data,omitempty"`
}

// VirtualStackConfig holds configuration for the virtual stack container.
type VirtualStackConfig struct {
	TotalCount   int     `json:"total_count"`
	ItemHeight   float32 `json:"item_height"`
	ViewportH    float32 `json:"viewport_height"`
	BufferCount  int     `json:"buffer_count"`
	ScrollOffset float32 `json:"scroll_offset"`
}

// VirtualWindow calculates the slice range [StartIndex, EndIndex) currently visible.
type VirtualWindow struct {
	StartIndex int                `json:"start_index"`
	EndIndex   int                `json:"end_index"`
	OffsetY    float32            `json:"offset_y"`
	TotalH     float32            `json:"total_height"`
	Items      []VirtualStackItem `json:"items"`
}

// ComputeVirtualWindow calculates the visible window of items given current scroll offset.
func ComputeVirtualWindow(config VirtualStackConfig) VirtualWindow {
	if config.ItemHeight <= 0 {
		config.ItemHeight = 40.0
	}
	if config.BufferCount <= 0 {
		config.BufferCount = 5
	}

	totalH := float32(config.TotalCount) * config.ItemHeight

	firstVisible := int(math.Floor(float64(config.ScrollOffset / config.ItemHeight)))
	visibleCount := int(math.Ceil(float64(config.ViewportH / config.ItemHeight)))

	startIdx := firstVisible - config.BufferCount
	if startIdx < 0 {
		startIdx = 0
	}

	endIdx := firstVisible + visibleCount + config.BufferCount
	if endIdx > config.TotalCount {
		endIdx = config.TotalCount
	}

	offsetY := float32(startIdx) * config.ItemHeight

	items := make([]VirtualStackItem, 0, endIdx-startIdx)
	for i := startIdx; i < endIdx; i++ {
		items = append(items, VirtualStackItem{
			Index:  i,
			Top:    float32(i) * config.ItemHeight,
			Height: config.ItemHeight,
		})
	}

	return VirtualWindow{
		StartIndex: startIdx,
		EndIndex:   endIdx,
		OffsetY:    offsetY,
		TotalH:     totalH,
		Items:      items,
	}
}

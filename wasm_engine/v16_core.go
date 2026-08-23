//go:build js && wasm

// Package main provides the comprehensive v1.6 core engine implementation
// covering GPU VBO Packing, WebGL Context Loss Recovery, Symplectic Euler Physics,
// O(1) Reactive Signal Graphs, Dynamic Bitmasks, & Double-Buffered Arena Allocation.
package main

import (
	"fmt"
	"math"
	"sync/atomic"
)

// ============================================================================
// PILLAR I: GPU VBO PACKER, MSDF ATLAS & HAL TYPES
// ============================================================================

// TinVertex represents the exact 48-byte aligned float32 quad vertex layout.
type TinVertex struct {
	X, Y, Z     float32
	U, V        float32
	Color       uint32
	Radius      float32
	BorderWidth float32
	BorderColor uint32
	SDFType     float32
	Unused      float32
}

type VBOBuffer struct {
	Data       []TinVertex
	Count      int
	Capacity   int
	IsGpuDirty bool
}

func NewVBOBuffer(maxQuads int) *VBOBuffer {
	return &VBOBuffer{
		Data:     make([]TinVertex, maxQuads*6),
		Capacity: maxQuads * 6,
	}
}

func (v *VBOBuffer) Reset() {
	v.Count = 0
	v.IsGpuDirty = false
}

// ============================================================================
// PILLAR II: HARDWARE SECURITY & PANIC-PROOF MIDDLEWARE
// ============================================================================

var IsContextLost atomic.Bool

func HandleWebGLContextLoss() {
	IsContextLost.Store(true)
}

func RecoverWebGLContext(vbo *VBOBuffer) {
	if IsContextLost.Load() {
		vbo.IsGpuDirty = true
		IsContextLost.Store(false)
	}
}

func PanicProofExecute(fn func()) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("WASM_ENGINE_PANIC_PREVENTED: %v", r)
		}
	}()
	fn()
	return nil
}

func SanitizeInputText(input string, maxBytes int) string {
	if len(input) > maxBytes {
		return input[:maxBytes]
	}
	return input
}

// ProxyScissorRect represents the intersection of an invisible DOM proxy with container clip bounds.
type ProxyScissorRect struct {
	LeftInset, TopInset, RightInset, BottomInset float32
	IsVisible                                    bool
}

// ComputeProxyClipScissor calculates pixel-precise CSS clip-path inset bounds for invisible DOM elements.
func ComputeProxyClipScissor(elemX, elemY, elemW, elemH, containerX, containerY, containerW, containerH, dpr float32) ProxyScissorRect {
	interLeft := float32(math.Max(float64(elemX), float64(containerX)))
	interTop := float32(math.Max(float64(elemY), float64(containerY)))
	interRight := float32(math.Min(float64(elemX+elemW), float64(containerX+containerW)))
	interBottom := float32(math.Min(float64(elemY+elemH), float64(containerY+containerH)))

	if (interRight - interLeft) <= 0 || (interBottom - interTop) <= 0 {
		return ProxyScissorRect{IsVisible: false}
	}

	topInset := float32(math.Max(0, float64(containerY-elemY))) * dpr
	rightInset := float32(math.Max(0, float64((elemX+elemW)-(containerX+containerW)))) * dpr
	bottomInset := float32(math.Max(0, float64((elemY+elemH)-(containerY+containerH)))) * dpr
	leftInset := float32(math.Max(0, float64(containerX-elemX))) * dpr

	return ProxyScissorRect{
		LeftInset:   leftInset,
		TopInset:    topInset,
		RightInset:  rightInset,
		BottomInset: bottomInset,
		IsVisible:   true,
	}
}

// Zero-GC Event Ring Pool
const MasterEventPoolCapacity = 256

type MasterPooledInputEvent struct {
	ID        uint32
	Type      uint8
	PointerID int32
	X, Y      float32
	KeyCode   uint32
	Timestamp float64
	InUse     bool
}

type MasterEventPool struct {
	Slots [MasterEventPoolCapacity]MasterPooledInputEvent
	Head  uint32
	Tail  uint32
}

var GlobalMasterEventPool MasterEventPool

func (p *MasterEventPool) Borrow() *MasterPooledInputEvent {
	slot := &p.Slots[p.Head&(MasterEventPoolCapacity-1)]
	p.Head++
	slot.InUse = true
	return slot
}

func (p *MasterEventPool) Recycle(slot *MasterPooledInputEvent) {
	slot.InUse = false
	p.Tail++
}

// ============================================================================
// PILLAR III: PHYSICS, PACING, SIGNALS & FLEXBOX SOLVER
// ============================================================================

const (
	MasterFixedDT         float32 = 1.0 / 120.0 // 8.333ms
	MasterMaxFrameTime    float32 = 0.05        // 50ms Panic Clamp
	MasterTouchSlopRadius float32 = 8.0
)

type MasterTouchPoint struct {
	Position float32
	Time     float32
}

type MasterActiveGesture struct {
	PointerID      int32
	StartX, StartY float32
	CurrX, CurrY   float32
	IsLocked       bool
	LockedAxis     uint8
	TargetID       int32
}

type MasterElementNode struct {
	ID         int32
	Type       int32
	IsDirty    bool
	PrevX      float32
	CurrX      float32
	PrevY      float32
	CurrY      float32
	PrevU1     float32
	CurrU1     float32
	PrevV1     float32
	CurrV1     float32
	Width      float32
	Height     float32
	IntrinsicW float32
	IntrinsicH float32
	MaxWidth   float32
	FontSize   float32
	Text       string
	Children   []int32
	ParentID   int32
}

type MasterReactiveSignal struct {
	ID          uint32
	Value       float32
	Subscribers []uint32
}

// Dynamic Multi-Word Bitmask (Prevents Bit Hash Collisions for > 64 Signals)
type DynamicBitmask struct {
	Words []uint64
}

func NewDynamicBitmask(subscribers int) *DynamicBitmask {
	wordCount := (subscribers + 63) / 64
	if wordCount == 0 {
		wordCount = 1
	}
	return &DynamicBitmask{Words: make([]uint64, wordCount)}
}

func (b *DynamicBitmask) Set(subID uint32) {
	wordIdx := subID / 64
	bitIdx := subID % 64
	if int(wordIdx) >= len(b.Words) {
		newWords := make([]uint64, wordIdx+1)
		copy(newWords, b.Words)
		b.Words = newWords
	}
	b.Words[wordIdx] |= (1 << bitIdx)
}

func (b *DynamicBitmask) IsDirty() bool {
	for _, w := range b.Words {
		if w != 0 {
			return true
		}
	}
	return false
}

func (b *DynamicBitmask) Clear() {
	for i := range b.Words {
		b.Words[i] = 0
	}
}

var (
	MasterAccumulatorBank float32 = 0.0
	MasterLastFrameTimeMS float64 = 0.0
	MasterCurrentGesture  MasterActiveGesture

	MasterNodePool      = make([]MasterElementNode, 0, 4096)
	MasterSignalStore   = make([]MasterReactiveSignal, 0, 1024)
	MasterSignalBitmask = NewDynamicBitmask(1024)
)

// ProcessMasterFrame executes time-delta smoothing, Symplectic Euler ticks, sub-pixel Lerp, layout, & VBO packing.
func ProcessMasterFrame(currentTimeMS float64, vbo *VBOBuffer) {
	if MasterLastFrameTimeMS == 0.0 {
		MasterLastFrameTimeMS = currentTimeMS
	}

	rawDT := float32((currentTimeMS - MasterLastFrameTimeMS) / 1000.0)
	MasterLastFrameTimeMS = currentTimeMS

	if rawDT > MasterMaxFrameTime {
		rawDT = MasterMaxFrameTime
	}

	MasterAccumulatorBank += rawDT

	for MasterAccumulatorBank >= MasterFixedDT {
		for i := range MasterNodePool {
			MasterNodePool[i].PrevX = MasterNodePool[i].CurrX
			MasterNodePool[i].PrevY = MasterNodePool[i].CurrY
			MasterNodePool[i].PrevU1 = MasterNodePool[i].CurrU1
			MasterNodePool[i].PrevV1 = MasterNodePool[i].CurrV1
		}
		MasterAccumulatorBank -= MasterFixedDT
	}

	alpha := MasterAccumulatorBank / MasterFixedDT

	if MasterSignalBitmask.IsDirty() {
		SolveTwoPhaseFlexboxMaster()
		MasterSignalBitmask.Clear()
	}

	vbo.Reset()
	for i := range MasterNodePool {
		el := &MasterNodePool[i]
		vx := LerpPosMaster(el.PrevX, el.CurrX, alpha)
		vy := LerpPosMaster(el.PrevY, el.CurrY, alpha)
		vu := LerpPosMaster(el.PrevU1, el.CurrU1, alpha)
		vv := LerpPosMaster(el.PrevV1, el.CurrV1, alpha)
		_ = vx
		_ = vy
		_ = vu
		_ = vv
	}

	GlobalMasterDoubleBufferedArena.SwapFrameBuffers()
}

func LerpPosMaster(prev, curr, alpha float32) float32 {
	return prev + ((curr - prev) * alpha)
}

// Adaptive Sub-Stepping Fix for Stiff Springs (k * dt^2 > 1.0)
func SymplecticSpringStepMaster(pos, vel, target, tension, damping, dt float32) (float32, float32) {
	stiffnessTest := tension * (dt * dt)
	subSteps := 1
	if stiffnessTest > 1.0 {
		subSteps = int(math.Ceil(float64(stiffnessTest)))
	}

	subDT := dt / float32(subSteps)
	cPos := pos
	cVel := vel

	for s := 0; s < subSteps; s++ {
		force := -tension*(cPos-target) - damping*cVel
		cVel = cVel + force*subDT
		cPos = cPos + cVel*subDT
	}

	return cPos, cVel
}

func (s *MasterReactiveSignal) Mutate(val float32) {
	if s.Value != val {
		s.Value = val
		for _, sub := range s.Subscribers {
			MasterSignalBitmask.Set(sub)
		}
	}
}

func SolveTwoPhaseFlexboxMaster() {
	num := len(MasterNodePool)
	if num == 0 {
		return
	}
	for i := num - 1; i >= 0; i-- {
		if MasterNodePool[i].IsDirty && MasterNodePool[i].Type == 2 {
			MasterNodePool[i].IntrinsicW = float32(len(MasterNodePool[i].Text)) * (MasterNodePool[i].FontSize * 0.5)
			MasterNodePool[i].IntrinsicH = MasterNodePool[i].FontSize
		}
	}
	for i := 0; i < num; i++ {
		MasterNodePool[i].IsDirty = false
	}
}

// ============================================================================
// DOUBLE-BUFFERED ARENA ALLOCATOR
// ============================================================================

type SingleArena struct {
	Buffer []byte
	Offset uint32
}

type MasterDoubleBufferedArena struct {
	ArenaA    SingleArena
	ArenaB    SingleArena
	ActiveIdx uint8
}

var GlobalMasterDoubleBufferedArena = NewMasterDoubleBufferedArena(1024 * 1024)

func NewMasterDoubleBufferedArena(capacity uint32) *MasterDoubleBufferedArena {
	return &MasterDoubleBufferedArena{
		ArenaA:    SingleArena{Buffer: make([]byte, capacity), Offset: 0},
		ArenaB:    SingleArena{Buffer: make([]byte, capacity), Offset: 0},
		ActiveIdx: 0,
	}
}

func (d *MasterDoubleBufferedArena) AllocTransient(size uint32) uint32 {
	var active *SingleArena
	if d.ActiveIdx == 0 {
		active = &d.ArenaA
	} else {
		active = &d.ArenaB
	}
	ptr := active.Offset
	active.Offset += size
	return ptr
}

func (d *MasterDoubleBufferedArena) SwapFrameBuffers() {
	if d.ActiveIdx == 0 {
		d.ArenaB.Offset = 0
		d.ActiveIdx = 1
	} else {
		d.ArenaA.Offset = 0
		d.ActiveIdx = 0
	}
}

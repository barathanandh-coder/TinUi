package compiler

import (
	"bytes"
	"encoding/binary"
)

const (
	Magic   = "TINB"
	Version = uint16(1)

	OpCreateNodeInt   = uint8(1)
	OpSetAttributeInt = uint8(2)
	OpSetTextInt      = uint8(3)
	OpAppendChildInt  = uint8(4)
)

func EncodeBinaryIR(instructions []Instruction) ([]byte, error) {
	stringTable := make(map[string]uint16)
	var stringList []string

	getStrIdx := func(s string) uint16 {
		if idx, exists := stringTable[s]; exists {
			return idx
		}
		idx := uint16(len(stringList))
		stringTable[s] = idx
		stringList = append(stringList, s)
		return idx
	}

	// Pre-populate empty string
	getStrIdx("")

	// First pass: collect all strings for supported opcodes
	for _, item := range instructions {
		switch item.Op {
		case OpCreateNode:
			tag := item.Tag
			if tag == "" {
				tag = "div"
			}
			getStrIdx(tag)
		case OpSetAttribute:
			getStrIdx(item.Key)
			getStrIdx(item.Value)
		case OpSetText:
			getStrIdx(item.Value)
		}
	}

	buf := new(bytes.Buffer)

	// Encode header
	buf.WriteString(Magic)
	if err := binary.Write(buf, binary.LittleEndian, Version); err != nil {
		return nil, err
	}

	// Encode string table
	if err := binary.Write(buf, binary.LittleEndian, uint32(len(stringList))); err != nil {
		return nil, err
	}
	for _, s := range stringList {
		encoded := []byte(s)
		if err := binary.Write(buf, binary.LittleEndian, uint16(len(encoded))); err != nil {
			return nil, err
		}
		buf.Write(encoded)
	}

	// Encode opcodes
	if err := binary.Write(buf, binary.LittleEndian, uint32(len(instructions))); err != nil {
		return nil, err
	}
	for _, item := range instructions {
		switch item.Op {
		case OpCreateNode:
			buf.WriteByte(OpCreateNodeInt)
			binary.Write(buf, binary.LittleEndian, uint32(item.ID))
			tag := item.Tag
			if tag == "" {
				tag = "div"
			}
			binary.Write(buf, binary.LittleEndian, getStrIdx(tag))

		case OpSetAttribute:
			buf.WriteByte(OpSetAttributeInt)
			binary.Write(buf, binary.LittleEndian, uint32(item.ID))
			binary.Write(buf, binary.LittleEndian, getStrIdx(item.Key))
			binary.Write(buf, binary.LittleEndian, getStrIdx(item.Value))

		case OpSetText:
			buf.WriteByte(OpSetTextInt)
			binary.Write(buf, binary.LittleEndian, uint32(item.ID))
			binary.Write(buf, binary.LittleEndian, getStrIdx(item.Value))

		case OpAppendChild:
			buf.WriteByte(OpAppendChildInt)
			isRoot := uint8(0)
			if item.Parent == 0 {
				isRoot = 1
			}
			buf.WriteByte(isRoot)
			binary.Write(buf, binary.LittleEndian, uint32(item.Parent))
			binary.Write(buf, binary.LittleEndian, uint32(item.Child))

		default:
			// Unsupported ops are encoded as 0 byte by the Python logic
			buf.WriteByte(0)
		}
	}

	return buf.Bytes(), nil
}

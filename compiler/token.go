package compiler

type TokenType string

type Token struct {
	Type    TokenType
	Literal string
}

const (
	ILLEGAL   TokenType = "ILLEGAL"
	EOF       TokenType = "EOF"
	NEWLINE   TokenType = "NEWLINE"

	// Identifiers and Literals
	IDENT     TokenType = "IDENT"
	STRING    TokenType = "STRING"
	FSTRING   TokenType = "FSTRING"
	NUMBER    TokenType = "NUMBER"

	// Operators and Punctuation
	ASSIGN      TokenType = "="
	PLUS_ASSIGN TokenType = "+="
	COLON       TokenType = ":"
	COMMA       TokenType = ","
	LPAREN      TokenType = "("
	RPAREN      TokenType = ")"

	// Keywords
	COMPONENT TokenType = "COMPONENT"
	STATE     TokenType = "STATE"
	DEF       TokenType = "DEF"

	// Block Formatting
	INDENT TokenType = "INDENT"
	DEDENT TokenType = "DEDENT"
)

var keywords = map[string]TokenType{
	"component": COMPONENT,
	"state":     STATE,
	"def":       DEF,
}

func LookupIdent(ident string) TokenType {
	if tok, ok := keywords[ident]; ok {
		return tok
	}
	return IDENT
}

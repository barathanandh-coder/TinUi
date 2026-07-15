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
	ASSIGN       TokenType = "="
	PLUS_ASSIGN  TokenType = "+="
	MINUS_ASSIGN TokenType = "-="
	COLON        TokenType = ":"
	COMMA       TokenType = ","
	LPAREN      TokenType = "("
	RPAREN      TokenType = ")"

	// Keywords
	COMPONENT TokenType = "COMPONENT"
	STATE     TokenType = "STATE"
	DEF       TokenType = "DEF"
	IF        TokenType = "IF"
	ELSE      TokenType = "ELSE"
	FOR       TokenType = "FOR"
	IN        TokenType = "IN"

	// Operators
	OPERATOR  TokenType = "OPERATOR"

	// Block Formatting
	INDENT TokenType = "INDENT"
	DEDENT TokenType = "DEDENT"
)

var keywords = map[string]TokenType{
	"component": COMPONENT,
	"state":     STATE,
	"def":       DEF,
	"if":        IF,
	"else":      ELSE,
	"for":       FOR,
	"in":        IN,
}

func LookupIdent(ident string) TokenType {
	if tok, ok := keywords[ident]; ok {
		return tok
	}
	return IDENT
}

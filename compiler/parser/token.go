package parser

type TokenType string

const (
	IDENT   TokenType = "IDENT"
	STRING  TokenType = "STRING"
	COLON   TokenType = "COLON"
	INDENT  TokenType = "INDENT"
	DEDENT  TokenType = "DEDENT"
	NEWLINE TokenType = "NEWLINE"
	EOF     TokenType = "EOF"
	ILLEGAL TokenType = "ILLEGAL"
)

type Token struct {
	Type    TokenType
	Literal string
	Line    int
	Column  int
}

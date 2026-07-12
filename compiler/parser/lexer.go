package parser

type Lexer struct {
	input        string
	position     int
	readPosition int
	ch           byte
	line         int
	column       int
	indentStack  []int
	tokensQueue  []Token
}

func NewLexer(input string) *Lexer {
	l := &Lexer{
		input:       input,
		line:        1,
		column:      0,
		indentStack: []int{0},
	}
	l.readChar()
	// Process initial indentation if any
	l.handleIndentation()
	return l
}

func (l *Lexer) readChar() {
	if l.readPosition >= len(l.input) {
		l.ch = 0
	} else {
		l.ch = l.input[l.readPosition]
	}
	l.position = l.readPosition
	l.readPosition++
	l.column++
}

func (l *Lexer) NextToken() Token {
	if len(l.tokensQueue) > 0 {
		tok := l.tokensQueue[0]
		l.tokensQueue = l.tokensQueue[1:]
		return tok
	}

	for {
		if l.ch == 0 {
			for len(l.indentStack) > 1 {
				l.indentStack = l.indentStack[:len(l.indentStack)-1]
				l.tokensQueue = append(l.tokensQueue, Token{Type: DEDENT, Literal: "", Line: l.line, Column: l.column})
			}
			l.tokensQueue = append(l.tokensQueue, Token{Type: EOF, Literal: "", Line: l.line, Column: l.column})
			tok := l.tokensQueue[0]
			l.tokensQueue = l.tokensQueue[1:]
			return tok
		}

		if (l.ch == ' ' || l.ch == '\t') && l.column > 1 {
			l.skipWhitespace()
			continue
		}

		if l.ch == '\n' || l.ch == '\r' {
			tok := l.handleNewline()
			l.tokensQueue = append(l.tokensQueue, tok)
			l.handleIndentation()
			if len(l.tokensQueue) > 0 {
				tok = l.tokensQueue[0]
				l.tokensQueue = l.tokensQueue[1:]
				return tok
			}
			continue
		}

		if l.ch == '#' {
			l.skipUntilNewline()
			continue
		}

		var tok Token
		tok.Line = l.line
		tok.Column = l.column

		switch l.ch {
		case ':':
			tok = Token{Type: COLON, Literal: string(l.ch), Line: l.line, Column: l.column}
			l.readChar()
		case '"', '\'':
			tok.Type = STRING
			tok.Literal = l.readString(l.ch)
		default:
			if isLetter(l.ch) || l.ch == '-' || l.ch == '_' {
				tok.Literal = l.readIdentifier()
				tok.Type = IDENT
				return tok
			} else {
				tok = Token{Type: ILLEGAL, Literal: string(l.ch), Line: l.line, Column: l.column}
				l.readChar()
			}
		}

		return tok
	}
}

func (l *Lexer) handleNewline() Token {
	tok := Token{Type: NEWLINE, Literal: "\n", Line: l.line, Column: l.column}
	if l.ch == '\r' {
		l.readChar()
	}
	if l.ch == '\n' {
		l.readChar()
	}
	l.line++
	l.column = 0
	return tok
}

func (l *Lexer) handleIndentation() {
	spaces := 0
	for l.ch == ' ' || l.ch == '\t' {
		if l.ch == '\t' {
			spaces += 4
		} else {
			spaces += 1
		}
		l.readChar()
	}

	if l.ch == '\n' || l.ch == '\r' || l.ch == 0 || l.ch == '#' {
		return // empty line or comment
	}

	currentIndent := l.indentStack[len(l.indentStack)-1]

	if spaces > currentIndent {
		l.indentStack = append(l.indentStack, spaces)
		l.tokensQueue = append(l.tokensQueue, Token{Type: INDENT, Literal: "", Line: l.line, Column: spaces})
	} else if spaces < currentIndent {
		for len(l.indentStack) > 1 && spaces < l.indentStack[len(l.indentStack)-1] {
			l.indentStack = l.indentStack[:len(l.indentStack)-1]
			l.tokensQueue = append(l.tokensQueue, Token{Type: DEDENT, Literal: "", Line: l.line, Column: spaces})
		}
	}
}

func (l *Lexer) skipWhitespace() {
	for l.ch == ' ' || l.ch == '\t' {
		l.readChar()
	}
}

func (l *Lexer) skipUntilNewline() {
	for l.ch != '\n' && l.ch != '\r' && l.ch != 0 {
		l.readChar()
	}
}

func (l *Lexer) readIdentifier() string {
	position := l.position
	for isLetter(l.ch) || isDigit(l.ch) || l.ch == '-' || l.ch == '_' || l.ch == '.' || l.ch == '%' {
		l.readChar()
	}
	return l.input[position:l.position]
}

func (l *Lexer) readString(quote byte) string {
	position := l.position + 1
	l.readChar()
	for l.ch != quote && l.ch != 0 {
		l.readChar()
	}
	str := l.input[position:l.position]
	if l.ch == quote {
		l.readChar()
	}
	return str
}

func isLetter(ch byte) bool {
	return 'a' <= ch && ch <= 'z' || 'A' <= ch && ch <= 'Z' || ch == '_'
}

func isDigit(ch byte) bool {
	return '0' <= ch && ch <= '9'
}

package compiler

type Lexer struct {
	input        string
	position     int
	readPosition int
	ch           byte
	isLineStart  bool
	indentStack  []int
	pending      []Token
}

func NewLexer(input string) *Lexer {
	l := &Lexer{
		input:       input,
		isLineStart: true,
		indentStack: []int{0},
	}
	l.readChar()
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
}

func (l *Lexer) peekChar() byte {
	if l.readPosition >= len(l.input) {
		return 0
	}
	return l.input[l.readPosition]
}

func (l *Lexer) NextToken() Token {
	if len(l.pending) > 0 {
		tok := l.pending[0]
		l.pending = l.pending[1:]
		return tok
	}

	if l.isLineStart {
		l.isLineStart = false
		spaces := 0
		for l.ch == ' ' || l.ch == '\t' {
			if l.ch == '\t' {
				spaces += 4
			} else {
				spaces++
			}
			l.readChar()
		}

		if l.ch == '\n' || l.ch == '\r' || l.ch == '#' || l.ch == 0 {
			if l.ch == '#' {
				for l.ch != '\n' && l.ch != '\r' && l.ch != 0 {
					l.readChar()
				}
			}
			
			if l.ch == 0 {
			    l.isLineStart = false
			} else {
				l.isLineStart = true
				// Skip the newline since we are already on an empty line
				if l.ch == '\r' {
					l.readChar()
				}
				if l.ch == '\n' {
					l.readChar()
				}
				return l.NextToken()
			}
		}

		currentIndent := l.indentStack[len(l.indentStack)-1]

		if spaces > currentIndent {
			l.indentStack = append(l.indentStack, spaces)
			return Token{Type: INDENT, Literal: ""}
		}

		if spaces < currentIndent {
			for len(l.indentStack) > 1 && spaces < l.indentStack[len(l.indentStack)-1] {
				l.indentStack = l.indentStack[:len(l.indentStack)-1]
				l.pending = append(l.pending, Token{Type: DEDENT, Literal: ""})
			}
			return l.NextToken()
		}
	}

	for l.ch == ' ' || l.ch == '\t' {
		l.readChar()
	}

	if l.ch == '#' {
		for l.ch != '\n' && l.ch != '\r' && l.ch != 0 {
			l.readChar()
		}
	}

	var tok Token

	switch l.ch {
	case '=':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = Token{Type: OPERATOR, Literal: string(ch) + string(l.ch)}
		} else {
			tok = Token{Type: ASSIGN, Literal: string(l.ch)}
		}
	case '!':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = Token{Type: OPERATOR, Literal: string(ch) + string(l.ch)}
		} else {
			tok = Token{Type: ILLEGAL, Literal: string(l.ch)}
		}
	case '+':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = Token{Type: PLUS_ASSIGN, Literal: string(ch) + string(l.ch)}
		} else {
			tok = Token{Type: ILLEGAL, Literal: string(l.ch)}
		}
	case '-':
		if l.peekChar() == '=' {
			ch := l.ch
			l.readChar()
			tok = Token{Type: MINUS_ASSIGN, Literal: string(ch) + string(l.ch)}
		} else {
			tok = Token{Type: ILLEGAL, Literal: string(l.ch)}
		}
	case ':':
		tok = Token{Type: COLON, Literal: string(l.ch)}
	case ',':
		tok = Token{Type: COMMA, Literal: string(l.ch)}
	case '(':
		tok = Token{Type: LPAREN, Literal: string(l.ch)}
	case ')':
		tok = Token{Type: RPAREN, Literal: string(l.ch)}
	case '\n', '\r':
		if l.ch == '\r' {
			l.readChar()
			if l.ch != '\n' {
				tok = Token{Type: ILLEGAL, Literal: "\r"}
				return tok
			}
		}
		tok = Token{Type: NEWLINE, Literal: "\n"}
		l.isLineStart = true
	case 0:
		if len(l.indentStack) > 1 {
			for len(l.indentStack) > 1 {
				l.indentStack = l.indentStack[:len(l.indentStack)-1]
				l.pending = append(l.pending, Token{Type: DEDENT, Literal: ""})
			}
			l.pending = append(l.pending, Token{Type: EOF, Literal: ""})
			return l.NextToken()
		}
		tok = Token{Type: EOF, Literal: ""}
	case '"':
		tok.Type = STRING
		tok.Literal = l.readString()
	case 'f':
		if l.peekChar() == '"' {
			l.readChar()
			tok.Type = FSTRING
			tok.Literal = l.readString()
		} else {
			tok.Literal = l.readIdentifier()
			tok.Type = LookupIdent(tok.Literal)
			return tok
		}
	default:
		if isLetter(l.ch) || l.ch == '_' {
			tok.Literal = l.readIdentifier()
			tok.Type = LookupIdent(tok.Literal)
			return tok
		} else if isDigit(l.ch) {
			tok.Literal = l.readNumber()
			tok.Type = NUMBER
			return tok
		} else {
			tok = Token{Type: ILLEGAL, Literal: string(l.ch)}
		}
	}

	l.readChar()
	return tok
}

func (l *Lexer) readIdentifier() string {
	position := l.position
	for isLetter(l.ch) || l.ch == '_' || isDigit(l.ch) {
		l.readChar()
	}
	return l.input[position:l.position]
}

func (l *Lexer) readNumber() string {
	position := l.position
	for isDigit(l.ch) {
		l.readChar()
	}
	return l.input[position:l.position]
}

func (l *Lexer) readString() string {
	position := l.position + 1
	l.readChar()
	for l.ch != '"' && l.ch != 0 {
		l.readChar()
	}
	return l.input[position:l.position]
}

func isLetter(ch byte) bool {
	return ('a' <= ch && ch <= 'z') || ('A' <= ch && ch <= 'Z')
}

func isDigit(ch byte) bool {
	return '0' <= ch && ch <= '9'
}

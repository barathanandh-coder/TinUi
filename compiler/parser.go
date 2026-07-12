package compiler

import (
	"fmt"
)

type Parser struct {
	l         *Lexer
	curToken  Token
	peekToken Token
	Errors    []string
}

func NewParser(l *Lexer) *Parser {
	p := &Parser{
		l:      l,
		Errors: []string{},
	}
	p.nextToken()
	p.nextToken()
	return p
}

func (p *Parser) nextToken() {
	p.curToken = p.peekToken
	p.peekToken = p.l.NextToken()
}

func (p *Parser) Parse() []*Component {
	var components []*Component

	for p.curToken.Type != EOF {
		if p.curToken.Type == NEWLINE {
			p.nextToken()
			continue
		}

		if p.curToken.Type == COMPONENT {
			if comp := p.parseComponent(); comp != nil {
				components = append(components, comp)
			}
		} else {
			p.Errors = append(p.Errors, fmt.Sprintf("Expected component declaration, got %s", p.curToken.Type))
			p.nextToken()
		}
	}
	return components
}

func (p *Parser) parseComponent() *Component {
	comp := &Component{}
	p.nextToken() 

	if p.curToken.Type != IDENT {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected component name, got %s", p.curToken.Type))
		return nil
	}
	comp.Name = p.curToken.Literal
	p.nextToken()

	if p.curToken.Type == LPAREN {
		p.nextToken()
		for p.curToken.Type != RPAREN && p.curToken.Type != EOF {
			if p.curToken.Type == IDENT {
				comp.Args = append(comp.Args, p.curToken.Literal)
			}
			p.nextToken()
		}
		p.nextToken() 
	}

	if p.curToken.Type == COLON {
		p.nextToken()
		if p.curToken.Type == NEWLINE {
			p.nextToken()
		}

		if p.curToken.Type == INDENT {
			p.nextToken()
			for p.curToken.Type != DEDENT && p.curToken.Type != EOF {
				if p.curToken.Type == NEWLINE {
					p.nextToken()
					continue
				}

				if p.curToken.Type == STATE {
					comp.States = append(comp.States, p.parseState())
				} else if p.curToken.Type == DEF {
					comp.Mutations = append(comp.Mutations, p.parseMutation())
				} else if p.curToken.Type == IDENT {
					if node := p.parseNode(); node != nil {
						comp.RootNodes = append(comp.RootNodes, node)
					}
				} else {
					p.Errors = append(p.Errors, fmt.Sprintf("Unexpected token in component body: %s", p.curToken.Type))
					p.nextToken()
				}
			}
			p.nextToken() 
		}
	}
	return comp
}

func (p *Parser) parseState() *StateDecl {
	p.nextToken() 
	state := &StateDecl{}
	
	if p.curToken.Type == IDENT {
		state.Name = p.curToken.Literal
		p.nextToken()
	}
	if p.curToken.Type == ASSIGN {
		p.nextToken()
		if p.curToken.Type == NUMBER || p.curToken.Type == STRING || p.curToken.Type == IDENT {
			state.Initial = p.curToken.Literal
			p.nextToken()
		}
	}
	return state
}

func (p *Parser) parseMutation() *Mutation {
	p.nextToken() 
	mut := &Mutation{}
	if p.curToken.Type == IDENT {
		mut.Name = p.curToken.Literal
		p.nextToken()
	}
	if p.curToken.Type == LPAREN {
		p.nextToken()
		if p.curToken.Type == RPAREN {
			p.nextToken()
		}
	}
	if p.curToken.Type == COLON {
		p.nextToken()
		if p.curToken.Type == NEWLINE {
			p.nextToken()
		}
		if p.curToken.Type == INDENT {
			p.nextToken()
			if p.curToken.Type == IDENT {
				target := p.curToken.Literal
				p.nextToken()
				if p.curToken.Type == PLUS_ASSIGN {
					p.nextToken()
					if p.curToken.Type == NUMBER {
						mut.Body = target + " += " + p.curToken.Literal
						p.nextToken()
					}
				}
			}
			for p.curToken.Type != DEDENT && p.curToken.Type != EOF {
			    p.nextToken()
			}
			p.nextToken() 
		}
	}
	return mut
}

func (p *Parser) parseNode() *Node {
	node := &Node{
		Name:       p.curToken.Literal,
		Attributes: make(map[string]string),
	}
	p.nextToken()

	if p.curToken.Type == LPAREN {
		p.parseArguments(node)
	}

	if p.curToken.Type == COLON {
		p.nextToken() 
		
		if p.curToken.Type == NEWLINE {
			p.nextToken() 
		}

		if p.curToken.Type == INDENT {
			p.nextToken() 
			
			for p.curToken.Type != DEDENT && p.curToken.Type != EOF {
				if p.curToken.Type == NEWLINE {
					p.nextToken()
					continue
				}
				if child := p.parseNode(); child != nil {
					node.Children = append(node.Children, child)
				}
			}
			p.nextToken() 
		}
	}

	return node
}

func (p *Parser) parseArguments(node *Node) {
	p.nextToken() 

	for p.curToken.Type != RPAREN && p.curToken.Type != EOF {
		if p.curToken.Type == STRING || p.curToken.Type == FSTRING {
		    if p.curToken.Type == FSTRING {
		        node.IsFString = true
		    }
			node.Args = append(node.Args, p.curToken.Literal)
			p.nextToken()
		} else if p.curToken.Type == IDENT {
			key := p.curToken.Literal
			p.nextToken()

			if p.curToken.Type == ASSIGN {
				p.nextToken()
				if p.curToken.Type == STRING || p.curToken.Type == IDENT {
					node.Attributes[key] = p.curToken.Literal
					p.nextToken() 
				}
			}
		}

		if p.curToken.Type == COMMA {
			p.nextToken()
		}
	}
	p.nextToken() 
}

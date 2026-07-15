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
					comp.Mutations = append(comp.Mutations, p.parseDefStatement())
				} else if p.curToken.Type == IDENT {
					if node := p.parseNode(); node != nil {
						comp.RootNodes = append(comp.RootNodes, node)
					}
				} else if p.curToken.Type == IF {
					if node := p.parseIfStatement(); node != nil {
						comp.RootNodes = append(comp.RootNodes, node)
					}
				} else if p.curToken.Type == FOR {
					if node := p.parseForStatement(); node != nil {
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

func (p *Parser) parseDefStatement() *DefNode {
	p.nextToken() 
	funcName := ""
	if p.curToken.Type == IDENT {
		funcName = p.curToken.Literal
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
		
		var mutations []MutationNode
		if p.curToken.Type == INDENT {
			p.nextToken()
			
			for p.curToken.Type != DEDENT && p.curToken.Type != EOF {
				if p.curToken.Type == NEWLINE {
					p.nextToken()
					continue
				}
				
				if p.curToken.Type == IDENT {
					targetVar := p.curToken.Literal
					p.nextToken()
					
					var operator string
					if p.curToken.Type == ASSIGN || p.curToken.Type == PLUS_ASSIGN || p.curToken.Type == MINUS_ASSIGN || p.curToken.Type == OPERATOR {
						operator = p.curToken.Literal
						p.nextToken()
					}
					
					valToken := p.curToken
					p.nextToken()
					
					mutations = append(mutations, MutationNode{
						StateKey: targetVar,
						Operator: operator,
						Value:    valToken.Literal,
					})
				} else {
					p.nextToken() 
				}
			}
			p.nextToken() 
			
			return &DefNode{
				FuncName:  funcName,
				Mutations: mutations,
			}
		}
	}
	return &DefNode{FuncName: funcName, Mutations: []MutationNode{}}
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
				if p.curToken.Type == IF {
					if child := p.parseIfStatement(); child != nil {
						node.Children = append(node.Children, child)
					}
				} else if p.curToken.Type == FOR {
					if child := p.parseForStatement(); child != nil {
						node.Children = append(node.Children, child)
					}
				} else if child := p.parseNode(); child != nil {
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

func (p *Parser) parseIfStatement() *ConditionalNode {
	p.nextToken() // consume IF

	if p.curToken.Type != IDENT {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected condition variable, got %s", p.curToken.Type))
		return nil
	}
	condVar := p.curToken.Literal
	p.nextToken()

	if p.curToken.Type != OPERATOR {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected operator, got %s", p.curToken.Type))
		return nil
	}
	operator := p.curToken.Literal
	p.nextToken()

	var val string
	if p.curToken.Type == STRING {
		val = p.curToken.Literal
	} else if p.curToken.Type == IDENT {
		val = p.curToken.Literal
	} else {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected value, got %s", p.curToken.Type))
		return nil
	}
	p.nextToken()

	if p.curToken.Type != COLON {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected ':', got %s", p.curToken.Type))
		return nil
	}
	p.nextToken()

	if p.curToken.Type == NEWLINE {
		p.nextToken()
	}

	if p.curToken.Type != INDENT {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected INDENT, got %s", p.curToken.Type))
		return nil
	}
	p.nextToken()

	var trueNodes []ASTNode
	for p.curToken.Type != DEDENT && p.curToken.Type != EOF {
		if p.curToken.Type == NEWLINE {
			p.nextToken()
			continue
		}
		if p.curToken.Type == IF {
			if child := p.parseIfStatement(); child != nil {
				trueNodes = append(trueNodes, child)
			}
		} else if p.curToken.Type == FOR {
			if child := p.parseForStatement(); child != nil {
				trueNodes = append(trueNodes, child)
			}
		} else {
			if child := p.parseNode(); child != nil {
				trueNodes = append(trueNodes, child)
			}
		}
	}
	p.nextToken() // DEDENT

	var falseNodes []ASTNode
	if p.curToken.Type == ELSE {
		p.nextToken() // ELSE
		if p.curToken.Type != COLON {
			p.Errors = append(p.Errors, fmt.Sprintf("Expected ':', got %s", p.curToken.Type))
			return nil
		}
		p.nextToken() // COLON
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
				if p.curToken.Type == IF {
					if child := p.parseIfStatement(); child != nil {
						falseNodes = append(falseNodes, child)
					}
				} else if p.curToken.Type == FOR {
					if child := p.parseForStatement(); child != nil {
						falseNodes = append(falseNodes, child)
					}
				} else {
					if child := p.parseNode(); child != nil {
						falseNodes = append(falseNodes, child)
					}
				}
			}
			p.nextToken() // DEDENT
		}
	}

	return &ConditionalNode{
		ConditionVar: condVar,
		Operator:     operator,
		Value:        val,
		TrueBranch:   trueNodes,
		FalseBranch:  falseNodes,
	}
}

func (p *Parser) parseForStatement() *ForNode {
	p.nextToken() // consume FOR

	if p.curToken.Type != IDENT {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected iterator variable, got %s", p.curToken.Type))
		return nil
	}
	iteratorName := p.curToken.Literal
	p.nextToken()

	if p.curToken.Type != IN {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected 'in', got %s", p.curToken.Type))
		return nil
	}
	p.nextToken()

	if p.curToken.Type != IDENT {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected iterable key, got %s", p.curToken.Type))
		return nil
	}
	iterableKey := p.curToken.Literal
	p.nextToken()

	if p.curToken.Type != COLON {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected ':', got %s", p.curToken.Type))
		return nil
	}
	p.nextToken()

	if p.curToken.Type == NEWLINE {
		p.nextToken()
	}

	if p.curToken.Type != INDENT {
		p.Errors = append(p.Errors, fmt.Sprintf("Expected INDENT, got %s", p.curToken.Type))
		return nil
	}
	p.nextToken()

	var bodyNodes []ASTNode
	for p.curToken.Type != DEDENT && p.curToken.Type != EOF {
		if p.curToken.Type == NEWLINE {
			p.nextToken()
			continue
		}
		if p.curToken.Type == IF {
			if child := p.parseIfStatement(); child != nil {
				bodyNodes = append(bodyNodes, child)
			}
		} else if p.curToken.Type == FOR {
			if child := p.parseForStatement(); child != nil {
				bodyNodes = append(bodyNodes, child)
			}
		} else {
			if child := p.parseNode(); child != nil {
				bodyNodes = append(bodyNodes, child)
			}
		}
	}
	p.nextToken() // DEDENT

	return &ForNode{
		IteratorName: iteratorName,
		IterableKey:  iterableKey,
		Body:         bodyNodes,
	}
}


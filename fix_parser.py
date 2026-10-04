import re

with open("src/compiler/parser.go", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the double line prefix: `[line %d:%d] [line %d:%d]`
content = re.sub(r'\[line %d:%d\] \[line %d:%d\]', '[line %d:%d]', content)

# Fix the arguments lacking line/col:
# We find `p.Errors = append(p.Errors, fmt.Sprintf("[line %d:%d] `
# And ensure `p.curToken.Line, p.curToken.Col, ` is added if not present.
def replacer(match):
    prefix = match.group(1) # e.g. p.Errors = append(p.Errors, fmt.Sprintf("[line %d:%d] Expected...
    args = match.group(2) # e.g. p.curToken.Type
    if "p.curToken.Line" not in args:
        return f'{prefix}p.curToken.Line, p.curToken.Col, {args}'
    return match.group(0)

content = re.sub(r'(p\.Errors = append\(p\.Errors, fmt\.Sprintf\("\[line %d:%d\] [^"]+", )([^)]+\)\))', replacer, content)

with open("src/compiler/parser.go", "w", encoding="utf-8") as f:
    f.write(content)

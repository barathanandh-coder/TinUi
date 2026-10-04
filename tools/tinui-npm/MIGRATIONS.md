# Migrating from TinPyUI v1.x to v1.4.2

## Breaking Changes

### 1. CLI Commands

**v1.x:**
```bash
tinpyui compile src/index.tin
tinpyui serve
```

**v1.4.2:**
```bash
# New dev command with live reload
tinpyui dev src/index.tin

# Or manual compile + serve (still works)
tinpyui compile src/index.tin
tinpyui serve
```

### 2. Prop Passing

**v1.x (broken):**
```tin
FeatureCard(title="My Title")  # title was ignored
```

**v1.4.2 (fixed):**
```tin
FeatureCard(title="My Title")  # title now correctly passed
```

### 3. Multi-Line Props

**v1.x (crashed):**
```tin
Text(
    text="Hello",
    color="cyan"
)
```

**v1.4.2 (works):**
```tin
Text(
    text="Hello",
    color="cyan"
)
```

### 4. Float Values

**v1.x (crashed):**
```tin
Text(lineHeight=1.7)
```

**v1.4.2 (works):**
```tin
Text(lineHeight=1.7)
```

### 5. Event Binding

**v1.x (broken):**
```tin
Button(text="Click", action="submit")  # action was stripped
```

**v1.4.2 (works):**
```tin
Button(text="Click", action="submit")  # action correctly wired
```

## New Features

- `tinpyui dev` — File watching + live reload
- `tinpyui.pyi` — IDE autocomplete support
- Error boundaries — Red screen on render errors
- 14 new components (BlackHoleLogo, ReviewCard, TiltCard, etc.)
- Proper attribute passthrough (href, data-action, data-bind)

## Upgrade Steps

1. Update global install:
   ```bash
   npm install -g tinpyui@latest
   ```

2. Verify version:
   ```bash
   tinpyui --version  # Should show v1.4.2
   ```

3. Test your existing `.tin` files:
   ```bash
   tinpyui dev src/index.tin
   ```

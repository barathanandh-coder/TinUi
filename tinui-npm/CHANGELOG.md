# Changelog

## [1.4.2] - 2026-07-24

### Added
- `tinpyui dev` command with file watching and live reload
- `tinpyui.pyi` type stub for IDE autocomplete
- Error boundary system with red screen overlay
- 14 new components: BlackHoleLogo, ReviewCard, CodeBlock, NeonBadge, NeonBox, FeatureCard, DemoCard, TiltCard, GlassCard, MagneticButton, InfiniteMarquee, TextReveal, CursorTrail, NoiseTexture, Spotlight
- Multi-line prop support in compiler
- Float/decimal number support in compiler
- Generic attribute passthrough (href, data-action, data-bind, etc.)
- Custom component prop substitution
- `engines` field in package.json (Node >= 18)
- `files` field in package.json (cleaner publish)

### Fixed
- NavLink href attribute no longer stripped
- Custom component props now correctly propagated
- Floating-point lexer crash
- Multi-line prop lexer crash
- Event binding (data-action, data-bind) now works
- Silent failures now show red error overlay
- Nested old tarball removed from package

### Changed
- IR version bumped to 2.0.0
- CLI help text updated

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Instruction {
    pub op: String,
    #[serde(default)]
    pub id: Option<i32>,
    #[serde(default)]
    pub tag: Option<String>,
    #[serde(default)]
    pub parent: Option<i32>,
    #[serde(default)]
    pub child: Option<i32>,
    #[serde(default)]
    pub key: Option<String>,
    #[serde(default)]
    pub value: Option<String>,
    #[serde(rename = "type", default)]
    pub prop_type: Option<String>,
    #[serde(default)]
    pub initial: Option<String>,
    #[serde(default)]
    pub template: Option<String>,
    #[serde(default)]
    pub state_keys: Vec<String>,
    #[serde(default)]
    pub event: Option<String>,
    #[serde(default)]
    pub mutation: Option<String>,
    #[serde(default)]
    pub is_hidden: bool,
    #[serde(default)]
    pub state_key: Option<String>,
    #[serde(default)]
    pub operator: Option<String>,
    #[serde(default)]
    pub compare_val: Option<String>,
    #[serde(default)]
    pub true_branch: Vec<Instruction>,
    #[serde(default)]
    pub false_branch: Vec<Instruction>,
    #[serde(default)]
    pub iterable_key: Option<String>,
    #[serde(default)]
    pub iterator_name: Option<String>,
    #[serde(default)]
    pub loop_template: Vec<Instruction>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct IRBlueprint {
    #[serde(default)]
    pub mutations: HashMap<String, Vec<Instruction>>,
    #[serde(default)]
    pub nodes: Vec<Instruction>,
}

#[derive(Debug, Clone)]
pub struct TextBinding {
    pub template: String,
    pub state_keys: Vec<String>,
    pub scope: Option<HashMap<String, String>>,
}

#[derive(Debug, Clone)]
pub struct LoadingBinding {
    pub state_key: String,
    pub loader_type: String,
    pub loader_speed: String,
}

#[derive(Debug, Clone)]
pub struct ConditionalBinding {
    pub state_key: String,
    pub operator: String,
    pub compare_val: String,
    pub true_branch: Vec<Instruction>,
    pub false_branch: Vec<Instruction>,
    pub current_bool: bool,
}

#[derive(Debug, Clone)]
pub struct ListBinding {
    pub iterable_key: String,
    pub iterator_name: String,
    pub loop_template: Vec<Instruction>,
}

#[derive(Debug, Clone)]
pub struct StateEntry {
    pub state_type: String,
    pub str_val: String,
    pub int_val: i64,
}

#[derive(Debug, Clone)]
pub struct ParallaxNode {
    pub id: i32,
    pub speed: f64,
}

pub const ENGINE_CSS: &str = r#"
/* Micro-interactions */
[data-hover-effect="lift"]:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
[data-hover-effect="glow"]:hover { box-shadow: 0 0 15px rgba(255,255,255,0.3); }
[data-hover-effect="scale"]:hover { transform: scale(1.05); }
[data-hover-effect="shift-right"]:hover { transform: translateX(4px); }
[data-hover-effect="dim"]:hover { opacity: 0.7; }

[data-click-effect="press"]:active { transform: scale(0.95); }
[data-click-effect="ripple"]:active { opacity: 0.5; }
[data-click-effect="snap"]:active { transform: scale(0.9); transition: 0.05s !important; }
[data-click-effect="recoil"]:active { transform: translateX(-4px); }

/* Loaders */
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
.tin-loading-skeleton {
	color: transparent !important;
	background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%);
	background-size: 200% 100%;
	animation: shimmer 1.5s infinite linear;
	pointer-events: none;
}
.tin-loading-skeleton * { visibility: hidden !important; }

.tin-loading-shimmer {
	position: relative;
	overflow: hidden;
}
.tin-loading-shimmer::after {
	content: "";
	position: absolute;
	top: 0; left: 0; width: 100%; height: 100%;
	background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
	animation: shimmer 1.2s infinite;
}

.tin-loading-blur-overlay {
	filter: blur(4px);
	pointer-events: none;
	opacity: 0.6;
}

@keyframes spin { to { transform: rotate(360deg); } }
.tin-loading-spinner {
	position: relative;
	color: transparent !important;
	pointer-events: none;
}
.tin-loading-spinner * { visibility: hidden !important; }
.tin-loading-spinner::after {
	content: "";
	position: absolute;
	top: calc(50% - 10px); left: calc(50% - 10px);
	width: 20px; height: 20px;
	border: 2px solid rgba(255,255,255,0.3);
	border-top-color: #fff;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

/* Scroll Reveals */
[data-scroll-reveal] {
	opacity: 0;
	transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
[data-scroll-reveal="fade-up"] { transform: translateY(40px); }
[data-scroll-reveal="zoom-in"] { transform: scale(0.9); }
[data-scroll-reveal="slide-left"] { transform: translateX(-40px); }
[data-scroll-reveal="slide-right"] { transform: translateX(40px); }
[data-scroll-reveal="assemble"] { transform: translateY(20px) scale(0.95) rotateX(10deg); transform-origin: center bottom; perspective: 1000px; }

[data-scroll-reveal].tin-revealed {
	opacity: 1;
	transform: translate(0) scale(1) rotateX(0);
}

/* Parallax */
[data-parallax-speed] {
    will-change: transform;
}

/* Text Cycle Effects */
.tin-cycle-typewriter { animation: typewriter 0.5s steps(20, end); white-space: nowrap; overflow: hidden; display: inline-block; }
@keyframes typewriter { from { width: 0; } to { width: 100%; } }

.tin-cycle-flip-up { animation: flipUp 0.5s ease-out; display: inline-block; }
@keyframes flipUp { from { transform: rotateX(-90deg); opacity: 0; } to { transform: rotateX(0); opacity: 1; } }

.tin-cycle-glitch-swap { animation: glitch 0.3s linear; display: inline-block; }
@keyframes glitch { 
  0% { transform: translate(0); } 
  20% { transform: translate(-2px, 2px); } 
  40% { transform: translate(-2px, -2px); } 
  60% { transform: translate(2px, 2px); } 
  80% { transform: translate(2px, -2px); } 
  100% { transform: translate(0); } 
}

/* Choreography */
@keyframes cascade-down { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes stagger-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes explode-out { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }

/* Attention Effects */
.tin-attention-heartbeat { animation: heartbeat 1s ease-in-out; }
@keyframes heartbeat {
  0% { transform: scale(1); }
  14% { transform: scale(1.1); }
  28% { transform: scale(1); }
  42% { transform: scale(1.1); }
  70% { transform: scale(1); }
}

.tin-attention-bounce { animation: bounce 1s cubic-bezier(0.28, 0.84, 0.42, 1); }
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.tin-attention-pulse { animation: attentionPulse 1.2s cubic-bezier(0.4, 0, 0.6, 1); }
@keyframes attentionPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.05); }
}

.tin-attention-shimmer-border { position: relative; }
.tin-attention-shimmer-border::after {
  content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
  background-size: 200% 100%;
  animation: shimmerBorder 1s linear forwards;
  z-index: -1; border-radius: inherit; pointer-events: none;
}
@keyframes shimmerBorder { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }

.tin-attention-glitch { animation: glitchAttn 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) both; }
@keyframes glitchAttn {
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
}

/* Transitions */
.tin-transition-out { pointer-events: none; }
.tin-transition-in { z-index: 10; }

.tin-anim-fade-in { animation: fadeIn forwards; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.tin-anim-fade-out { animation: fadeOut forwards; }
@keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }

.tin-anim-slide-from-right { animation: slideFromRight forwards; }
@keyframes slideFromRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
.tin-anim-slide-to-left { animation: slideToLeft forwards; }
@keyframes slideToLeft { from { transform: translateX(0); opacity: 1; } to { transform: translateX(-100%); opacity: 0; } }

.tin-anim-scale-up { animation: scaleUp forwards; }
@keyframes scaleUp { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.tin-anim-scale-down { animation: scaleDown forwards; }
@keyframes scaleDown { from { transform: scale(1); opacity: 1; } to { transform: scale(0.9); opacity: 0; } }
"#;

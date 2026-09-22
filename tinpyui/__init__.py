"""
TinPyUI v1.7.0 — Production-Grade Hardware-Accelerated Universal Python GUI Framework Library
"""

__version__ = "1.7.0"

import hashlib
import platform
import random
import sys
import os
import time
import math
import ctypes
import threading
import json
import sqlite3
import csv
import subprocess
from typing import Any, Callable, List, Optional, Union, Dict, Tuple

from .core import (
    SpringPhysics, SpringSolver, Rect, _context_stack,
    eval_prop, safe_eval_prop, failsafe_guard, RecursionGuard,
    ThreadDispatcher, parse_color, Signal, State, Node
)
from .components import (
    Section, Row, Column, Card, LayoutWindow, Spacer, Divider,
    AnimatedBackground, Navbar, Container, Grid, Surface,
    HeroContainer, Header, Footer, Main, Marquee, Modal, Tooltip,
    ShaderLayer, WebGLCanvas, ParticleField,
    Heading, Text, GradientText, Badge, Icon, Link,
    Button, Input, NavItem, Slider, Switch, Progress, ProgressBar,
    Avatar, Image, VirtualStack, VirtualList, Spring,
    DataTable, LiveDataTable, AutoCRUD, Form,
    DataGrid, AIChat, ColorPicker, DatePicker, Calendar,
    Chart, LineChart, BarChart, DonutChart, Sparkline,
    TreeView, TreeNode
)
from .data import (
    Database, Table, QueryBuilder, LiveQuery, SQLiteDatabase, DB, SQLiteDB, db,
    PostgresDatabase, PostgresTable, PostgresDB,
    MongoDatabase, MongoCollection, MongoQueryBuilder, MongoDB,
    RedisDatabase, RedisStore, RedisDB,
    DuckDBDatabase, ClickHouseDatabase,
    connect, KeyValueStore, use_store, model, ModelWrapper
)
from .net import (
    PlatformBridge, haptics, Router, EventBus,
    Storage, storage, HTTPClient, WebSocketConnection,
    use_socket, use_sse, api,
    VectorClock, LWWRegister, MeshState,
    PresenceTracker, MeshNode, use_mesh_state
)
from .security import (
    HoneypotAPI, honeypot, RAMMaskedState, Sanitizer, sanitizer,
    Security, security, EncryptedState, CSRFGuard, csrf,
    SafeStorage, safe_storage, AutoSecurityDefaults,
    SessionBindingGuard, session_guard, SecureCookieGuard, cookie_guard
)
from .utils import (
    AccessibilityManager, a11y, SEOEngine, seo,
    PerformanceMonitor, perf_monitor, GDIPool, FailSafeAssetLoader,
    I18nEngine, i18n, t, set_locale, get_locale,
    is_rtl, get_direction, format_currency, format_number
)
from .shaders import (
    ShaderPreset, GpuPerformanceMode, get_shader_code, set_shader_preset, set_gpu_mode
)
from .morphisms import (
    Morphism, get_morphism_style
)
from .transitions import (
    RedirectTransition, redirect_page, show_toast
)
from .scroll import (
    ScrollSpeedPreset, set_scroll_speed, toggle_auto_scroll
)
from .renderers import (
    DirectGpuSurface, GpuBackend
)
from .app import (
    App, Window, create_window, run, export_mobile, export_android, export_ios
)

__all__ = [
    "SpringPhysics", "SpringSolver", "Rect", "_context_stack",
    "eval_prop", "safe_eval_prop", "failsafe_guard", "RecursionGuard",
    "ThreadDispatcher", "parse_color", "Signal", "State", "Node",
    "Section", "Row", "Column", "Card", "LayoutWindow", "Spacer", "Divider",
    "AnimatedBackground", "Navbar", "Container", "Grid", "Surface",
    "HeroContainer", "Header", "Footer", "Main", "Marquee", "Modal", "Tooltip",
    "ShaderLayer", "WebGLCanvas", "ParticleField",
    "Heading", "Text", "GradientText", "Badge", "Icon", "Link",
    "Button", "Input", "NavItem", "Slider", "Switch", "Progress", "ProgressBar",
    "Avatar", "Image", "VirtualStack", "VirtualList", "Spring",
    "DataTable", "LiveDataTable", "AutoCRUD", "Form",
    "DataGrid", "AIChat", "ColorPicker", "DatePicker", "Calendar",
    "Chart", "LineChart", "BarChart", "DonutChart", "Sparkline",
    "TreeView", "TreeNode",
    "Database", "Table", "QueryBuilder", "LiveQuery", "SQLiteDatabase", "DB", "SQLiteDB", "db",
    "PostgresDatabase", "PostgresTable", "PostgresDB",
    "MongoDatabase", "MongoCollection", "MongoQueryBuilder", "MongoDB",
    "RedisDatabase", "RedisStore", "RedisDB",
    "DuckDBDatabase", "ClickHouseDatabase",
    "connect", "KeyValueStore", "use_store", "model", "ModelWrapper",
    "PlatformBridge", "haptics", "Router", "EventBus",
    "Storage", "storage", "HTTPClient", "WebSocketConnection",
    "use_socket", "use_sse", "api",
    "VectorClock", "LWWRegister", "MeshState", "PresenceTracker", "MeshNode", "use_mesh_state",
    "HoneypotAPI", "honeypot", "RAMMaskedState", "Sanitizer", "sanitizer",
    "Security", "security", "EncryptedState", "CSRFGuard", "csrf",
    "SafeStorage", "safe_storage", "AutoSecurityDefaults",
    "SessionBindingGuard", "session_guard", "SecureCookieGuard", "cookie_guard",
    "AccessibilityManager", "a11y", "SEOEngine", "seo",
    "PerformanceMonitor", "perf_monitor", "GDIPool", "FailSafeAssetLoader",
    "I18nEngine", "i18n", "t", "set_locale", "get_locale", "is_rtl", "get_direction", "format_currency", "format_number",
    "ShaderPreset", "GpuPerformanceMode", "get_shader_code", "set_shader_preset", "set_gpu_mode",
    "Morphism", "get_morphism_style",
    "RedirectTransition", "redirect_page", "show_toast",
    "ScrollSpeedPreset", "set_scroll_speed", "toggle_auto_scroll",
    "DirectGpuSurface", "GpuBackend",
    "App", "Window", "create_window", "run", "export_mobile", "export_android", "export_ios"
]


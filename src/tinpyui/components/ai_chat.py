"""
TinPyUI AI Chat & LLM Streaming Component
Features real-time token streaming, code block formatting, copy button, and chat bubbles.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Union
from ..core.node import Node
from ..core.signals import Signal

class AIChat(Node):
    """AI Conversational Streaming Chat component with Markdown & code highlight support."""

    def __init__(
        self,
        messages: Optional[Union[List[Dict[str, Any]], Signal]] = None,
        model_name: str = "AI Assistant",
        avatar: Optional[str] = None,
        user_avatar: Optional[str] = None,
        placeholder: str = "Ask anything or write a prompt... (Enter to send)",
        on_send: Optional[Callable[[str], None]] = None,
        height: str = "600px",
        **kwargs
    ):
        self.model_name = model_name
        self.on_send = on_send
        self._is_streaming = False
        self._current_stream_buffer = ""

        if isinstance(messages, Signal):
            self._messages_signal = messages
            self._messages = list(messages.value or [])
            messages.subscribe(self._on_messages_signal_update)
        else:
            self._messages_signal = None
            self._messages = list(messages or [])

        super().__init__(
            "AIChat",
            messages=self._messages,
            model_name=model_name,
            avatar=avatar,
            user_avatar=user_avatar,
            placeholder=placeholder,
            height=height,
            is_streaming=self._is_streaming,
            on_send=self._handle_user_send,
            **kwargs
        )

    def _on_messages_signal_update(self, new_val):
        self._messages = list(new_val or [])
        self.props["messages"] = self._messages

    def _handle_user_send(self, text: str):
        if not text or not text.strip():
            return
        cleaned = text.strip()
        self.append_message("user", cleaned)
        if self.on_send:
            self.on_send(cleaned)

    def append_message(self, role: str, content: str, meta: Optional[Dict[str, Any]] = None):
        """Appends a new complete message to the chat history."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": time.strftime("%H:%M:%S"),
            "meta": meta or {}
        }
        self._messages.append(msg)
        self.props["messages"] = list(self._messages)
        if self._messages_signal:
            self._messages_signal.value = list(self._messages)

    def start_stream(self, role: str = "assistant", initial_token: str = ""):
        """Initiates an active streaming token response."""
        self._is_streaming = True
        self._current_stream_buffer = initial_token
        msg = {
            "role": role,
            "content": initial_token,
            "timestamp": time.strftime("%H:%M:%S"),
            "streaming": True
        }
        self._messages.append(msg)
        self.props["is_streaming"] = True
        self.props["messages"] = list(self._messages)

    def stream_token(self, token: str):
        """Appends an incoming streaming token and updates UI."""
        if not self._is_streaming or not self._messages:
            self.start_stream(initial_token=token)
            return

        self._current_stream_buffer += token
        self._messages[-1]["content"] = self._current_stream_buffer
        self.props["messages"] = list(self._messages)
        if self._messages_signal:
            self._messages_signal.value = list(self._messages)

    def end_stream(self):
        """Finalizes the current streaming response."""
        self._is_streaming = False
        if self._messages and self._messages[-1].get("streaming"):
            self._messages[-1]["streaming"] = False
        self.props["is_streaming"] = False
        self.props["messages"] = list(self._messages)
        if self._messages_signal:
            self._messages_signal.value = list(self._messages)

    def clear(self):
        """Clears all messages."""
        self._messages.clear()
        self._is_streaming = False
        self._current_stream_buffer = ""
        self.props["messages"] = []
        self.props["is_streaming"] = False
        if self._messages_signal:
            self._messages_signal.value = []

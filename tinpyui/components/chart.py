"""
TinPyUI Declarative Reactive SVG Charting Suite
Supports Line, Bar, Donut, and Sparkline charts with responsive vector generation and Signal bindings.
"""

import math
from typing import Any, Callable, Dict, List, Optional, Union
from ..core.node import Node
from ..core.signals import Signal

class Chart(Node):
    """Universal reactive SVG Chart base node."""

    def __init__(
        self,
        chart_type: str = "line",
        data: Optional[Union[List[Union[float, int, Dict[str, Any]]], Signal]] = None,
        labels: Optional[List[str]] = None,
        width: str = "100%",
        height: str = "300px",
        colors: Optional[List[str]] = None,
        title: Optional[str] = None,
        **kwargs
    ):
        self.chart_type = chart_type
        self.width = width
        self.height = height
        self.colors = colors or ["#00f2fe", "#4facfe", "#00ff88", "#ff007f", "#ffaa00"]
        self.title = title

        if isinstance(data, Signal):
            self._data_signal = data
            self._raw_data = list(data.value or [])
            data.subscribe(self._on_data_signal_update)
        else:
            self._data_signal = None
            self._raw_data = list(data or [])

        self._labels = labels or []
        svg_content = self.render_svg()

        super().__init__(
            "Chart",
            chart_type=chart_type,
            data=self._raw_data,
            labels=self._labels,
            width=width,
            height=height,
            colors=self.colors,
            title=title,
            svg=svg_content,
            **kwargs
        )

    def _on_data_signal_update(self, new_val):
        self._raw_data = list(new_val or [])
        self.props["data"] = self._raw_data
        self.props["svg"] = self.render_svg()

    def set_data(self, new_data: List[Any], new_labels: Optional[List[str]] = None):
        """Updates chart data points and regenerates SVG."""
        self._raw_data = list(new_data)
        if new_labels is not None:
            self._labels = new_labels
        self.props["data"] = self._raw_data
        self.props["labels"] = self._labels
        self.props["svg"] = self.render_svg()
        if self._data_signal:
            self._data_signal.value = self._raw_data

    def _extract_values(self) -> List[float]:
        values = []
        for item in self._raw_data:
            if isinstance(item, (int, float)):
                values.append(float(item))
            elif isinstance(item, dict):
                # Try common keys
                val = item.get("value", item.get("val", item.get("y", 0)))
                values.append(float(val) if isinstance(val, (int, float)) else 0.0)
        return values

    def render_svg(self) -> str:
        """Generates self-contained scalable SVG XML string."""
        values = self._extract_values()
        if not values:
            return '<svg viewBox="0 0 500 200" width="100%" height="100%"><text x="250" y="100" fill="#666" text-anchor="middle">No Data</text></svg>'

        w = 500
        h = 220
        pad_x = 40
        pad_y = 30
        plot_w = w - (pad_x * 2)
        plot_h = h - (pad_y * 2)

        min_val = min(values) if min(values) < 0 else 0
        max_val = max(values) if max(values) > 0 else 1
        val_range = max_val - min_val or 1.0

        if self.chart_type == "bar":
            bars = []
            num_bars = len(values)
            bar_w = max(4.0, (plot_w / num_bars) * 0.7)
            spacing = plot_w / num_bars
            for i, val in enumerate(values):
                x = pad_x + (i * spacing) + (spacing - bar_w) / 2
                bar_h = (val - min_val) / val_range * plot_h
                y = pad_y + plot_h - bar_h
                col = self.colors[i % len(self.colors)]
                bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" fill="{col}" opacity="0.9" />')
            return f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%"><g>{"".join(bars)}</g></svg>'

        elif self.chart_type == "donut":
            cx, cy = w / 2, h / 2
            r = min(plot_w, plot_h) / 2.5
            total = sum(values) or 1.0
            circumference = 2 * math.pi * r
            offset = 0.0
            arcs = []
            for i, val in enumerate(values):
                fraction = val / total
                dash = fraction * circumference
                gap = circumference - dash
                col = self.colors[i % len(self.colors)]
                arcs.append(
                    f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="{col}" '
                    f'stroke-width="24" stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-dashoffset="{-offset:.1f}" />'
                )
                offset += dash
            return f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%"><g>{"".join(arcs)}</g></svg>'

        elif self.chart_type == "sparkline":
            pts = []
            step = plot_w / max(1, len(values) - 1)
            for i, val in enumerate(values):
                x = pad_x + (i * step)
                y = pad_y + plot_h - ((val - min_val) / val_range * plot_h)
                pts.append(f"{x:.1f},{y:.1f}")
            col = self.colors[0]
            return f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%"><polyline fill="none" stroke="{col}" stroke-width="3" points="{" ".join(pts)}" /></svg>'

        else: # "line" default
            pts = []
            step = plot_w / max(1, len(values) - 1)
            for i, val in enumerate(values):
                x = pad_x + (i * step)
                y = pad_y + plot_h - ((val - min_val) / val_range * plot_h)
                pts.append(f"{x:.1f},{y:.1f}")
            col = self.colors[0]
            pts_str = " ".join(pts)
            # Area under curve
            area_str = f"{pad_x},{pad_y + plot_h} {pts_str} {pad_x + plot_w},{pad_y + plot_h}"
            return (
                f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%">'
                f'<defs><linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0%" stop-color="{col}" stop-opacity="0.3"/>'
                f'<stop offset="100%" stop-color="{col}" stop-opacity="0.0"/>'
                f'</linearGradient></defs>'
                f'<polygon points="{area_str}" fill="url(#chartGrad)"/>'
                f'<polyline fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" points="{pts_str}"/>'
                f'</svg>'
            )


class LineChart(Chart):
    def __init__(self, data: Any = None, **kwargs):
        super().__init__(chart_type="line", data=data, **kwargs)

class BarChart(Chart):
    def __init__(self, data: Any = None, **kwargs):
        super().__init__(chart_type="bar", data=data, **kwargs)

class DonutChart(Chart):
    def __init__(self, data: Any = None, **kwargs):
        super().__init__(chart_type="donut", data=data, **kwargs)

class Sparkline(Chart):
    def __init__(self, data: Any = None, **kwargs):
        super().__init__(chart_type="sparkline", data=data, height="60px", **kwargs)

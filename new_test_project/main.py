import tinpyui as tin

class App(tin.App):
    def __init__(self):
        super().__init__(title="new_test_project — Universal (Mobile + Tablet + Web WASM)", width=1280, height=820)
        self.count = tin.Signal(0)

    def build(self):
        with tin.LayoutWindow(title="new_test_project") as root:
            with tin.Column(width="full", padding=24, gap=16):
                tin.GradientText("🚀 new_test_project", gradient=["neon-cyan", "neon-purple"], size="hero")
                tin.Badge("Target: Universal (Mobile + Tablet + Web WASM)", variant="neon-cyan")
                tin.Text(text=lambda: f"Reactive Counter: {self.count.value}", color="white")
                with tin.Row(gap=12):
                    tin.Button("Increment Counter", on_click=lambda: self.count.set(self.count.value + 1))
                    tin.Button("📳 Haptic Pulse", on_click=lambda: tin.haptics.vibrate(60))
        return root

if __name__ == "__main__":
    app = App()
    app.run(prompt_target=True)

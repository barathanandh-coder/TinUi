// engine_core.cc (The Universal TinPyUI C++ Wrapper)
// Provides a unified 2-3MB cross-platform native OS window host leveraging native rendering engines:
// - macOS: Cocoa + WKWebView (Apple Metal hardware acceleration)
// - Linux: GTK3/4 + WebKitGTK (X11 / Wayland display server integration)
// - Windows: Win32 + Edge WebView2 (DirectX 12 hardware acceleration)

#include <iostream>
#include <string>

// Include lightweight open-source C++ webview abstraction header
#include "webview.h"

int main() {
    // 1. Initialize the native OS window host (enable Developer Tools)
    webview::webview w(true, nullptr);
    
    w.set_title("TinPyUI Native Application Host");
    w.set_size(1600, 900, WEBVIEW_HINT_NONE);

    // 2. Establish the Inter-Process Communication (IPC) Bridge
    // Listens for JS/Wasm messages and pipes them to Python via stdout
    w.bind("NativeIPC", [](const std::string &req) -> std::string {
        std::cout << "IPC_MSG:" << req << std::endl;
        return "{}"; 
    });

    // 3. Load the WebGL/Wasm UI Payload
    w.navigate("file:///public/index.html");

    // 4. Start the OS-specific hardware message loop
    w.run();

    return 0;
}

// engine_core.cc (The Universal TinPyUI C++ Wrapper)
// Provides a unified 2-3MB cross-platform native OS window host leveraging native rendering engines:
// - macOS: Cocoa + WKWebView (Apple Metal hardware acceleration)
// - Linux: GTK3/4 + WebKitGTK (X11 / Wayland display server integration)
// - Windows: Win32 + Edge WebView2 (DirectX 12 hardware acceleration)

#include <iostream>
#include <string>
#include <vector>
#include "shader_pipeline.hpp"

// Include lightweight open-source C++ webview abstraction header
#include "webview.h"

static GLuint g_ActiveShaderProgram = 0;

// Exported C-FFI entry points for direct ctypes integration
extern "C" {

#ifdef _WIN32
__declspec(dllexport)
#endif
GLuint TinPyUI_CompileShader(GLenum type, const char* sourceCode) {
    return tinpyui::CompileShader(type, sourceCode);
}

#ifdef _WIN32
__declspec(dllexport)
#endif
GLuint TinPyUI_LinkProgram(GLuint vertexShader, GLuint fragmentShader) {
    return tinpyui::LinkProgram(vertexShader, fragmentShader);
}

#ifdef _WIN32
__declspec(dllexport)
#endif
bool TinPyUI_ReloadShader(GLuint* progHandle, const char* vertexSrc, const char* fragmentSrc) {
    if (!progHandle) return false;
    return tinpyui::ReloadShader(*progHandle, vertexSrc, fragmentSrc);
}

#ifdef _WIN32
__declspec(dllexport)
#endif
void* TinPyUI_InitDirectGpuSurface(int width, int height, int backend) {
    return tinpyui::CreateDirectGpuSurface(width, height, backend);
}

#ifdef _WIN32
__declspec(dllexport)
#endif
bool TinPyUI_RenderGpuFrame(void* surfaceHandle) {
    return tinpyui::RenderGpuFrame(reinterpret_cast<tinpyui::GpuSurfaceDescriptor*>(surfaceHandle));
}

#ifdef _WIN32
__declspec(dllexport)
#endif
void TinPyUI_DestroyDirectGpuSurface(void* surfaceHandle) {
    tinpyui::DestroyDirectGpuSurface(reinterpret_cast<tinpyui::GpuSurfaceDescriptor*>(surfaceHandle));
}

#ifdef _WIN32
__declspec(dllexport)
#endif
int TinPyUI_GetActiveGpuBackend(void* surfaceHandle) {
    if (!surfaceHandle) return 0;
    return reinterpret_cast<tinpyui::GpuSurfaceDescriptor*>(surfaceHandle)->backend;
}

#ifdef _WIN32
__declspec(dllexport)
#endif
void BootNativeWindow(void* shared_mem_ptr) {
    std::cout << "[TinPyUI Native Engine] Booting native host with shared memory pointer: " << shared_mem_ptr << std::endl;
    webview::webview w(true, nullptr);
    w.set_title("TinPyUI Native Application Host");
    w.set_size(1600, 900, WEBVIEW_HINT_NONE);

    w.bind("NativeIPC", [](const std::string &req) -> std::string {
        if (req.rfind("RELOAD_SHADER:", 0) == 0) {
            std::string fragCode = req.substr(14);
            const char* defaultVert = 
                "attribute vec2 position;\n"
                "void main() {\n"
                "    gl_Position = vec4(position, 0.0, 1.0);\n"
                "}\n";
            bool success = tinpyui::ReloadShader(g_ActiveShaderProgram, defaultVert, fragCode.c_str());
            return success ? "{\"status\":\"ok\"}" : "{\"status\":\"error\"}";
        }
        std::cout << "IPC_MSG:" << req << std::endl;
        return "{}"; 
    });

    w.navigate("file:///public/index.html");
    w.run();
}

} // extern "C"

int main() {
    // 1. Initialize the native OS window host (enable Developer Tools)
    webview::webview w(true, nullptr);
    
    w.set_title("TinPyUI Native Application Host");
    w.set_size(1600, 900, WEBVIEW_HINT_NONE);

    // 2. Establish the Inter-Process Communication (IPC) Bridge
    // Listens for JS/Wasm messages and pipes them to Python via stdout
    w.bind("NativeIPC", [](const std::string &req) -> std::string {
        if (req.rfind("RELOAD_SHADER:", 0) == 0) {
            std::string fragCode = req.substr(14);
            const char* defaultVert = 
                "attribute vec2 position;\n"
                "void main() {\n"
                "    gl_Position = vec4(position, 0.0, 1.0);\n"
                "}\n";
            bool success = tinpyui::ReloadShader(g_ActiveShaderProgram, defaultVert, fragCode.c_str());
            return success ? "{\"status\":\"ok\"}" : "{\"status\":\"error\"}";
        }
        std::cout << "IPC_MSG:" << req << std::endl;
        return "{}"; 
    });

    // 3. Load the WebGL/Wasm UI Payload
    w.navigate("file:///public/index.html");

    // 4. Start the OS-specific hardware message loop
    w.run();

    return 0;
}

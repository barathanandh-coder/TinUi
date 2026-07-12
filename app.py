from flask import Flask, render_template_string
import json

app = Flask(__name__)

# This is the HTML file we built in Phase 3, now converted into a Jinja2 template
# Notice the {{ state_json | safe }} injection in the script block.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TinUI + Flask Integration</title>
    <style>
        body { font-family: system-ui; background: #f4f4f5; padding: 2rem; }
        .flex-center { display: flex; flex-direction: column; align-items: center; gap: 1rem; }
        button { background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
        
        /* Phase 5 Debugging Tools UI */
        .devtools { 
            position: fixed; 
            bottom: 0; left: 0; right: 0; 
            background: #1e1e1e; color: white; 
            padding: 1rem; 
            display: flex; gap: 1rem; 
            justify-content: center; 
            border-top: 3px solid #3b82f6;
        }
        .devtools button { background: #10b981; }
        .devtools button:hover { background: #059669; }
    </style>
    <!-- Assuming wasm_exec.js and tinui_engine.wasm are served statically -->
    <script src="/static/wasm_exec.js"></script>
</head>
<body>
    <div id="tinui-root"></div>
    
    <div class="devtools">
        <button onclick="window.exportState()">Save Snapshot (.bin)</button>
        <input type="file" id="state-upload" accept=".bin" style="display:none;" onchange="window.loadState(this.files[0])">
        <button onclick="document.getElementById('state-upload').click()">Restore Snapshot</button>
    </div>

    <script>
        const go = new Go(); 
        
        // Jinja2 safely injects the Python dictionary as a JS object
        const serverState = {{ state_json | safe }};
        
        async function bootTinUI() {
            try {
                const wasm = await WebAssembly.instantiateStreaming(fetch("/static/tinui_engine.wasm"), go.importObject);
                go.run(wasm.instance);
                
                // Simulated IR (In a full build, Flask would read app.ir.json from disk)
                const testIR = [
                    { op: "CREATE_NODE", id: 1, tag: "div", key: "class", value: "flex-center" },
                    { op: "SET_ATTRIBUTE", id: 1, key: "class", value: "flex-center" },
                    { op: "APPEND_CHILD", parent: 0, child: 1 },
                    
                    { op: "CREATE_NODE", id: 2, tag: "h2" },
                    { op: "SET_TEXT", id: 2, value: "Count: 0" }, // Will be overwritten by Wasm
                    { op: "APPEND_CHILD", parent: 1, child: 2 },
                    
                    { op: "CREATE_NODE", id: 3, tag: "button" },
                    { op: "SET_TEXT", id: 3, value: "Increment" },
                    { op: "ADD_EVENT", id: 3, key: "click", value: "increment_counter" },
                    { op: "APPEND_CHILD", parent: 1, child: 3 }
                ];

                // Boot Wasm and pass BOTH the IR and the Hydration State
                window.BootTinUI(JSON.stringify(testIR), JSON.stringify(serverState));
                
                // Global Event Delegation
                document.getElementById("tinui-root").addEventListener("click", (e) => {
                    const action = e.target.getAttribute("data-action");
                    if (action) {
                        window.TinUIDispatch(action);
                    }
                });
                
                // --- Phase 5 APIs ---

                // 1. Export State to a .bin file
                window.exportState = function() {
                    const uint8Array = window.TinUISnapshot();
                    const blob = new Blob([uint8Array], { type: "application/octet-stream" });
                    const url = URL.createObjectURL(blob);
                    
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "tinui_state.bin";
                    a.click();
                    URL.revokeObjectURL(url);
                    console.log("State snapshot saved.");
                };

                // 2. Load State from a .bin file
                window.loadState = async function(file) {
                    if(!file) return;
                    const arrayBuffer = await file.arrayBuffer();
                    const uint8Array = new Uint8Array(arrayBuffer);
                    window.TinUIRestore(uint8Array);
                    console.log("State restored perfectly.");
                };

            } catch (err) {
                console.error("Boot Error:", err);
            }
        }
        bootTinUI();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    # Simulate a database call to get the user's saved counter value
    db_data = {
        "initial_count": 42
    }
    
    # Serialize the Python dict to JSON so JavaScript can read it
    state_json = json.dumps(db_data)
    
    return render_template_string(HTML_TEMPLATE, state_json=state_json)

if __name__ == "__main__":
    # Run the Flask server
    app.run(port=5000, debug=True)

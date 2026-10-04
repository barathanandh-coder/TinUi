import json
import subprocess
import sys

def send_request(proc, method, params=None, msg_id=1):
    req = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": method
    }
    if params is not None:
        req["params"] = params
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    response_str = proc.stdout.readline()
    if not response_str:
        return None
    try:
        return json.loads(response_str)
    except json.JSONDecodeError:
        print(f"Failed to decode response: {response_str}")
        sys.exit(1)

def main():
    # Start Go process
    # First we need to build it since we just changed Go files
    print("Building tinui agent...")
    build_proc = subprocess.run(["go", "build", "-o", "tinui.exe", "main.go"])
    if build_proc.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    print("Starting agent...")
    proc = subprocess.Popen(
        [".\\tinui.exe", "agent"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    uri = "file:///project/test.tin"

    # Step 1: Update document to version 2 (edit document)
    res = send_request(proc, "update_document", {
        "uri": uri,
        "source": "component Main():\n    Text(text=\"Hello\")",
        "version": 2
    }, msg_id=1)
    print("Update Version 2 Response:", res)
    assert res.get("result", {}).get("version") == 2

    # Step 2: Query for version 1 (stale version request)
    res = send_request(proc, "query", {
        "kind": "hover",
        "document": uri,
        "position": {"line": 1, "character": 4},
        "version": 1
    }, msg_id=2)
    print("Stale Query Version 1 Response:", res)
    assert "error" in res, "Expected an error for stale version"
    assert res["error"]["code"] == -32002, f"Expected code -32002, got {res['error']['code']}"

    # Step 3: Query for version 2 (current version request)
    res = send_request(proc, "query", {
        "kind": "hover",
        "document": uri,
        "position": {"line": 1, "character": 4},
        "version": 2
    }, msg_id=3)
    print("Valid Query Version 2 Response:", res)
    assert "result" in res, "Expected a result for valid version"
    assert res["result"]["version"] == 2

    # Shutdown
    send_request(proc, "shutdown", msg_id=4)
    proc.wait()
    print("Test passed successfully!")

if __name__ == "__main__":
    main()

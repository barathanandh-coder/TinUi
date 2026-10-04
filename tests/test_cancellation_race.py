import json
import subprocess
import sys
import threading
import time

def send_request(proc, method, params=None, msg_id=None):
    req = {
        "jsonrpc": "2.0",
        "method": method
    }
    if msg_id is not None:
        req["id"] = msg_id
    if params is not None:
        req["params"] = params
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()

def read_responses(proc, responses_dict, lock):
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            resp = json.loads(line)
            if "id" in resp:
                with lock:
                    responses_dict[resp["id"]] = resp
        except json.JSONDecodeError:
            pass

def main():
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
    
    responses = {}
    lock = threading.Lock()
    
    reader_thread = threading.Thread(target=read_responses, args=(proc, responses, lock))
    reader_thread.daemon = True
    reader_thread.start()

    uri = "file:///project/test.tin"
    
    # Send update version 1
    send_request(proc, "update_document", {
        "uri": uri,
        "source": "component Main():\n    Text(text=\"Hello\")",
        "version": 1
    }, msg_id=1)
    
    time.sleep(0.1) # Wait for update to be acknowledged

    # Check A
    send_request(proc, "check", {
        "uri": uri,
        "version": 1
    }, msg_id=10)
    
    # Query B
    send_request(proc, "query", {
        "kind": "hover",
        "document": uri,
        "position": {"line": 1, "character": 4},
        "version": 1
    }, msg_id=11)
    
    # Cancel B
    send_request(proc, "$/cancelRequest", {
        "id": 11
    }, msg_id=None)
    
    # Query C
    send_request(proc, "query", {
        "kind": "definition",
        "document": uri,
        "position": {"line": 1, "character": 4},
        "version": 1
    }, msg_id=12)
    
    # Update v2
    send_request(proc, "update_document", {
        "uri": uri,
        "source": "component Main():\n    Text(text=\"World\")",
        "version": 2
    }, msg_id=2)

    time.sleep(0.5) # Wait for responses

    with lock:
        res_b = responses.get(11, {})
        res_a = responses.get(10, {})
        res_c = responses.get(12, {})
        res_v2 = responses.get(2, {})

    print("Result B:", res_b)
    print("Result A:", res_a)
    print("Result C:", res_c)
    print("Result V2:", res_v2)
    
    assert "error" in res_b and res_b["error"]["code"] == -32800, "B should be cancelled"
    
    # A and C might complete, or they might hit Stale Document Version if the v2 update beats them to the VFS.
    # Both are acceptable and race-safe behaviors.
    is_a_ok = "result" in res_a or ("error" in res_a and res_a["error"]["code"] == -32002)
    is_c_ok = "result" in res_c or ("error" in res_c and res_c["error"]["code"] == -32002)
    
    assert is_a_ok, f"A behaved incorrectly: {res_a}"
    assert is_c_ok, f"C behaved incorrectly: {res_c}"
    
    assert res_v2.get("result", {}).get("version") == 2, "V2 should update properly"

    send_request(proc, "shutdown", msg_id=99)
    proc.wait()
    
    print("Race/Cancellation tests passed successfully.")

if __name__ == "__main__":
    main()

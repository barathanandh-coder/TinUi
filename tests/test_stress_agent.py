import json
import subprocess
import threading
import time
import random
import sys

def send_req(proc, method, params, req_id):
    req = {"jsonrpc": "2.0", "method": method, "params": params, "id": req_id}
    try:
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
    except Exception:
        pass

def send_notif(proc, method, params):
    req = {"jsonrpc": "2.0", "method": method, "params": params}
    try:
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
    except Exception:
        pass

def reader_thread(proc, results, lock, stats):
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            resp = json.loads(line)
            if "id" in resp:
                with lock:
                    if resp["id"] is not None:
                        if resp["id"] in results:
                            stats["duplicate_responses"] += 1
                            print(f"Duplicate response for ID {resp['id']}:")
                            print(f"  First: {results[resp['id']]}")
                            print(f"  Second: {resp}")
                        results[resp["id"]] = resp
                    stats["responses_received"] += 1
        except json.JSONDecodeError:
            with lock:
                stats["protocol_errors"] += 1

def main():
    print("Building agent with race detector...")
    subprocess.run(["go", "build", "-race", "-o", "tinui_race.exe", "main.go"], check=True)

    print("Starting stress test...")
    proc = subprocess.Popen(["./tinui_race.exe", "agent"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    
    results = {}
    lock = threading.Lock()
    stats = {
        "requests_sent": 0,
        "responses_received": 0,
        "cancelled_requests": 0,
        "duplicate_responses": 0,
        "protocol_errors": 0,
    }

    t = threading.Thread(target=reader_thread, args=(proc, results, lock, stats))
    t.daemon = True
    t.start()

    uri = "file:///project/stress.tin"
    
    # 1. Concurrent requests & VFS contention
    for i in range(1, 100):
        # Update version
        send_req(proc, "update_document", {"uri": uri, "source": f"component Main():\n    Text(text=\"{i}\")", "version": i}, f"u{i}")
        with lock:
            stats["requests_sent"] += 1
            
        # Fire concurrent requests
        for j in range(5):
            req_id = f"q_{i}_{j}"
            send_req(proc, "query", {"kind": "hover", "document": uri, "position": {"line": 1, "character": 4}, "version": i}, req_id)
            with lock:
                stats["requests_sent"] += 1
            
            # 2. Cancellation storm
            if random.random() < 0.3:
                send_notif(proc, "$/cancelRequest", {"id": req_id})
                with lock:
                    stats["cancelled_requests"] += 1
                    
        # 7. Malformed traffic
        if i % 10 == 0:
            proc.stdin.write("INVALID JSON\n")
            proc.stdin.flush()
            send_req(proc, "unknown_method", {}, f"unk{i}")
            with lock:
                stats["requests_sent"] += 1

    time.sleep(2)
    
    # Shutdown
    send_req(proc, "shutdown", {}, "shutdown")
    proc.wait()

    with lock:
        print("\n--- Stress Test Results ---")
        print(f"Requests Sent: {stats['requests_sent']}")
        print(f"Responses Received: {stats['responses_received']}")
        print(f"Cancelled Requests: {stats['cancelled_requests']}")
        print(f"Duplicate Responses: {stats['duplicate_responses']}")
        print(f"Protocol Errors (JSON Decode): {stats['protocol_errors']}")
        
        # Verify invariants
        assert stats['duplicate_responses'] == 0, "Invariant violation: Duplicate responses"
        assert stats['protocol_errors'] == 0, "Invariant violation: Protocol errors (stdout corrupted)"
        
        # Check cancellation semantics
        cancellations_honored = 0
        stale_versions = 0
        successes = 0
        for r_id, resp in results.items():
            if "error" in resp:
                if resp["error"]["code"] == -32800:
                    cancellations_honored += 1
                elif resp["error"]["code"] == -32002:
                    stale_versions += 1
            else:
                successes += 1
                
        print(f"Cancellations Honored (-32800): {cancellations_honored}")
        print(f"Stale Version Drops (-32002): {stale_versions}")
        print(f"Successful Responses: {successes}")

if __name__ == "__main__":
    main()

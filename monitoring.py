import os
import uuid
import time
from collections import defaultdict

import requests
from flask import Flask, request, Response, jsonify

from trainingmodel import TransitionModel
#configure URL
backend = os.environ.get("backend", "http://127.0.0.1:5001")

#training mode or detection mode
MODE = os.environ.get("MODE", "training")

modelPath = os.environ.get("modelPath", "model.json")

#detection parameters
#threshold = 0.05   #threshold for makring smtg as suspicious
threshold = float(os.environ.get("THRESHOLD", "0.05"))
maxLoginFails = 5       #max login failures allowed         
maxDownloads = 20     #max downloads allowed           

app = Flask(__name__)

#in detection mode
if MODE == "detection" and os.path.exists(modelPath):
    model = TransitionModel.load(modelPath)
else:
    model = TransitionModel()

#track session data - added request count and first flag timestamp
sessions = defaultdict(lambda: {
    "currentState": "START",
    "loginFailures": 0,
    "downloads": 0,
    "suspiciousEvents": [],
    "requestCount": 0,
    "firstFlagTs": None,
})

#get session id from headers or create new one
def get_session_id():
    sid = request.headers.get("X-Session-ID")
    if not sid:
        sid = "browser-" + str(uuid.uuid4())
    return sid

#map request to state
def map_state(path: str, method: str, backend_status: int) -> str:
    if path == "/login":
        if backend_status == 200:
            return "LOGIN_SUCCESS"
        else:
            return "LOGIN_FAILURE"
    elif path == "/download-data":
        return "DOWNLOAD_DATA"
    elif path == "/admin":
        return "ADMIN_ACCESS"
    else:
        return f"{method.upper()} {path}"

#forward request to backend and get response
def forward_request_to_backend():
    method = request.method
    url = backend + request.full_path 
    if url.endswith("?"):
        url = url[:-1]

    headers = dict(request.headers)
    headers.pop("Host", None)

    data = request.get_data()
    cookies = request.cookies

    resp = requests.request(
        method=method,
        url=url,
        headers=headers,
        data=data,
        cookies=cookies,
        timeout=5,
    )
    return resp

#log suspicious event - updated so that first flag timestamp is recorded
def log_suspicious(session_id, reason, prev_state, next_state):
    event = {
        "session": session_id,
        "reason": reason,
        "from": prev_state,
        "to": next_state,
        "timestamp": time.time(),
    }
    sessions[session_id]["suspiciousEvents"].append(event)

    if sessions[session_id]["firstFlagTs"] is None:
        sessions[session_id]["firstFlagTs"] = event["timestamp"]

    print("[SUSPICIOUS]", event)


#stats endpoint
@app.route("/_stats", methods=["GET"])
def stats():
    return jsonify({
        "mode": MODE,
        "num_sessions": len(sessions),
    })

#save the model
@app.route("/_save_model", methods=["POST"])
def save_model():
    """
    Call this after training to persist the learned transitions.
    """
    if MODE != "training":
        return jsonify({"error": "Can only save in training mode"}), 400
    model.save(modelPath)
    return jsonify({"ok": True, "path": modelPath})

#export session data
@app.route("/_export", methods=["GET"])
def export():
    out = {}
    for sid, s in sessions.items():
        out[sid] = {
            "requestCount": s["requestCount"],
            "numFlags": len(s["suspiciousEvents"]),
            "firstFlagTs": s["firstFlagTs"],
            "reasons": [e["reason"] for e in s["suspiciousEvents"]],
        }
    return jsonify(out)


#main proxy endpoint
@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(path):
    session_id = get_session_id()
    sess = sessions[session_id]
    prev_state = sess["currentState"]

    start_time = time.time()
    backend_resp = forward_request_to_backend()
    latency = time.time() - start_time

    next_state = map_state("/" + path, request.method, backend_resp.status_code)
    sess["requestCount"] += 1 #increment count


    if MODE == "training":
        model.observe(prev_state, next_state)

    else:

        if model.is_suspicious(prev_state, next_state, threshold):
            log_suspicious(session_id, "rare_transition", prev_state, next_state)

        if next_state == "LOGIN_FAILURE":
            sess["loginFailures"] += 1
            if sess["loginFailures"] > maxLoginFails:
                log_suspicious(
                    session_id,
                    "excessive_login_failures",
                    prev_state,
                    next_state,
                )

        if next_state == "DOWNLOAD_DATA":
            sess["downloads"] += 1
            if sess["downloads"] > maxDownloads:
                log_suspicious(
                    session_id,
                    "excessive_downloads",
                    prev_state,
                    next_state,
                )

        if next_state == "ADMIN_ACCESS":
            log_suspicious(
                session_id,
                "admin_endpoint_access",
                prev_state,
                next_state,
            )

        print(f"[METRIC] latency={latency:.4f}s sid={session_id}")

    sess["currentState"] = next_state

    response = Response(
        response=backend_resp.content,
        status=backend_resp.status_code,
        headers=dict(backend_resp.headers),
    )
    response.headers.pop("Transfer-Encoding", None)
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print(f"Starting monitor in {MODE!r} mode on port {port}, backend={backend}")
    app.run(host="0.0.0.0", port=port, debug=True)

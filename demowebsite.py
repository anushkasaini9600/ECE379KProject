from flask import Flask, request, jsonify

#using a flask website for the demo website
app = Flask(__name__)

#usernames and passwords
USERS = {
    "anushka": "12345",
    "bob": "98765",
}

#data for each user
PROFILE_DATA = {
    "anushka": {"name": "Anushka", "email": "anushkarsaini@gmail.com"},
    "bob": {"name": "Bob", "email": "bob123@gmail.com"},
}

#data dumps for download
USER_DATA_DUMP = {
    "anushka": {"posts": [1, 2, 3], "comments": [10, 11]},
    "bob": {"posts": [4, 5], "comments": [12]},
}

#admin secret data
ADMIN_SECRET = {"flag": "privateadmin"}

# Endpoint definitions
@app.route("/login", methods=["POST"])
def login():
    body = request.get_json() or {}
    username = body.get("username")
    password = body.get("password")

    if username in USERS and USERS[username] == password:
        return jsonify({"success": True, "user": username}), 200
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

#read the profile
@app.route("/profile", methods=["GET"])
def get_profile():
    username = request.args.get("user")
    if username not in PROFILE_DATA:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"profile": PROFILE_DATA[username]}), 200

#update the profile
@app.route("/profile", methods=["POST"])
def update_profile():
    body = request.get_json() or {}
    username = body.get("user")
    new_email = body.get("email")

    if username not in PROFILE_DATA:
        return jsonify({"error": "User not found"}), 404

    if new_email:
        PROFILE_DATA[username]["email"] = new_email

    return jsonify({"success": True, "profile": PROFILE_DATA[username]}), 200

#delete the profile
@app.route("/profile", methods=["DELETE"])
def delete_profile():
    username = request.args.get("user")
    if username not in PROFILE_DATA:
        return jsonify({"error": "User not found"}), 404

    PROFILE_DATA.pop(username, None)
    USER_DATA_DUMP.pop(username, None)
    return jsonify({"success": True}), 200

#download user data
@app.route("/download-data", methods=["GET"])
def download_data():
    username = request.args.get("user")
    if username not in USER_DATA_DUMP:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"data": USER_DATA_DUMP[username]}), 200

#get the admin endpoint
@app.route("/admin", methods=["GET"])
def admin_only():
    return jsonify({"admin": ADMIN_SECRET}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

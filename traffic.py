import os
import uuid
import time
import random
import sys

import requests
# Configure monitoring service URL
MONITOR_BASE = os.environ.get("MONITOR_BASE", "http://127.0.0.1:5002")
BACKEND_BASE = os.environ.get("BACKEND_BASE", "http://127.0.0.1:5003")

#start a new session
def new_session():
    return str(uuid.uuid4())

#make a POST request
def post(path, session_id, json=None):
    return requests.post(
        MONITOR_BASE + path,
        json=json or {},
        headers={"X-Session-ID": session_id},
        timeout=5,
    )

#make a GET request
def get(path, session_id, params=None):
    return requests.get(
        MONITOR_BASE + path,
        params=params or {},
        headers={"X-Session-ID": session_id},
        timeout=5,
    )

#normal session
def normal_user_session(username="anushka", correct_password="12345"):
    sid = new_session()

    
    post("/login", sid, {"username": username, "password": correct_password})


    actions = 0
    max_actions = random.randint(2, 5) 

    while actions < max_actions:

        get("/profile", sid, {"user": username})


        if random.random() < 0.4:
            post(
                "/profile",
                sid,
                {"user": username, "email": f"{username}+new{actions}@gmail.com"},
            )


        if random.random() < 0.3:
            get("/download-data", sid, {"user": username})

        actions += 1
        time.sleep(0.01)

    return sid
#benign session to recreate regular user behavior BUT has some irregularities like one failed login but then correct login
def benign_user_session(username="anushka", correct_password="12345"):
    sid = new_session()
    #failed
    if random.random() < 0.25:
        post("/login", sid, {"username": username, "password": "wrong_pw"})
        time.sleep(0.01)
    #correct
    post("/login", sid, {"username": username, "password": correct_password})

    max_actions = random.randint(8, 25)
    actions = 0

    while actions < max_actions:
        get("/profile", sid, {"user": username})

        if random.random() < 0.35:
            get("/profile", sid, {"user": username})

        if random.random() < 0.25:
            post("/profile", sid, {"user": username, "email": f"{username}+b{actions}@gmail.com"})

        if random.random() < 0.20:
            get("/download-data", sid, {"user": username})

        actions += 1
        time.sleep(0.01)

    return sid


#attack
def brute_force_attack_session(target_user="anushka"):

    sid = new_session()
    attempts = 0
    max_attempts = 50

    while attempts < max_attempts:
        post(
            "/login",
            sid,
            {
                "username": target_user,
                "password": f"wrong_password_{attempts}",
            },
        )
        attempts += 1
        time.sleep(0.005)

    return sid

#scraping attack
def scraping_attack_session(target_user="anushka"):
    sid = new_session()

    post("/login", sid, {"username": target_user, "password": "12345"})

    downloads = 0
    max_downloads = 100 

    while downloads < max_downloads:
        get("/download-data", sid, {"user": target_user})
        downloads += 1
        time.sleep(0.005)

    return sid

#admin attack
def direct_admin_attack_session():

    sid = new_session()
    hits = 0
    max_hits = 20

    while hits < max_hits:
        get("/admin", sid)
        hits += 1
        time.sleep(0.01)

    return sid


def run_training(kind="regular"):
    print(f"Generating {kind} training traffic...")

    sessions_generated = 0
    max_sessions = 150  #150 sessions vs before it was just 100

    while sessions_generated < max_sessions:
        if kind == "regular":
            normal_user_session()
        elif kind == "benign":
            benign_user_session()
        else:
            raise ValueError("kind must be 'regular' or 'benign'")

        sessions_generated += 1
        time.sleep(0.02)

    print(f"Finished {kind} training traffic: {sessions_generated} sessions.")


def run_detection():
    print("Generating mixed detection traffic (normal + attacks)...")

    rounds = 0
    max_rounds = 10

    while rounds < max_rounds:
        for _ in range(5):
            normal_user_session()

        brute_force_attack_session()

        scraping_attack_session()

        direct_admin_attack_session()

        rounds += 1
        print(f"Completed detection round {rounds}/{max_rounds}")

    print("Finished detection traffic generation.")


if __name__ == "__main__":
    mode = "train_regular"
    if len(sys.argv) >= 2:
        mode = sys.argv[1].lower()

    if mode == "train_regular":
        run_training("regular")
    elif mode == "train_benign":
        run_training("benign")
    elif mode == "detect":
        run_detection()
    else:
        print("Usage: python traffic.py [train_regular|train_benign|detect]")

brute_force = 0
scraping = 0
admin = 0

with open("output.log", "r") as f:
    for line in f:
        if "[SUSPICIOUS]" not in line:
            continue
        if "excessive_login_failures" in line:
            brute_force += 1
        elif "excessive_downloads" in line:
            scraping += 1
        elif "admin_endpoint_access" in line:
            admin += 1

print("Brute force alerts:", brute_force)
print("Scraping alerts:", scraping)
print("Admin alerts:", admin)

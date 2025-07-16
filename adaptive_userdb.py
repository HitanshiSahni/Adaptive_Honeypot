import random
import os

userdb_path = "/home/hitanshi/cowrie/etc/userdb.txt"
backup_path = userdb_path + ".bak"

# Create a backup
with open(userdb_path, "r") as file:
    original = file.read()
with open(backup_path, "w") as file:
    file.write(original)

# List of fake but realistic username:password pairs
credentials = [
    ("admin", "admin123"),
    ("root", "toor"),
    ("guest", "guest"),
    ("user", "pass123"),
    ("test", "test@123"),
    ("dev", "devpass"),
    ("support", "helpdesk123"),
]

username, password = random.choice(credentials)
new_entry = f"{username}:{password}\n"

# Write the new entry
with open(userdb_path, "w") as file:
    file.write(new_entry)

print(f"[✓] Updated userdb with: {username}:{password}")
print(f"Backup created at: {backup_path}")

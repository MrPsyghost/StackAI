import json, os, random as r

def lower_all(l):
    return [x.lower() for x in l]

def create_db(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        with open(file_path, 'w') as f:
            data = {}
            json.dump(data, f, indent=4)
    return data

def delete_db(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def create_user(users, username, email, password):
    if username.lower() not in lower_all(list(users.keys())):
        users[username] = {"credentials":{"email":email, "password":password}, "posts":{}, "comments":{}}
        return True
    return False

def add_report(users, username, ai_name, subject, desc):
    if username.lower() in lower_all(list(users.keys())):
        report = {
            "ai": ai_name,
            "desc": desc,
            "comments": [],
        }
        if subject.lower() not in lower_all(list(users[username]["posts"].keys())):
            users[username]["posts"][subject] = report
            return True
        return False

def add_comment(users, user, subject, user2, text):
    if user.lower() in lower_all(list(users.keys())):
        users[user]["posts"][subject]["comments"].append(
            {
                "user": user2,
                "text": text,
            }
        )
        return True
    return False

def save_db(file_path, data):
    if os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

def read_db(users):
    reports = []
    for user in users:
        for report in users[user]["posts"]:
            reports.append([user, report, users[user]["posts"][report]['ai'], users[user]["posts"][report]['desc']])
    return reports
import os
import json
import requests
import time
import base64

# 🔹 قراءة Access Tokens من GitHub Secrets
tokens_json = os.getenv("TOKENS_JSON")
if not tokens_json:
    raise ValueError("⚠️ متغير البيئة 'TOKENS_JSON' غير متوفر في Secrets!")

tokens_data = json.loads(tokens_json)
tokens = tokens_data.get("accounts", [])

if not tokens:
    raise ValueError("⚠️ لم يتم العثور على أي حسابات في 'TOKENS_JSON'!")

# 🔹 إعدادات المستودعات
base_dir = "github_articles"
repo_name = "giftcard-articles"  # كل حساب لديه مستودع واحد بهذا الاسم

# 🔹 رفع المقالات لكل حساب
for account_num, account_data in enumerate(tokens, start=1):
    username = account_data["username"]
    token = account_data["token"]

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 🔹 تحديد مجلد المقالات لهذا الحساب
    articles_folder = os.path.join(base_dir, f"account_{account_num}")

    if not os.path.exists(articles_folder):
        print(f"⚠️ المجلد {articles_folder} غير موجود للحساب {username}، تخطي...")
        continue

    article_files = os.listdir(articles_folder)

    for article in article_files:
        file_path = os.path.join(articles_folder, article)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 🔹 تحويل المحتوى إلى Base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        # 🔹 رفع المقالة إلى المستودع
        github_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{article}"
        data = {
            "message": f"Added {article}",
            "content": encoded_content,
            "branch": "main"
        }
        response = requests.put(github_url, headers=headers, json=data)

        if response.status_code == 201:
            print(f"✅ {article} تم رفعه بنجاح إلى {repo_name} ({username})")
        elif response.status_code == 422:
            print(f"⚠️ {article} موجود بالفعل في {repo_name} ({username})")
        else:
            print(f"❌ فشل رفع {article} إلى {repo_name} ({username}): {response.json()}")

        # ⏳ تأخير لمنع الحظر (15 ثانية)
        time.sleep(15)

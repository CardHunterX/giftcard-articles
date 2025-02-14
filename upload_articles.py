import os
import json

# قراءة `TOKENS_JSON` من متغيرات البيئة
tokens_json_str = os.getenv("TOKENS_JSON")

# التحقق من وجود `TOKENS_JSON`
if not tokens_json_str:
    raise ValueError("⚠️ لم يتم العثور على أي حسابات في 'TOKENS_JSON'!")

# تحميل البيانات من JSON
tokens_data = json.loads(tokens_json_str)

# التحقق من وجود الحسابات
if "accounts" not in tokens_data or not tokens_data["accounts"]:
    raise ValueError("⚠️ لا يوجد أي حسابات في 'TOKENS_JSON'!")

# استخدام الحسابات
for account in tokens_data["accounts"]:
    username = account.get("username")
    token = account.get("github_token")

    if not username or not token:
        raise ValueError(f"⚠️ بيانات غير مكتملة للحساب: {account}")

    print(f"✅ تم العثور على الحساب: {username}")

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

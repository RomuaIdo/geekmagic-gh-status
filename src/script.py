import requests
import json
import os
from collections import Counter
from PIL import Image
import io


TOKEN = os.getenv("GH_TOKEN")
USER = "RomuaIdo"

if not TOKEN:
    print("ERRO: Token não encontrado!")
    exit(1)

headers = {"Authorization": f"Bearer {TOKEN}"}
print(f"Fetching data of {USER}...")

url_user = f"https://api.github.com/users/{USER}"
user_data = requests.get(url_user, headers=headers).json()
followers = user_data.get("followers", 0)

url_repos = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed"
repos_data = requests.get(url_repos, headers=headers)

if repos_data.status_code != 200:
    print(f"ERRO na API: {repos_data.text}")
    exit(1)

repos = repos_data.json()

stars_num = sum(repo.get('stargazers_count', 0) for repo in repos if isinstance(repo, dict))
projects_num = len([repo for repo in repos if isinstance(repo, dict)])

forks_num = sum(repo.get('forks_count', 0) for repo in repos if isinstance(repo, dict))
issues_num = sum(repo.get('open_issues_count', 0) for repo in repos if isinstance(repo, dict))
size_kb = sum(repo.get('size', 0) for repo in repos if isinstance(repo, dict))
size_mb = round(size_kb / 1024, 2)

last_project = repos[0].get('name', 'None') if repos else 'None'


main_project = "None"
more_stars = -1
languages = {}

for repo in repos:
    if isinstance(repo, dict):
        stars = repo.get('stargazers_count', 0)
        if stars > more_stars:
            more_stars = stars
            main_project = repo.get('name', 'None')

        languages_url = repo.get('languages_url')    
        if languages_url:
            langs_response = requests.get(languages_url, headers=headers)
            
            if langs_response.status_code == 200:
                repo_langs = langs_response.json()
                
                for lang, bytes_count in repo_langs.items():
                    languages[lang] = languages.get(lang, 0) + bytes_count


top3_lang = Counter(languages).most_common(3)
top3_lang_str = [lang for lang, count in top3_lang]
while len(top3_lang_str) < 3:
    top3_lang_str.append("None")

top3_lang_json = {
    "top1": top3_lang_str[0],
    "top2": top3_lang_str[1],
    "top3": top3_lang_str[2]
}

gh_data = {
    "user": USER,
    "followers": followers,
    "stars_num": stars_num,
    "projects_num": projects_num,
    "forks_num": forks_num,
    "issues_open": issues_num,
    "size_mb": size_mb,
    "main_languages": top3_lang_json,
    "main_project": main_project,
    "last_project": last_project
}


avatar_url = user_data.get("avatar_url")

if avatar_url:
    print("Downloading avatar...")
    avatar_response = requests.get(avatar_url)
    avatar = Image.open(io.BytesIO(avatar_response.content))

    avatar = avatar.resize((64, 64))
    avatar = avatar.convert("RGB")

    with open("../avatar.bin", "wb") as f:
        for y in range(avatar.height):
            for x in range(avatar.width):
                r, g, b = avatar.getpixel((x, y))
                
                rgb365 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                f.write(rgb365.to_bytes(2, byteorder='big'))
                
    print("Avatar downloaded and converted successfully!")


with open("../status.json", "w", encoding="utf-8") as file:
    json.dump(gh_data, file, ensure_ascii=False, indent=2)

print("status.json generated successfully!")

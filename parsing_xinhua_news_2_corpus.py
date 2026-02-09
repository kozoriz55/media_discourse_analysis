import requests
import json
from bs4 import BeautifulSoup
import time
import csv
import re
import os

HEADERS = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
	"Accept": "application/json, text/javascript, */*; q=0.01",
	"Referer": "https://www.news.cn/",
	"X-Requested-With": "XMLHttpRequest",
	"Cookie": "wdcid=041658; xinhuatoken=news; wdlast=17677" #додати свіжі кукіс
}

def fetch_news_page(keyword, page=1):
	url = "https://so.news.cn/getNews"
	params = {
		"lang": "cn",
		"curPage": page,
		"searchFields": 1,#Пошук у заголовках + повному тексті новини - 1
		"sortField": 0,
		"keyword": keyword
	}
	response = requests.get(url, headers=HEADERS, params=params)
	print(f"📡 Сторінка {page} — Статус: {response.status_code}")
	
	if response.status_code == 200:
		try:
			return response.json()
		except Exception:
			print("❌ JSON не розпарсився. Частина відповіді:\n", response.text[:300])
			return None
	return None

def extract_article_text(url):
	try:
		r = requests.get(url, headers=HEADERS, timeout=10)
		r.encoding = 'utf-8'
		soup = BeautifulSoup(r.text, 'lxml')

		candidates = [
			("div", {"id": "detail"}),
			("div", {"class": "article"}),
			("div", {"id": "p-detail"}),
			("div", {"class": "mainCon", "id": "content"}),
			("div", {"class": "main"}),
			("div", {"id": "content"}),
			("div", {"class": "content"}),
			("div", {"class": "zw"}),
			("div", {"class": "con_txt"}),
		]

		for tag, attrs in candidates:
			container = soup.find(tag, attrs=attrs)
			if container:
				paragraphs = container.find_all("p")
				if paragraphs:
					return "".join(p.get_text(strip=True) for p in paragraphs)

		return soup.get_text(" ", strip=True)[:2000]  # запасний варіант
	except Exception as e:
		print(f"❌ Не витягнув текст: {url} — {e}")
		return "не отримано"

def main():
	keyword = "王毅"   # пошукове слово
	filename = f"C:\\Users\\...\\Desktop\\{keyword}_news_xinhua.csv"

	first_page = fetch_news_page(keyword, 1)
	if not first_page:
		print("❌ Не вдалося отримати першу сторінку.")
		return

	total_pages = first_page.get("content", {}).get("pageCount", 1)
	print(total_pages)
	seen_titles = set()

	write_header = not os.path.exists(filename)

	with open(filename, "a", encoding="utf-8-sig", newline="") as f:
		writer = csv.writer(f, delimiter="\t")
		if write_header:
			writer.writerow(["Заголовок", "URL", "Текст"])

		for page in range(1, total_pages + 1):
			data = fetch_news_page(keyword, page)
			if page%80==0: print("спимо 5 хвилин"), time.sleep(300)
			time.sleep(1)# щоб не банили
			results = data.get("content", {}).get("results") if data else None
			if not results:
				print(f"⚠️ Пропущено сторінку {page}: немає новин")
				continue

			for item in results:
				try:
					title = re.sub('<[^>]+>|&nbsp;|&quot;', '', item.get("title", "")).strip()
					url = item.get("url")
					if title and url and title not in seen_titles:
						text = extract_article_text(url)
						writer.writerow([title, url, text])
						seen_titles.add(title)
						print(f"✅ {title}, довжина: {len(text)}")
				except Exception as e:
					print(f"⚠️ Помилка новини: {e}")
					continue

	print(f"✅ Завершено. Дані збережено у '{filename}'")

if __name__ == "__main__":
	main()


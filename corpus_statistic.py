import re
import jieba
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
CHINESE_RE = re.compile(r"^[\u4e00-\u9fff]+$")
# ===== Зчитування корпусу =====
with open("C:\\Users\\davin\\Desktop\\wangyi_corpus.txt", "r", encoding="utf-8") as f:
    text = f.read()
# ===== 1. Речення =====
sentences = [s.strip() for s in re.split(r"[。！？]", text) if s.strip()]
# ===== 2. Токенізація за результатами сегментації jieba =====
tokens = [t for t in jieba.cut(text) if CHINESE_RE.match(t)]
# ===== 3. Базова статистика =====
num_tokens = len(tokens)
num_sentences = len(sentences)
types = set(tokens)
ttr = len(types) / num_tokens if num_tokens else 0
asl = num_tokens / num_sentences if num_sentences else 0
print("СТАТИСТИКА КОРПУСУ (КИТАЙСЬКА МОВА)")
print("---------------------------------")
print(f"Кількість символів (characters): {len(text)}")
print(f"Кількість токенів / слів (tokens): {num_tokens}")
print(f"Кількість речень (sentences): {num_sentences}")
print(f"Кількість унікальних слів (types): {len(types)}")
print(f"Type/Token Ratio (TTR): {ttr:.4f}")
print(f"Середня довжина речення (ASL): {asl:.2f}")
# ===== 4. Розподіл довжин речень =====
sentence_lengths = [len([t for t in jieba.cut(s) if CHINESE_RE.match(t)]) for s in sentences]
plt.hist(sentence_lengths, bins=50)
plt.title("Sentence length distribution")
plt.xlabel("Sentence length (in tokens)")
plt.ylabel("Number of sentences")
plt.show()
# ===== 5. Частотний словник =====
freq = Counter(tokens)
items_list = sorted(freq.items(), key=lambda x: x[1], reverse=True)#[:30] зазвичай для наочності обмежують кількість слів
# ===== 6. Логарифмічний Zipf-графік частотного розподілу =====
frequencies = [f for _, f in items_list]# розділяємо слова і частоти у два списка
words = [w for w, _ in items_list]
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.figure(figsize=(14, 6))
plt.plot(range(len(words)), frequencies)
plt.yscale('log')#Логарифмічний графік 
plt.title("Frequency distribution of vocabulary (log scale)")
plt.xlabel("Words")
plt.ylabel("Frequencies")
STEP = 200   # можна змінити
plt.xticks(range(0, len(words), STEP), words[::STEP], rotation=50)
plt.tight_layout()
plt.show()
# ===== 7. Аналіз частотних зон =====
initial = sum(1 for f in freq.values() if f >= 11)
middle = sum(1 for f in freq.values() if 2 <= f <= 10)
tail = sum(1 for f in freq.values() if f == 1)
print("\nАНАЛІЗ ЧАСТОТНИХ ЗОН")
print("------------------")
print(f"Початкова зона (≥11): {initial}")
print(f"Середня зона (10–2): {middle}")
print(f"Hapax legomena (1): {tail}")
# ===== 8. Розподіл слів за довжиною =====
length_freq = Counter(len(w) for w in tokens)# довжина слова = кількість ієрогліфів
print("\nРОЗПОДІЛ СЛІВ ЗА ДОВЖИНОЮ")
print("-----------------------")
for length in sorted(length_freq):
    print(f"Довжина {length}: {length_freq[length]} слів")
plt.bar(length_freq.keys(), length_freq.values())
plt.title("Word length distribution")
plt.xlabel("Word length (characters)")
plt.ylabel("Number of words")
plt.show()
# ===== Збереження словника в Excel і CSV =====
df = pd.DataFrame(items_list, columns=["term", "frequency"])
df.to_excel("C:\\Users\\davin\\Desktop\\frequency_dictionary.xlsx", index=False)
#df.to_csv("C:\\Users\\davin\\Desktop\\frequency_dictionary.csv", index=False, encoding="utf-8-sig")
print("\nФайл частотного словника збережено в Excel!")

# ===== 9. POS-токенізація =====
import jieba.posseg as pseg
from collections import defaultdict
pos_tokens = [(w, flag) for w, flag in pseg.cut(text) if CHINESE_RE.match(w)]
words = [w for w, _ in pos_tokens]
pos_tags = [flag for _, flag in pos_tokens]

OUTPUT_PATH = "C:\\Users\\davin\\Desktop\\wangyi_corpus_analysis.xlsx"
with pd.ExcelWriter(OUTPUT_PATH, engine="xlsxwriter") as writer:
	# ===== 10. Corpus-level statistics =====
	corpus_stats = pd.DataFrame([["Characters", len(text)],["Tokens", num_tokens],["Sentences", num_sentences],["Types", len(types)],["TTR", round(ttr, 4)],["ASL", round(asl, 2)]],columns=["metric", "value"])
	corpus_stats.to_excel(writer, sheet_name="Corpus_Stats", index=False)
	# ===== 11. POS Distribution =====
	pos_distribution = Counter(tag[0] for tag in pos_tags)
	pd.DataFrame(pos_distribution.items(),columns=["POS", "frequency"]).sort_values("frequency", ascending=False)\
	 .to_excel(writer, sheet_name="POS_Distribution", index=False)
	# ===== 12. Lexical Density =====
	LEXICAL_POS = {"n", "v", "a"}  # noun, verb, adjective
	lexical_items = [w for w, p in pos_tokens if p[0] in LEXICAL_POS]
	pos_toke = [p[0] for w, p in pos_tokens if p[0] in LEXICAL_POS]# або p.startswith(tuple(LEXICAL_POS))]
	lexical_density = len(lexical_items) / len(pos_tokens) if pos_tokens else 0
	pd.DataFrame([["Lexical density", lexical_density]],columns=["metric", "value"]).to_excel(writer, sheet_name="Lexical_Density", index=False)
	# ===== 13. Dispersion =====
	dispersion = Counter()
	for s in sentences:
		sent_words = set(w for w in jieba.cut(s) if CHINESE_RE.match(w))
		for w in sent_words:
			dispersion[w] += 1
	pd.DataFrame(dispersion.items(),columns=["word", "sentence_count"]).sort_values("sentence_count", ascending=False)\
	 .to_excel(writer, sheet_name="Dispersion", index=False)
	# ===== 14. Position Distribution =====
	position_dist = defaultdict(Counter)
	for s in sentences:
		sent_tokens = [w for w in jieba.cut(s) if CHINESE_RE.match(w)]
		n = len(sent_tokens)
		if n < 2: continue
		for i, w in enumerate(sent_tokens):
			if i == 0: position_dist[w]["initial"] += 1
			elif i == n - 1: position_dist[w]["final"] += 1
			else: position_dist[w]["middle"] += 1
	position_rows = []
	for word, pos_cnt in position_dist.items():
		position_rows.append([word,pos_cnt.get("initial", 0),pos_cnt.get("middle", 0),pos_cnt.get("final", 0)])
	pd.DataFrame(position_rows,columns=["word", "initial", "middle", "final"]).to_excel(writer, sheet_name="Position_Distribution", index=False)
	# ===== 15. Word length distribution =====
	pd.DataFrame(sorted(length_freq.items()),columns=["word_length", "count"]).to_excel(writer, sheet_name="Word_Length_Distribution", index=False)
	# ===== 16. Phrase frequency =====
	phrases = Counter()
	for s in sentences:
		tagged = [(w, p) for w, p in pseg.cut(s) if CHINESE_RE.match(w)]
		for i in range(len(tagged) - 1):
			if tagged[i][1].startswith("n") and tagged[i + 1][1].startswith("n"):
				phrase = tagged[i][0] + tagged[i + 1][0]
				phrases[phrase] += 1
				
	pd.DataFrame(phrases.most_common(),columns=["phrase", "frequency"]).to_excel(writer, sheet_name="Phrase_Frequency", index=False)
	# ===== 17. N-gram Frequencies (bigrams) =====
	bigrams = Counter()
	for i in range(len(words) - 1):
		bigrams[(words[i], words[i + 1])] += 1
	pd.DataFrame([("".join(bg), f) for bg, f in bigrams.items()],columns=["bigram", "frequency"]).sort_values("frequency", ascending=False)\
	 .to_excel(writer, sheet_name="Bigrams", index=False)
	# ===== 18. Collocations (PMI / t-score) =====
	from math import log2, sqrt
	total_tokens = len(words)
	total_bigrams = total_tokens - 1
	collocations = []
	for (w1, w2), f12 in bigrams.items():
		f1 = freq[w1]
		f2 = freq[w2]
		expected = (f1 * f2) / total_bigrams
		if f12 <= 1 or expected == 0: continue
		pmi = log2((f12 * total_bigrams) / (f1 * f2))
		t_score = (f12 - expected) / sqrt(f12)
		collocations.append((w1, w2, f12, pmi, t_score))
	pd.DataFrame(collocations,columns=["word_1", "word_2", "freq", "PMI", "t_score"]).sort_values("PMI", ascending=False)\
	 .to_excel(writer, sheet_name="Collocations", index=False)
print(f"\nУсі показники експортовано до Excel:")
print(OUTPUT_PATH)


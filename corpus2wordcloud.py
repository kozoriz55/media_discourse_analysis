SYMBOLS=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-')
def split_chinese_text(text, dictionary):
	words = []
	i = 0; l = len(text)
	while i < l:
		for j in range(i+12, i, -1):
			if text[i:j] in dictionary:
				words.append(text[i:j])
				i = j
				break
		else:
			words.append(text[i:i+1])
			i += 1
	return ''.join(w if w.upper() in SYMBOLS and next_w.upper() in SYMBOLS else w + " " for w, next_w in zip(words, words[1:]))

with open("C:\\Users\\davin\\Desktop\\wangyi_corpus.txt", 'rt', encoding='utf-8') as f1:
	chinese_text = f1.read()
with open("C:\\Users\\davin\\Desktop\\zh_orpho.txt", 'rt', encoding='utf-8') as f:
	chinese_dictionary = {word.split('+')[0] for word in f.readlines()}
chinese_words = split_chinese_text(chinese_text, chinese_dictionary)
with open("C:\\Users\\davin\\Desktop\\wangyi_corpus_sep.txt", 'wt', encoding='utf-8') as f2:
	f2.write(chinese_words)
print("файл успішно записаний")
# Видалення стоп-слів
from nltk.corpus import stopwords
stop_words = set(stopwords.words('chinese'))#840
filtered_words = " ".join([word for word in chinese_words if word not in stop_words]) 
#створення хмари
import matplotlib.pyplot as plt
from wordcloud import WordCloud
font_path = r"C:\Windows\Fonts\msyh.ttc"
wordcloud = WordCloud(font_path=font_path, width=800, height=400, background_color='white', colormap='viridis').generate(filtered_words)
# Відображення результату
plt.figure(figsize=(8, 4))
plt.imshow(wordcloud, interpolation='bilinear')#.to_array()
plt.axis("off")  # Прибираємо осі
#plt.tight_layout(pad=0) Прибираємо поля
plt.title("Хмара слів з корпусу 'Wangyi_news'", fontsize=14)
plt.show()
#замінити в C:\Users\davin\AppData\Local\Programs\Python\Python311\Lib\site-packages\wordcloud\wordcloud.py
#return np.asarray(self.to_image(), copy=copy) на return np.asarray(self.to_image())

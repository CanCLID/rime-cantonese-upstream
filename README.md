# rime-cantonese 上游詞表

本倉庫係 [rime-cantonese](https://github.com/rime/rime-cantonese) 嘅上游詞表。rime-cantonese 作為下游輸入法碼表會通過 CI 自動從本倉庫揸取更新構建新碼表。

## 結構

呢個上游詞表會將所有詞條分成以下幾類，每類對應一個文件：

1. `char.csv`：單字音
1. `word.csv`：常用詞
1. `phrase.csv`：短句
1. `eng.csv`：含有英文字母嘅詞條
1. `fragment.csv`：文字碎片、常見輸入組合、ngram
1. `trending.csv`未分類嘅流行詞

## 數據源

### 單字音

主要字音來源

- LSHK 電腦用漢字粵語拼音表 https://github.com/lshk-org/jyutping-table

參考數據源

- Unihan 12.0 kCantonese： ~30000 個帶粵拼字條 https://www.unicode.org/charts/unihan.html
- 粵語審音配詞字庫

### 詞條

- 《實用廣州話分類詞典》https://github.com/rime/rime-cantonese/blob/build/lexicons/%E3%80%8A%E5%AF%A6%E7%94%A8%E5%BB%A3%E5%B7%9E%E8%A9%B1%E5%88%86%E9%A1%9E%E8%A9%9E%E5%85%B8%E3%80%8B.tsv
-

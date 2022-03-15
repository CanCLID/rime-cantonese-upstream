# rime-cantonese 上游詞表

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-red.svg)](https://creativecommons.org/licenses/by/4.0/)

[English](https://github.com/CanCLID/rime-cantonese-upstream#rime-cantonese-upstream-word-list)

本倉庫係 [rime-cantonese](https://github.com/rime/rime-cantonese) 嘅上游詞表。rime-cantonese 作為下游輸入法碼表會通過 CI 自動從本倉庫揸取更新構建新碼表。

## 結構

呢個上游詞表會將所有詞條分成以下幾類，每類對應一個文件：

1. `char.csv`：單字音
1. `word.csv`：常用詞
1. `phrase_fragment.csv`：短句、文字碎片、常見輸入組合、ngram
1. `trending.csv`未分類嘅流行詞

## 數據源

單字音主數據源

- LSHK 電腦用漢字粵語拼音表 https://github.com/lshk-org/jyutping-table

參考數據源

- [Unihan 12.0 kCantonese](https://www.unicode.org/charts/unihan.html)
- [粵語審音配詞字庫](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/)
- [《廣州話正音字典》](https://github.com/jyutnet/cantonese-books-data/tree/master/2004_%E5%BB%A3%E5%B7%9E%E8%A9%B1%E6%AD%A3%E9%9F%B3%E5%AD%97%E5%85%B8)
- [《粵音小鏡》](https://zhuanlan.zhihu.com/p/21693656)

詞條主數據源

- [粵典](https://words.hk/faiman/analysis/wordslist/)
- [冚唪唥粵文](https://hambaanglaang.hk/)
- [《實用廣州話分類詞典》](https://github.com/rime/rime-cantonese/blob/build/lexicons/%E3%80%8A%E5%AF%A6%E7%94%A8%E5%BB%A3%E5%B7%9E%E8%A9%B1%E5%88%86%E9%A1%9E%E8%A9%9E%E5%85%B8%E3%80%8B.tsv)
- A Dictionary of Cantonese Slang
- 《廣州話詞典》
- 《地道廣州話用語》

# rime-cantonese Upstream Word List

This repo serves as the upstream data storage for [rime-cantonese](https://github.com/rime/rime-cantonese). The rime-cantonese repo regularly pulls data from this repo and compile the lexicon.

## Structure

This repo contains the following files:

1. `char.csv`: Characters
1. `word.csv`: Common words
1. `phrase_fragment.csv`: Short phrases, input fragments and combos, ngrams
1. `trending.csv`: Uncategorized newly added words.

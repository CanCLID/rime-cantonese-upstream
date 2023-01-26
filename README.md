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

### 單字收錄 `char.csv` 格式説明

| char         | jyutping                 | pron_rank                                                                                                                 | tone_var                                               | literary_vernacular                                                      | comment                                                                                                                                               |
| ------------ | ------------------------ | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 漢字 Unicode | 粵拼：漢字對應嘅粵拼發音 | 發音常見度： <ul><li>`預設`：必須且唯一，常用度一定最高</li><li>`常用`：可以有多於一個</li><li>`罕見`</li><li>`棄用`</li> | 該發音是否本調變調：<ul><li>`本調`</li><li>`變調`</li> | 該發音是否文白異讀：<ul><li>`無`</li><li>`文讀`</li><li>`白讀`</li></ul> | 該發音例子、解釋：<ul><li>如果係罕見音，唔可以留空</li><li>如果個發音無能產性，就放例詞</li><li>可以放發音來源</li><li> 唔可以有半角逗號`,`</li></ul> |

高升變調唔歸入`白讀`，歸入`變調`。`-aak`/`-ak`互換、`ek`/`ik`等等先歸入`白讀`。

## 收錄原則

### 單字

- 區分 ng-/∅- 聲母，統一剩收原讀音，唔收混淆後嘅讀音。
- 除簡化漢字外，所有異體字字形都收錄。字形轉換交畀 [OpenCC](https://github.com/BYVoid/OpenCC) 處理。
- 唔收懶音，例如 n-/l- 混淆音

### 詞語

- 同單字音一樣，區分 ng-/∅- 聲母。
- 所有詞條全部標準化成 OpenCC 字形。
- 詞語標音全部記作實際發音，即係變調後嘅發音。

## 數據源

單字音主數據源

- LSHK 電腦用漢字粵語拼音表 https://github.com/lshk-org/jyutping-table

參考數據源

- [Unihan 12.0 kCantonese](https://www.unicode.org/charts/unihan.html)
- [粵語審音配詞字庫](https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/)
- [《廣州話正音字典》](https://github.com/jyutnet/cantonese-books-data/tree/master/2004_%E5%BB%A3%E5%B7%9E%E8%A9%B1%E6%AD%A3%E9%9F%B3%E5%AD%97%E5%85%B8)

詞條主數據源

- [粵典](https://words.hk/faiman/analysis/wordslist/)
- [冚唪唥粵文](https://hambaanglaang.hk/)
- [《實用廣州話分類詞典》](https://github.com/rime/rime-cantonese/blob/build/lexicons/%E3%80%8A%E5%AF%A6%E7%94%A8%E5%BB%A3%E5%B7%9E%E8%A9%B1%E5%88%86%E9%A1%9E%E8%A9%9E%E5%85%B8%E3%80%8B.tsv)
- A Dictionary of Cantonese Slang
- 《廣州話詞典》
- 《地道廣州話用語》

## 貢獻人員名單

- laubonghaudoi
- Ayaka
- Leimaau
- Chaak
- Bing Cheung
- Cherry
- Lili Ou
- Philip Wong
- Henry Chan
- Alex Man

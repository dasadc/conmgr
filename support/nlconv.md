# nlconv.py

`nlconv.py`は、問題データ生成ツールです。  
Perlで記述された`nlconv.pl`を、Pythonに移植しました。使い方は、Perl版とほぼ同様です。  
DAシンポジウム2017アルゴリズムのルールに対応しています。


## 必要なライブラリ

openpyxlが必要です。

    pip install openpyxl

## 実行例


    % ./nlconv.py sample2017.xlsx
    input_file = sample2017.xlsx
    Q1 [1/2]
    Q1 [2/2]
    sample2017_Q1_adc_sol.txt
    sample2017_Q1.txt
    sample2017_Q1.csv
    sample2017_Q1_adc.txt
    Q2 [1/2]
    Q2 [2/2]
    sample2017_Q2_adc_sol.txt
    sample2017_Q2.txt
    sample2017_Q2.csv
    sample2017_Q2_adc.txt

    % ./nlconv.py --rule 2016 sample.xlsx 
    input_file = sample.xlsx
    Q1 [1/1]
    sample_Q1.txt
    sample_Q1.csv
    sample_Q1_adc.txt
    Q2 [1/1]
    sample_Q2.txt
    sample_Q2.csv
    sample_Q2_adc.txt
    Q3 [1/1]
    sample_Q3_adc_sol.txt
    sample_Q3.txt
    sample_Q3.csv
    sample_Q3_adc.txt
    Q4 [1/2]
    Q4 [2/2]
    sample_Q4_adc_sol.txt
    sample_Q4.txt
    sample_Q4.csv
    sample_Q4_adc.txt


# nlconv.pl (旧バージョン)

`nlconv.pl`は、問題データ生成ツールです。

Excelファイル(.xls|.xlsx)形式で問題を記述しておいて、`nlconv.pl`を使って、テキストファイル形式の問題ファイルを生成できます。


## 必要なライブラリ

そもそも、perlスクリプトなので、実行するためにperlが必要です。

追加のライブラリとして、`Spreadsheet::ParseExcel` と `Spreadsheet::XLSX` が必要ですので、インストールしておいてください。

CentOS7の場合、EPELからインストール可能でした。

```
perl-Spreadsheet-ParseExcel.x86_64               0.5900-8.el7               epel
perl-Spreadsheet-XLSX.noarch                   0.13-8.el7                   epel
```

```
sudo yum install perl-Spreadsheet-ParseExcel.x86_64 perl-Spreadsheet-XLSX.noarch
```

Ubuntu 14.04 LTSでは、以下のようにしてインストールできます。
```
sudo apt-get install libspreadsheet-xlsx-perl
```


FreeBSDでも、パッケージかportsからインストールできます。

パッケージが利用できない場合でも、CPANを利用して、かんたんにインストールできると思います。

```
sudo yum install perl-CPAN.noarch
cpan
install Spreadsheet::ParseExcel
install Spreadsheet::XLSX
```

## 実行例

```
% ./nlconv.pl sample.xlsx
input = sample.xlsx
sample_Q1.txt
sample_Q1.csv
sample_Q1_adc.txt
sample_Q2.txt
sample_Q2.csv
sample_Q2_adc.txt
sample_Q3.txt
sample_Q3.csv
sample_Q3_adc.txt
```

入力ファイル

- 1シートに、1問ずつ、記述します。
- サンプルファイル sample.xlsx を参照してください。

出力ファイル

- 1問(1シート)あたり、3種類のテキストファイルが出力されます。
- 意味は、見た目でわかると思います。


# 問題の作成方法

Excelで適当に「正解の絵」を描くだけで、OKです。

具体例として、[2014年のプレゼン資料](http://www.sig-sldm.org/DC2014/slides.pdf)をご覧ください。

- P.30「今回の問題作成方法」のように、Excelで、正解の絵を描きます。
- P.36-50にも、出題した問題が、同様に掲載されています。

P.30では、線がすべて数字でうめつくされているのに対して、
P.36-50は、端点のみに数字が入っています。

これはどちらでもOKです。ただし、中途半端なところに、数字を残さないでください。
線毎に

- 最初から最後まで、すべて数字でうめつくす
- 端点のみ数字を書く

の、どちらかです。線の番号が違っていれば、混在してもOKかもしれません（？）

色は、見やすさのためだけのものなので、どうでもいいです。

Excel上でセルをコピペして描いていくときは、P.30の形式が作業しやすいと思います。

1ファイルで複数のワークシートを使って、複数問、書けます。


# 2016年版ルールへの対応

2016年版ルールで導入された、複数の層がある場合にも対応しています。

- 層ごとに、ワークシートを分けて記述してください。
- ワークシート名は、`名前.1`、`名前.2`という形式にします。層の番号を、`.`の後につけます。たとえば、2層の場合、`Q4.1`、`Q4.2`とします。
- ビアは、`(ビア名)=(数字)`という形式で記述します。たとえば、`a=1`なら、「そのマスにビア`a`を配置して、線`1`と接続している」という意味です。

1層だけの問題をつくりたい場合は、次のようにします。

- 層の名前は、`名前.1`というように、`.1`をつけます。
- 層の番号は1、層の数は1とします。
- ビアは記述しません。

以下のセルから、ツールがデータを読み取ります。それ以外のセルの値は、無視するので、コメントを残すなどの目的に利用できます。

| セル | 意味 |
|------|------|
|A1    |行の数|
|A2    |列の数|
|C1    |Aと書いておくと、nlconv.plは回答データも出力する|
|D1    |層の番号。1,2,…|
|F1    |層の数|
|B4〜  |盤面データの座標(0,0)。ここから右下方向へ、盤面を記述する|


ワークシート「Q4.1」の内容

![ワークシートQ4.1](sample_Q4_1.png)

ワークシート「Q4.2」の内容

![ワークシートQ4.2](sample_Q4_2.png)


# 2017年版ルールへの対応

2017年版ルールでは、ビアの位置指定が無くなりました。

- `nlconv.py`は、2017年版ルールに対応しています。
- `nlconv.pl`は、2017年版ルールに対応していません。

https://github.com/dasadc/conmgr/blob/master/adc2016.md
https://github.com/dasadc/resources/blob/master/adc2017/adc2017rule.md
https://dasadc.github.io/adc2017/rule.html



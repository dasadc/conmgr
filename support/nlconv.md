# nlconv.pl

nlconv.plは、問題データ生成ツールです。

Excelファイル(.xls,.xlsx)形式で問題を記述しておいて、`nlconv.pl`を使って、テキストファイル形式の問題ファイルを生成できます。


## 必要なライブラリ

そもそも、perlスクリプトなので、実行するためにperlが必要です。

追加のライブラリとして、Spreadsheet::ParseExcel と use Spreadsheet::XLSX が必要ですので、インストールしておいてください。

CentOS7の場合、EPELからインストール可能でした。

```
perl-Spreadsheet-ParseExcel.x86_64               0.5900-8.el7               epel
perl-Spreadsheet-XLSX.noarch                   0.13-8.el7                   epel
```

```
sudo yum install perl-Spreadsheet-ParseExcel.x86_64 perl-Spreadsheet-XLSX.noarch
```

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


## 問題の作成方法

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

Excel上でセルをコピペして描いていくときは、P.30のような形式のほうが作業しやすいと思います。

1ファイルで複数のワークシートを使って、複数問、書けます。

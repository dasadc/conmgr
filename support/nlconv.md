# nlconv.pl

nlconv.plは、問題データ生成ツールです。

Excelファイル(.xls,.xlsx)形式で問題を記述しておいて、`nlconv.pl`を使って、テキストファイル形式の問題ファイルを生成できます。


## 必要なライブラリ

そもそも、perlスクリプトなので、実行するためにperlが必要です。

追加のライブラリとして、Spreadsheet::ParseExcel と use Spreadsheet::XLSX が必要ですので、インストールしておいてください。

CentOS7の場合、EPELからインストール可能でした。

```
aaaa
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

# DAシンポジウム アルゴリズムデザインコンテスト （２０１６年度版）

本リポジトリは、[DAシンポジウム2016](http://www.sig-sldm.org/das/)で行う[アルゴリズムデザインコンテスト](http://www.sig-sldm.org/das/ADC/ADC.html) の参加者向け解説、およびコンテスト内にて使用する「**自動運営システム**」のソースおよび解説を含みます。

## 最新情報

- 2016-09-02 自動運営システムのテストを開始しました。
- 2016-08-21 申込最終期限を記載しました。また、問題チェック用スクリプト nlcheck.py をアップデート（デバッグ）しています。
- 2016-07-08 申込期限延長しました。およびページを微修正しました。
- 2016-06-30 トップページを2016年度版に更新しました。

## 参加者向けアナウンス事項

### 事前準備関連
* [user document](adc2016.md) にて問題・回答フォーマットを定義しました。ご確認ください。
* 現在ADC2016向け自動運営システム準備中です。

<!--
* 詳細は [アルゴリズムデザインコンテスト当日までにやってほしいこと](#アルゴリズムデザインコンテスト当日までにやってほしいこと) を参照ください。
-->

### 申し込み関連
<!-- * ADC2016参加申し込み（＝DAS2016投稿申し込み）は[DAS2016投稿Webフォーム](https://www.ipsj.or.jp/02moshikomi/event/event-da2016-toukou.html)からお願いいたします。 -->
 **参加申し込みは締め切らせていただきました。ご応募ありがとうございました。** 


## アルゴリズムデザインコンテスト参加者向けマニュアル

[user document](adc2016.md)

<!--
## 内部の開発者向けマニュアル

[development2016](adc2016dev.md)
[development2015](adc2015dev.md)
-->

-----

<!--
*注意：以下は過去のドキュメントです。参考までに残してあります。２０１６年度版へのアップデートは8月中予定*
-->

## ADC自動運営システム

### 自動運営システムって何ですか？

- 参加者が自作した問題データを収集します。
- 問題データを配布します。
- 回答データを収集します。
- 回答を採点します。
- コンテストの進捗状況をリアルタイムで表示します。


### アルゴリズムデザインコンテスト当日までにやってほしいこと

参加者のみなさんが開発したソフトウェア（ソルバー）と、自動運営システムとが、正常に連携して動作するかどうか、__事前に動作確認を行います__。

これは、インターネット上で提供されているクラウドサービスを利用して行います。



### 動作確認作業（事前）の流れ 

1. DAシンポジウム2016幹事より、アカウント情報をメールで送付します。
2. [ADCサービスの利用方法](adc2015.md)を見ながら、動作確認してください。
3. 自動運営システムに関して、不具合、不明点、提案などありましたら、[Issues](https://github.com/dasadc/conmgr/issues "Issues")に書き込むか(※GitHubのアカウントが必要)、幹事へメールでお伝え下さい。
4. 自動運営システムの修正・改良が行われたときは、その結果に問題ないかの確認に協力をお願いします。

### 自作問題データの扱い

自作問題データのアップロードもできますが、動作確認中にアップロードしてしまうと、他のチームに、問題がばれてしまいます。本番までの秘密としておいてください。

- データ形式が正しいかを[チェックするだけ](adc2016.md#qcheck)の（データを保存しない）専用機能があります。
  - [server/nlcheck.py](server/nlcheck.py) を使って確認することもできます（[ドキュメント](server/nlcheck.md)）。

<!--
  - [server/numberlink.py](server/numberlink.py) を使って確認することもできます。実行方法: `python numberlink.py 問題ファイル`
-->

### 回答方法

コンテスト本番では、回答は1問につき1回しか許されませんが、
動作確認期間中は、何度でも、回答できるようにしておきます。


## 自動運営システムを使った、コンテストの流れ （概要）

### コンテストの開始前

1. 参加者がログインします。
2. 参加者は、自作の問題データをアップロードします。
   - アップロードした問題データを、削除したり、アップロードしなおすこともできます。

3. ある時刻がきたら、自作問題のアップロードが締め切られます。
4. 出題問題を確定します。
5. 定刻になったら、コンテストが開始します。

### コンテストの開始後

参加者は、以下のことを行います。

1. 出題問題の番号一覧リストをダウンロードします。
2. 出題問題を、1つ、ダウンロードします。
   - 1度に1問だけダウンロードできます。繰り返して全問ダウンロードしてもかまいません。
3. ソルバーで問題を解きます。
4. 解いている最中に、3分に1回程度の頻度で、ステータス報告を行います。
   - これは、参加者側のシステムが正常に動いているかを、自動運営システムから判断できるようにするためです。
5. 解が得られたら、回答データをアップロードします。
6. つづけて、回答の補足情報（計算時間、使用メモリ量など）をアップロードします。
7. 2からを、繰り返します。
8. もし、なかなか解が得られない場合は、別の問題に取り組んでもかまいません。
9. 定刻が来たら、コンテストが終了です。回答データのアップロードが締め切られます。



## アルゴリズムデザインコンテスト当日の流れ

基本的には、事前の動作確認で行ったことと同じです。

アカウントは本番でも同じものを使用します。

コンテスト本番では、自動運営システムにアクセスするときのURLが変わりますので、間違えないよう、ご注意ください。

## 自動運営システムの動作モード

1時間の周期で、動作モードが遷移していきます。

現在時刻の「分」の値によって、ユーザーができることが変化していきます。本番のつもりで、動作を確認してみてください。

```
状態   時:分:秒-時:分:秒
[init]
[im0]  HH:00:00-HH:02:59 ... (準備中)
[Qup]  HH:03:00-HH:14:59 ... 問題アップロード可能／出題リストを削除;回答データを削除
[im1]  HH:15:00-HH:19:59 ... 問題アップロード締め切り／出題リストを作成
[Aup]  HH:20:00-HH:54:59 ... 回答アップロード可能
[im2]  HH:55:00-HH:59:59 ... 回答アップロード締め切り
```

今のところ、ユーザーがアップロードした問題は、自動的に削除されることはありません。


## (付録) 問題の作成方法

Excelファイルから問題データへ変換するツールがあります。

[ドキュメント](support/nlconv.md)


# conmgr

[DAシンポジウム2015](http://www.ipsj.or.jp/kenkyukai/event/s-da2015.html)で行う[アルゴリズムデザインコンテスト](http://www.sig-sldm.org/designcontest.html)にて使用する「**自動運営システム**」について説明します。


## アルゴリズムデザインコンテスト参加者向け

[user document](adc2015.md)

## 内部の開発者向け

[development](adc2015dev.md)


## 自動運営システムは何をするものか？

- 参加者が自作した問題データを収集します。
- 問題データを配布します。
- 回答データを収集します。
- 回答を採点します。
- コンテストの進捗状況をリアルタイムで表示します。

## アルゴリズムデザインコンテスト当日までにやるべきこと

参加者のみなさんが開発したソフトウェア（ソルバー）と、自動運営システムとが、正常に連携して動作するかどうか、事前に動作確認を行います。

これは、インターネット上で提供されているクラウドサービスを利用して行えます。



### 動作確認作業の流れ 

1. DAシンポジウム2015幹事より、アカウント情報をメールで送付します。
2. [user document](adc2015.md)を見ながら、動作確認してください。
3. 自動運営システムに関して、不具合、不明な事、提案などありましたら、Issues(※未確認)に、書き込んでください。
4. 自動運営システムの修正・改良が行われたときは、その結果に問題ないかの確認に協力をお願いします。

### 自作問題データ

自作問題データのアップロードもできますが、動作確認中にアップロードしてしまうと、他のチームに、問題がばれてしまいます。本番までの秘密としておいてください。

- データ形式が正しいかをチェックするだけの（データを保存しない）専用機能を提供する予定です。

### 回答データ

コンテスト本番では、回答は1問につき1回しか許されませんが、
動作確認期間中は、何度でも、回答できるようにしておきます。



## 自動運営システムを使った、コンテストの流れ （概要）

コンテストの開始前

1. 参加者がログインします。
2. 参加者は、自作の問題データをアップロードします。
   - アップロードした問題データを、削除したり、アップロードしなおすこともできます。

3. ある時刻がきたら、自作問題のアップロードが締め切られます。
4. 出題問題の確定作業を行われます。
5. 定刻になったら、コンテストが開始します。

コンテストの開始後

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





## アルゴリズムデザインコンテスト当日にやること

基本的には、事前の動作確認で行ったことと同じです。


コンテスト本番では、自動運営システムにアクセスするときのURLが変わりますので、間違えないでください。


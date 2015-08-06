# 開発者向けメモ

# configファイル adcconfig.py

`SECRET_KEY`と`SALT`を、ランダムな文字列に書き換え、他人から見ないように管理しておくこと。gitに入れてはいけない。

    cp adcconfig.sample.py adcconfig.py

元のパスワードは不明なため、SECRET_KEYとSALTを変更したときは、アカウントを作成しなおす必要がある。ユーザー名、名称、uid、gidは既存のものがわかるが、パスワードは新規に設定しなければならない。


# アカウント作成

1. `adcusers_in.sample.py` を `adcusers_in.py` という名前でコピーする
2. `adcusers_in.py` にユーザー情報を書き込む。パスワードは生パスワードを書く
3. `adcusers_gen.py` を実行する。パスワードがハッシュに置き換わった `adcusers.py` が作られる。実際の処理では、`adcusers.py`が参照される
4. `adcusers_in.py` は削除することを推奨する

最初に、ファイル`adcusers.py`を見た後に、データベースを見に行く仕組みになっている。そのため、`adcusers.py`では、adminアカウントのみ定義しておき、ユーザーアカウントは、データベースへ登録するのがよい。

## adminアカウント

`adcusers.py`ファイルに直接書く。gitに入れてはいけない。

さらに、データベースにも登録する。この理由は、問題データを登録できるユーザーは、データベース上に登録されたアカウントのみ、という仕様になっているため。


## ユーザーアカウント

コマンドラインツールadccliで作成できる。

    adccli create-user 'test-01' '適切なパスワード'  'ウサギさんチーム' 1001 1000

### 複数アカウントを一括登録

    adccli create-users ファイル

ファイルは、`adcusers_in.sample.py`と同じ書式。


# 認証の仕組み

Flaskのsessionを利用して、認証の仕組みを設けている。

1. クライアントは、ユーザー名、パスワードを送ってloginを要求する
2. サーバ側でsession情報を更新。サーバからクッキーがもらえる。session情報はクッキーに保存されている
3. 以後、クッキーをつけて処理をつづける
4. クライアントがlogoutを要求すると、session情報が消去される

クッキーの内容は暗号化されており、その鍵は、adcconfig.pyの`SECRET_KEY`で指定することになっている。

## セッション情報

セッション情報は、サーバー側（データベース）ではなくクッキーに保存される。

そのため、同じクッキーを使っていれば、サーバを切り替えても（`SECRET_KEY`が同じならば）、ログイン状態が維持される。


# Google App Engine Datastore

datastore.pyとadcutil.pyを参照。

# セキュリティ

本当は、`adccli --URL='https://das-adc.appspot.com/'` でアクセスすることが望ましい。
- 実は、httpsでも動く。
  - しかし、proxyサーバ経由だと動かない
- 使っているpythonのライブラリがhttplib。これの出来が悪くて、proxyサーバさえまともに扱えず、自前で実装している
- もっといいサードパーティのライブラリがあるらしいが、それを利用すると、ユーザーに追加インストールを強いることになってしまうので、今回は見送った。
  - Pythonで標準で用意されているライブラリだけで動くように、adccliは作ってある


# ADCサービスAPI

RESTful API風になっています。

以下は、今後変更される可能性があります。まだ実装していないものも含まれます。
具体的な使用方法は、curlの実行例を参考にしてください。

    #path                            メソッド、説明
    #--------------------------------------------------------------------------
    /                                GET    お知らせ
    /login                           GET    ログイン画面(HTML form)
    /login                           POST
    /logout                          GET,POST
    /whoami                          GET    自分のユーザー名を返す
    /Q                               GET    出題の一覧リストを返す
    /Q/all-in-zip                    GET    未実装
    /Q/<Q-number>                    GET    出題データを返す
	/Qcheck                          PUT    問題ファイルの妥当性をチェックする
	/Qcheck                          GET,POST  Webブラウザ用
    /A                               GET    すべての回答データの一覧リストを返す
    /A                               DELETE すべての回答データを削除する
    /A/<username>                    GET    回答の一覧リストを返す 本番では禁止
    /A/<username>/Q                  GET    Webブラウザ用
    /A/<username>/Q/<Q-number>       PUT    回答提出
    /A/<username>/Q/<Q-number>       GET    回答データを返す 本番では禁止
    /A/<username>/Q/<Q-number>       DELETE 回答データを削除 本番では禁止
    /A/<username>/Q/<Q-number>/info  GET,PUT,DELETE 回答の補足情報にアクセス
    /user/<username>/password        PUT    パスワード変更  未実装
    /user/<username>/Q               GET    問題データの一覧リストを返す
    /user/<username>/Q/<Q-number>    PUT,POST,GET,DELETE  問題データのアクセス
    /user/<username>/alive           PUT    死活監視用
    /user/<username>/log             GET,DELETE    ログデータ
    /user/<username>/log/<key>/<number> GET,DELETE ログデータ
    /admin/user                      GET    ユーザー一覧リスト
    /admin/user/<username>           GET,POST,DELETE  ユーザー情報取得、ユーザーアカウント作成、削除
    /admin/Q/all                     GET    すべての問題の一覧リストを返す
    /admin/Q/list                    PUT    出題リストを作成する
    /admin/Q/list                    GET    出題リストを返す
    /admin/Q/list                    DELETE 出題リストを削除する
    /admin/log                       GET,DELETE  ログデータ
    /admin/log/<key>/<number>        GET,DELETE  ログデータ
    /score                           GET  スコア 未実装
    /score/<username>                GET  スコア 未実装

    # 例
    #path                            メソッド
    #--------------------------------------------------------------------------
    /Q/01                            GET
    /Q/02                            GET
    /A/team-01/Q/1                   POST
    /A/team-01/Q/2                   POST
    /user/team-01/Q/1                PUT,POST,GET,DELETE
    /user/team-01/Q/2                PUT,POST,GET,DELETE
    /user/team-01/Q/3                PUT,POST,GET,DELETE
    /user/team-02/Q/1                PUT,POST,GET,DELETE
    /admin/user/team-01              GET
    /admin/user/team-01              POST
    /score/team-03                   GET

- 細かいことだが、POSTで投稿。PUTは差し換え。POSTしたあとでないと、PUTできない。

- 問題データ、回答データは、プレインテキスト形式。それ以外では、原則としてJSON形式を採用している。２種類を使い分けているのは、JSON形式では、改行コードをデータにそのまま含めることができないのが理由。
- Q-numberは、10進数の整数であり、1,2でも、01,02でも、0001,0002でもよい。
- 指定できるQ-numberは、一般ユーザは1,2,3のどれか。admin権限があれば自由。

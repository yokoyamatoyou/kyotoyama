

# **Google Cloudを活用した医療画像解析MVP開発計画書**

## **第1部：MVP戦略・アーキテクチャ設計**

### **1.1. エグゼクティブサマリーと技術概要**

本計画書は、医療画像のAI解析を行うための最小実行可能製品（MVP）の開発に関する包括的なロードマップを提示するものです。本MVPの目的は、認証されたユーザーが医療画像をアップロードし、AIモデルによる病変の可能性の特定・分析結果を、インタラクティブで理解しやすいWebインターフェースを通じて受け取ることを可能にする、セキュアでスケーラブル、かつコスト効率の高いアプリケーションを構築することにあります。

開発戦略としては、段階的アプローチを採用します。まずローカル環境でのプロトタイピングから開始し、アプリケーションのコアロジックを検証します。その後、本番環境に対応可能な形にパッケージ化し、最終的にGoogle Cloudプラットフォーム上へデプロイします。このアプローチにより、機能開発とインフラ構築の懸念を分離し、プロジェクトのリスクを段階的に低減させます。

採用する技術スタックは、Google Cloud上でインタラクティブなAI/ML Webアプリケーションを構築するための現代的なベストプラクティスを反映しています。

* **GUI（フロントエンド）:** Pythonネイティブで迅速なWeb UI開発を可能にする**Streamlit** 1 を採用します。これにより、データサイエンティストやMLエンジニアが直接UIを構築でき、専門のフロントエンド開発者への依存を最小限に抑えます。  
* **バックエンド & ホスティング:** サーバーレスでコンテナベースの**Google Cloud Run** 2 を選択します。特に、MVPの断続的なトラフィックに対してコスト効率を最大化する「スケール・トゥ・ゼロ」機能は、本プロジェクトに最適です 4。  
* **AI & 解析:** 専門解析と解釈・レポート生成を組み合わせたデュアルAIアプローチを活用します。  
  * **専門解析:** 医療画像のセグメンテーションにおいて最先端の性能を持つオープンソースツールキット**ANTsPyNet** 6 を利用します。  
  * **解釈 & レポート生成:** Googleのマルチモーダルモデルである**Vertex AI (Gemini Pro Vision)** 8 を活用し、解析結果を解釈して構造化された人間が読める形式のサマリーを生成します。  
* **セキュリティ:** Googleの**Identity-Aware Proxy (IAP)** 10 をセキュリティレイヤーとして指定します。これにより、アプリケーションコードを複雑化させることなく、エンタープライズレベルの一元的な認証・認可を実現します。

ユーザーが言及した「2025年5月頃にデプロイさせやすいサービス」とは、Googleが近年、特にそのチュートリアルやラボで強力に推進している「StreamlitアプリケーションをGoogle Cloud Run上で実行し、Geminiと統合する」というパターンを指していると結論付けられます 2。これは単なる便利な選択肢ではなく、Googleが推奨する迅速なAIアプリケーション開発のための検証済みパターンです。本計画は、この最新かつ導入が容易なソリューションが、ユーザーの求めるものであることを確認し、その実現に向けた具体的な指針を提供します。

### **1.2. システムアーキテクチャ設計**

本MVPのシステムは、エンドユーザーの操作からデータの流れ、そして結果の表示まで、一貫性のあるセキュアなアーキテクチャに基づいています。以下にその全体像と各コンポーネントの役割を詳述します。

#### **1.2.1. エンドツーエンドのデータフロー**

1. ユーザーはアプリケーションの公開URLにアクセスします。  
2. リクエストはまず**Google Cloud Load Balancer**によって捕捉されます。  
3. ロードバランサに統合された**Identity-Aware Proxy (IAP)** が、ユーザーをGoogleがホストするサインインページにリダイレクトし、Googleアカウントでの認証を要求します 10。  
4. 認証が成功すると、IAPはユーザーのIDを、事前に設定された認可済みプリンシパル（IAMロール）のリストと照合します 10。  
5. 認可されたユーザーのリクエストのみが、バックエンドの**Cloud Run**サービスに転送されます。  
6. Cloud Runは、デプロイされたDockerイメージからコンテナインスタンスを起動します（インスタンスが稼働していない場合は「コールドスタート」が発生します） 3。  
7. コンテナ内で起動した**Streamlitアプリケーション**が初期化され、ユーザーにファイルアップロード用のウィジェットを提示します。  
8. ユーザーが医療画像をアップロードします。  
9. Streamlitのバックエンドは、アプリケーション内の**ANTsPyNetモジュール**を呼び出し、画像のセグメンテーション処理を実行します。これにより、病変の可能性がある領域のマスクデータと座標が生成されます。  
10. 次に、アプリケーションは**Vertex AI API**を呼び出します。この際、元の画像、生成されたマスク、そして慎重に設計されたプロンプトを**Gemini Pro Visionモデル**に送信します 8。  
11. Geminiは、自然言語による説明、信頼度スコア、その他のメタデータを含む、構造化された**JSONオブジェクト**を返却します 12。  
12. StreamlitアプリケーションはこのJSONを解析し、最終的な結果（元画像、ヒートマップ/マスクのオーバーレイ表示、Geminiによるテキストサマリー）をユーザーに分かりやすく表示します。

#### **1.2.2. 技術スタックと採用理由**

以下の表は、本アーキテクチャを構成する主要な技術要素とその採用理由をまとめたものです。各選択は、プロジェクトの要件（セキュリティ、スケーラビリティ、開発速度、コスト効率）を最大化するために、意図的かつ調査に基づいて行われています。

| コンポーネント | 採用技術 | 正当化と主要な典拠 |
| :---- | :---- | :---- |
| **GUIフレームワーク** | Streamlit | Pythonネイティブでの迅速なWebアプリ開発が可能。データ中心のアプリケーションに最適で、GCPエコシステムとシームレスに連携する。 1 |
| **コンピュート/ホスティング** | Google Cloud Run | サーバーレス、フルマネージド。MVPに理想的なコスト効率を実現するスケール・トゥ・ゼロ機能を持ち、コンテナからデプロイされる。 3 |
| **認証** | Identity-Aware Proxy (IAP) | エンタープライズグレードの一元化されたセキュリティレイヤー。アプリレベルの認証コードを必要とせず、IAMを通じてアクセスを管理する。 10 |
| **ロードバランシング** | Cloud Load Balancer | IAP統合に必須。単一の安定したイングレスポイントを提供し、SSLを有効化する。 11 |
| **コンテナ化** | Docker | アプリケーションと依存関係をパッケージ化する標準技術。ローカル開発からクラウド本番環境までの一貫性を保証し、Cloud Runの前提条件となる。 3 |
| **イメージストレージ** | Google Artifact Registry | GCP内でコンテナイメージを安全に保管するための、プライベートなDockerレジストリ。 |
| **画像解析** | ANTsPyNet | 医療画像のレジストレーションとセグメンテーションのための、最先端のオープンソースツールキット。 6 |
| **AIによる解釈** | Vertex AI (Gemini Pro Vision) | 画像コンテンツの理解、構造化されたテキストサマリーの生成、リッチで文脈的な分析を提供するためのマルチモーダルモデル。 8 |

### **1.3. 段階的開発ロードマップ**

本プロジェクトは、以下の3つの明確なフェーズに分けて推進します。各フェーズは具体的な目標と成果物を持ち、順次進めることで、着実な開発とリスク管理を実現します。

* **フェーズ1：ローカルでのプロトタイピングとコアロジック開発**  
  * **目標:** ローカルマシン上で全てのアプリケーション機能を構築し、検証する。  
  * **成果物:** コマンドラインから実行可能な、動作するPythonアプリケーション。  
* **フェーズ2：本番環境グレードのコンテナ化**  
  * **目標:** 動作するアプリケーションを、セキュアで効率的、かつ自己完結したDockerイメージにパッケージ化する。  
  * **成果物:** あらゆる環境で実行可能なDockerイメージ。  
* **フェーズ3：セキュアでスケーラブルなクラウド展開**  
  * **目標:** コンテナをGoogle Cloudにデプロイし、ネットワーキングを設定し、認可されたユーザーのためにアプリケーションを保護する。  
  * **成果物:** 公開アクセス可能でセキュアなWebアプリケーション。

## **第2部：詳細な実装・コーディング計画**

### **2.1. フェーズ1：ローカルでのプロトタイピングとコアロジック開発**

このフェーズの目的は、クラウドへのデプロイを意識する前に、アプリケーションの中核となる機能をローカル環境で完全に実装し、その動作を検証することです。これにより、機能的なバグとインフラの問題を切り分けて対処できます。

#### **2.1.1. 開発環境のセットアップ**

1. **Python仮想環境の構築:** プロジェクトの依存関係をシステムから隔離するため、仮想環境を作成します。  
   Bash  
   python \-m venv.venv  
   source.venv/bin/activate  \# macOS/Linux  
   \#.venv\\Scripts\\activate   \# Windows

2. **依存関係ファイルの作成:** プロジェクトルートにrequirements.txtファイルを作成し、初期の依存ライブラリを記述します。ライブラリのバージョンを固定することは、再現性を確保するためのベストプラクティスです 15。  
   \# requirements.txt  
   streamlit==1.35.0  
   google-generativeai==0.7.1  
   antspyx==0.4.3  
   antspynet==1.0.3  
   tensorflow==2.16.1  
   pydantic==2.7.4

3. **ライブラリのインストール:**  
   Bash  
   pip install \-r requirements.txt

#### **2.1.2. プロジェクト構造**

一貫性と保守性を高めるため、以下のディレクトリ構造を推奨します。

mvp-medical-app/  
├──.venv/  
├── app.py                \# Streamlitアプリケーションのメインエントリーポイント  
├── pages/  
│   └── 1\_Image\_Analysis.py \# 主要な画像解析ページのスクリプト  
├── modules/  
│   ├── image\_analyzer.py \# ANTsPyNetを使用した画像解析ロジック  
│   └── report\_generator.py \# Gemini APIを使用したレポート生成ロジック  
└── requirements.txt

Streamlitはpages/ディレクトリ内のPythonファイルを自動的に検出し、サイドバーにナビゲーションリンクとして追加します。これにより、マルチページアプリケーションの構築が容易になります 1。

#### **2.1.3. Streamlit GUIの開発 (1\_Image\_Analysis.py)**

このファイルは、ユーザーインターフェースの主要部分を担います。

* **ページ設定:** st.set\_page\_config()を使用して、ページのタイトルやレイアウトを設定します。  
* **ファイルアップロード:** st.file\_uploader()ウィジェットを配置し、ユーザーが医療画像（例：NIfTI, PNG形式）をアップロードできるようにします。  
* **処理中のフィードバック:** st.spinner()コンテキストマネージャを使用し、時間のかかる解析処理中にユーザーへ待機中であることを示します。  
* **結果のレイアウト:** st.columns()を使用して画面を分割し、入力画像、解析結果のオーバーレイ表示、Geminiによるテキストレポートを並べて表示することで、視認性を高めます。  
* **キャッシング:** Streamlitのキャッシング機能（st.cache\_dataとst.cache\_resource）を積極的に活用します 1。これにより、ウィジェットの操作などで再描画が発生した際に、時間のかかる画像解析やAPI呼び出しを再実行するのを防ぎ、アプリケーションの応答性を大幅に向上させます。

#### **2.1.4. 画像解析モジュール (image\_analyzer.py)**

このモジュールは、アップロードされた画像の具体的な解析処理をカプセル化します。

* **関数の定義:** analyze\_image(uploaded\_file)のような関数を定義します。この関数はStreamlitからアップロードされたファイルオブジェクトを受け取ります。  
* **ANTsPyNetの利用:** 関数内部で、ANTsPyNetライブラリを使用して画像解析を行います。MVPの具体的な機能として、antspynet.brain\_extractionは文書化もされており、優れた出発点となります 6。  
  Python  
  import ants  
  from antspynet.utilities import brain\_extraction

  def analyze\_image(image\_bytes):  
      \# バイトデータからANTsImageオブジェクトを読み込む  
      image \= ants.image\_read(image\_bytes, pixeltype='float')

      \# 脳抽出を実行（例）  
      probability\_mask \= brain\_extraction(image, modality="t1")  
      mask \= ants.threshold\_image(probability\_mask, 0.5, 1)

      \# 結果を辞書形式で返す  
      return {  
          "original\_image": image,  
          "segmentation\_mask": mask,  
          "probability\_mask": probability\_mask  
      }

* **戻り値:** 解析結果として、元の画像オブジェクト、生成されたセグメンテーションマスク、そして後段のレポート生成で利用可能な主要な座標や確率マップなどを辞書形式で返します。

#### **2.1.5. Geminiレポート生成モジュール (report\_generator.py)**

このモジュールは、画像解析の結果を基に、Gemini APIを利用して高度な解釈とレポート生成を行います。ユーザーが提示した複数の出力形式（座標、ヒートマップ、LLMによる文章）の要望に対し、単一の形式を選択するのではなく、それらの長所を組み合わせた包括的なソリューションを提供します。具体的には、視覚的なヒートマップ（確率マップ）と、Geminiが生成する構造化されたテキストサマリーを組み合わせます。これにより、ユーザーは所見を直感的に「見る」ことと、その文脈を詳細に「理解する」ことの両方が可能になり、臨床的に有用な情報を提供できます。

この実現には、Geminiの\*\*構造化出力（JSONモード）\*\*機能が極めて有効です。この機能により、モデルの応答を厳密に定義されたJSONスキーマに準拠させることができ、信頼性の高い機械可読な出力を得られます。Pythonでは、Pydanticモデルを使用することで、このJSONスキーマを直感的かつ堅牢に定義できます 12。

1. **Pydanticによる出力スキーマの定義:**  
   Python  
   from pydantic import BaseModel, Field  
   from typing import List, Optional

   class LesionFinding(BaseModel):  
       is\_finding\_present: bool \= Field(description="画像内に注目すべき所見が存在するかどうか。")  
       finding\_summary: Optional\[str\] \= Field(description="所見の簡潔な一行サマリー。所見がない場合はnull。")  
       detailed\_description: Optional\[str\] \= Field(description="画像とマスクに基づいた、病変の可能性のある領域の特徴に関する詳細な説明。所見がない場合はnull。")  
       confidence\_score: Optional\[float\] \= Field(description="これが有意な所見である可能性に関する0.0から1.0の信頼度スコア。所見がない場合はnull。")  
       anatomical\_location: Optional\[str\] \= Field(description="推定される解剖学的な位置（例：右前頭葉）。")

2. **レポート生成関数の実装:**  
   Python  
   import google.generativeai as genai  
   from PIL import Image  
   import io

   def generate\_structured\_report(original\_image, probability\_mask, api\_key):  
       genai.configure(api\_key=api\_key)

       \# ANTsImageをPillow Imageに変換  
       original\_pil \= Image.fromarray(original\_image.numpy().astype('uint8'))  
       mask\_pil \= Image.fromarray((probability\_mask.numpy() \* 255).astype('uint8'))

       \# モデルの設定  
       generation\_config \= genai.GenerationConfig(  
           response\_mime\_type="application/json",  
           response\_schema=LesionFinding,  
       )  
       model \= genai.GenerativeModel(  
           model\_name="gemini-1.5-pro-latest", \# あるいは gemini-pro-vision  
           generation\_config=generation\_config  
       )

       \# プロンプトの構築  
       prompt \= """  
       あなたは医療画像解析を支援するAIアシスタントです。  
       提供された2枚の画像を分析してください。1枚目は元のT1強調MRI画像、2枚目は病変の可能性がある領域を示す確率マップです。  
       この確率マップで値が高い（明るい）領域に注目し、以下の指示に従ってJSON形式でレポートを作成してください。  
       \- is\_finding\_present: 確率マップに有意な高信号領域があるか (true/false)  
       \- finding\_summary: ある場合、所見の簡潔なサマリーを記述  
       \- detailed\_description: ある場合、所見の位置、形状、信号強度などの特徴を詳細に記述  
       \- confidence\_score: 所見が実際に重要である可能性を0.0から1.0で評価  
       \- anatomical\_location: 推定される解剖学的部位を記述  
       もし有意な所見が見られない場合は、is\_finding\_presentをfalseとし、他のフィールドはnullとしてください。  
       """

       response \= model.generate\_content(\[prompt, original\_pil, mask\_pil\])

       \# Pydanticモデルにレスポンスをロードして検証  
       try:  
           report\_data \= LesionFinding.model\_validate\_json(response.text)  
           return report\_data  
       except Exception as e:  
           print(f"Error validating Gemini response: {e}")  
           return None

この実装により、Geminiからの応答は常に定義したLesionFindingクラスの構造に準拠することが保証されます。これにより、後続の処理が簡素化され、アプリケーション全体の安定性が向上します 19。

### **2.2. フェーズ2：本番環境グレードのコンテナ化**

このフェーズの核心は、ローカルで開発したアプリケーションを、移植性が高く、再現性があり、本番環境での実行に最適化されたDockerコンテナにパッケージ化することです。特にMLアプリケーションでは、巨大な事前学習済みモデルファイルの管理が重要な課題となります。モデルをコンテナ実行時にダウンロードする方式は、起動遅延、ネットワーク障害による失敗、余分なコストの原因となり、アプリケーションの信頼性を著しく損ないます 20。

これを解決するための最善のアプローチは、\*\*コンテナのビルドプロセス中にモデルをダウンロードし、イメージ内に含めてしまう（ベイキングする）\*\*ことです。これにより、実行環境のネットワーク状態に依存しない、自己完結した不変のアーティファクトが完成します。ANTsPyNetのようなライブラリは、通常、初回使用時にモデルを動的にダウンロードするため 20、Dockerfile内でこのダウンロードを明示的にトリガーする工夫が必要です。

この課題に対処するため、**マルチステージビルド**というDockerの高度な機能を利用します。この手法は、ビルド用の一時的なステージ（builder）と、最終的な本番用ステージ（final）を分離します。builderステージで依存関係のインストールやモデルのダウンロードといった時間のかかる「汚れる」作業を行い、finalステージではbuilderステージから必要な成果物（コンパイルされたライブラリやダウンロード済みモデルキャッシュなど）だけをコピーします。これにより、最終的なイメージサイズを劇的に削減し、セキュリティを向上させることができます 14。

#### **2.2.1. 最適化されたマルチステージDockerfile**

以下に、ANTsPyNetのモデルキャッシュ戦略を組み込んだ、本番環境グレードのDockerfileを示します。

Dockerfile

\# \===================================================================  
\# Stage 1: Builder  
\# 依存関係のインストールとモデルの事前キャッシュを行うステージ  
\# \===================================================================  
FROM python:3.11\-slim as builder

\# ビルド高速化のため、pipの代わりにuvを使用 \[23\]  
RUN pip install uv

WORKDIR /app

\# Dockerレイヤーキャッシュを有効活用するため、まずrequirements.txtのみをコピー \[16, 24\]  
COPY requirements.txt.

\# uvを使用して依存関係をインストール  
RUN uv pip install \--no-cache \-r requirements.txt

\# \---【重要】ANTsPyNetモデルの事前ダウンロード \---  
\# モデルダウンロードをトリガーするPythonスクリプトを作成  
\# ここでは'brainExtraction'モデルを例としてダウンロードする  
RUN echo "import antspynet; antspynet.utilities.get\_pretrained\_network('brainExtraction')" \> preload\_models.py

\# スクリプトを実行してキャッシュを生成する。  
\# デフォルトではキャッシュは /root/.antspynet/ に保存される  
RUN python preload\_models.py  
\# \---【重要】ステップ終了 \---

\# \===================================================================  
\# Stage 2: Final  
\# 最小限のコンポーネントで構成される軽量な本番イメージ  
\# \===================================================================  
FROM python:3.11\-slim

WORKDIR /app

\# セキュリティ向上のため、非rootユーザーを作成・使用する \[25\]  
RUN addgroup \--system appuser && adduser \--system \--no-create-home appuser  
USER appuser

\# builderステージから、インストール済みのライブラリと事前キャッシュ済みのモデルをコピー  
\# ANTsPyNetのキャッシュパスを非rootユーザーのホームディレクトリに合わせる  
COPY \--from=builder /app /app  
COPY \--from=builder /root/.antspynet /home/appuser/.antspynet

\# アプリケーションコードをコピー  
COPY \--chown=appuser:appuser modules/./modules/  
COPY \--chown=appuser:appuser pages/./pages/  
COPY \--chown=appuser:appuser app.py.

\# Streamlitが使用するポートを公開  
EXPOSE 8501

\# Cloud Run環境でStreamlitを正しく動作させるための環境変数  
ENV STREAMLIT\_SERVER\_PORT=8501  
ENV STREAMLIT\_SERVER\_HEADLESS=true  
ENV ANTSPYNET\_CACHE\_DIRECTORY=/home/appuser/.antspynet

\# アプリケーションの実行コマンド  
CMD \["streamlit", "run", "app.py"\]

#### **2.2.2. .dockerignoreファイル**

ビルドコンテキスト（Dockerデーモンに送られるファイル群）のサイズを小さく保ち、ビルドを高速化し、不要なファイルがイメージに含まれるのを防ぐために、.dockerignoreファイルを作成します 14。

\#.dockerignore  
.venv  
\_\_pycache\_\_/  
\*.pyc  
\*.pyo  
\*.pyd  
.Python  
.git  
.gitignore  
.dockerignore  
README.md

このDockerfileと.dockerignoreファイルを使用することで、docker buildコマンドを実行するだけで、軽量かつ自己完結した、本番環境に即したコンテナイメージを構築できます。

### **2.3. フェーズ3：セキュアでスケーラブルなクラウド展開**

この最終フェーズでは、フェーズ2で作成したコンテナイメージをGoogle Cloudにデプロイし、セキュリティとスケーラビリティを確保した公開アプリケーションとして完成させます。

#### **2.3.1. 事前準備**

Google Cloudプロジェクトで、Cloud Run API, Artifact Registry API, Cloud Build API, Secret Manager APIを有効化しておく必要があります。

#### **2.3.2. ステップ1：イメージをArtifact Registryにプッシュ**

Artifact Registryは、GCP内でDockerイメージを安全に管理するためのプライベートレジストリです。

1. **Docker認証の設定:**  
   Bash  
   gcloud auth configure-docker-docker.pkg.dev

2. **リポジトリの作成:**  
   Bash  
   gcloud artifacts repositories create mvp-repo \\  
       \--repository-format=docker \\  
       \--location= \\  
       \--description="Repository for medical MVP app"

3. **イメージのビルド、タグ付け、プッシュ:**  
   Bash  
   \# 変数設定  
   export PROJECT\_ID=$(gcloud config get-value project)  
   export REGION= \# 例: us-central1  
   export IMAGE\_URI=${REGION}\-docker.pkg.dev/${PROJECT\_ID}/mvp-repo/mvp-medical-analyzer:v1

   \# イメージのビルド  
   docker build \-t ${IMAGE\_URI}.

   \# イメージのプッシュ  
   docker push ${IMAGE\_URI}

#### **2.3.3. ステップ2：APIキーをSecret Managerに保存**

APIキーをコードやコンテナイメージに直接埋め込むのは非常に危険です。Google Cloud Secret Managerを使用して、安全に管理します。

Bash

echo \-n "YOUR\_GEMINI\_API\_KEY" | \\  
    gcloud secrets create gemini-api-key \--data-file=- \\  
    \--replication-policy="automatic"

#### **2.3.4. ステップ3：Cloud Runへのデプロイ**

以下のコマンドは、コスト、パフォーマンス、およびStreamlitアプリケーションのステートフルな性質を考慮した、ベストプラクティスに基づいています。

Bash

gcloud run deploy mvp-medical-analyzer \\  
    \--image=${IMAGE\_URI} \\  
    \--platform=managed \\  
    \--region=${REGION} \\  
    \--allow-unauthenticated \\  
    \--port=8501 \\  
    \--min-instances=0 \\  
    \--max-instances=2 \\  
    \--session-affinity \\  
    \--cpu-boost \\  
    \--memory=4Gi \\  
    \--cpu=2 \\  
    \--set-secrets=GEMINI\_API\_KEY=gemini-api-key:latest

\--allow-unauthenticatedフラグは、Cloud Runサービス自体への直接アクセスを許可しますが、次のステップで設定するIAPによって、最終的なアプリケーションへのアクセスは厳密に制御されます。

以下の表は、上記のデプロイコマンドで使用される主要なフラグとその推奨値、およびその正当性をまとめたものです。この設定は、研究で見られた一般的な問題（予期せぬ高コストやセッションの不安定さなど）を直接的に緩和するための、専門家による構成です 13。

| パラメータ | フラグ | 推奨値 | 正当化と主要な典拠 |
| :---- | :---- | :---- | :---- |
| **最小インスタンス** | \--min-instances | 0 | MVPのコスト削減に不可欠。アイドル時にインスタンスをゼロにスケールし、コストを最小化する。 4 |
| **最大インスタンス** | \--max-instances | 2 | 予期せぬスケーリングによるコストの急増を防ぐためのコスト管理策。 5 |
| **セッションアフィニティ** | \--session-affinity | true | ユーザーが同じコンテナインスタンスに接続し続けるようにする。Streamlitのステートフルな性質に有益。 13 |
| **CPUブースト** | \--cpu-boost | true | 起動時のCPU割り当てを増やし、コールドスタート時間を短縮してユーザー体験を向上させる。 13 |
| **メモリ** | \--memory | 4Gi | MLモデルには十分なメモリを割り当てる。監視し、必要に応じて調整する。 4 |
| **CPU** | \--cpu | 2 | ANTsPyNetはリソースを消費するため、2vCPUから開始する。 4 |
| **シークレット** | \--set-secrets | GEMINI\_API\_KEY=... | Secret Managerを使用してAPIキーを環境変数として安全に注入する。 |

#### **2.3.5. ステップ4：Identity-Aware Proxy (IAP)による保護**

IAPは、アプリケーションコードを変更することなく、HTTPSリクエストに対して一元的なアクセス制御を適用します。これにより、認証されていないユーザーがアプリケーションに到達するのを防ぎます。IAPはCloud Runサービスに直接適用するのではなく、その前段に配置するロードバランサを保護します 11。

1. **ロードバランサのセットアップ:** IAPを有効にするには、まず外部HTTPSロードバランサを作成し、Cloud Runサービスをバックエンドとして設定する必要があります。このプロセスは複数のgcloudコマンドを伴いますが、Google Cloudの公式ドキュメント 10 に詳細な手順が記載されています。  
2. **OAuth同意画面の設定:** GCPコンソールの「APIとサービス」 \-\> 「OAuth同意画面」で、アプリケーション名やサポートメールなどを設定します。ユーザータイプは「外部」を選択します 10。  
3. **OAuth認証情報（クライアントID）の作成:** 「APIとサービス」 \-\> 「認証情報」で、「認証情報を作成」 \-\> 「OAuthクライアントID」を選択します。アプリケーションの種類として「ウェブアプリケーション」を選び、名前を付けます。作成後、クライアントIDとクライアントシークレットを控えておきます 10。  
4. **IAPの有効化:**  
   * ロードバランサのバックエンドサービスに対して、先ほど取得したOAuth認証情報を用いてIAPを有効化します。  
     Bash  
     gcloud compute backend-services update \\  
         \--global \\  
         \--iap=enabled,oauth2-client-id=,oauth2-client-secret=

5. **アクセス権の付与:** GCPコンソールの「セキュリティ」 \-\> 「Identity-Aware Proxy」ページに移動します。対象のバックエンドサービスを選択し、「プリンシパルを追加」をクリックします。アクセスを許可したいユーザーのメールアドレスやGoogleグループを入力し、「Cloud IAP」 \-\> 「IAP-secured Web App User」のロールを付与します 10。

この設定により、IAPが全ての認証フローを処理するため、Streamlitアプリケーション自体にstreamlit-authenticatorのような認証ロジックを実装する必要は一切ありません。これにより、アプリケーションコードはシンプルに保たれ、アクセス管理はIAMに一元化され、よりセキュアでシームレスなユーザー体験が実現します。これは、IAPとアプリケーションレベルの認証が重複してユーザー体験を損なうという、よくある問題を回避するための正しいアーキテクチャパターンです 27。

### **2.4. 高度な推奨事項：CI/CDとコスト管理**

MVPのデプロイ後、運用の効率化と継続的な改善のために、以下の高度なプラクティスを導入することを推奨します。

#### **2.4.1. Cloud Buildによる継続的インテグレーション/デプロイメント（CI/CD）**

手動でのビルドとデプロイは、時間がかかり、ヒューマンエラーの原因となります。Cloud Buildを使用して、ソースコードの変更をトリガーに、ビルドからデプロイまでを自動化するパイプラインを構築します。

プロジェクトのルートにcloudbuild.yamlファイルを作成します。

YAML

\# cloudbuild.yaml  
steps:  
\# 1\. Dockerイメージをビルド  
\- name: 'gcr.io/cloud-builders/docker'  
  args:  
    \- 'build'  
    \- '-t'  
    \- '${\_REGION}-docker.pkg.dev/$PROJECT\_ID/mvp-repo/mvp-medical-analyzer:$COMMIT\_SHA'  
    \- '.'

\# 2\. イメージをArtifact Registryにプッシュ  
\- name: 'gcr.io/cloud-builders/docker'  
  args:  
    \- 'push'  
    \- '${\_REGION}-docker.pkg.dev/$PROJECT\_ID/mvp-repo/mvp-medical-analyzer:$COMMIT\_SHA'

\# 3\. Cloud Runにデプロイ  
\- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'  
  entrypoint: 'gcloud'  
  args:  
    \- 'run'  
    \- 'deploy'  
    \- 'mvp-medical-analyzer'  
    \- '--image'  
    \- '${\_REGION}-docker.pkg.dev/$PROJECT\_ID/mvp-repo/mvp-medical-analyzer:$COMMIT\_SHA'  
    \- '--region'  
    \- '${\_REGION}'  
    \- '--platform'  
    \- 'managed'  
    \- '--session-affinity' \# その他のフラグもここに追加

images:  
\- '${\_REGION}-docker.pkg.dev/$PROJECT\_ID/mvp-repo/mvp-medical-analyzer:$COMMIT\_SHA'

substitutions:  
  \_REGION: '' \# 例: us-central1

このファイルをGitHubリポジトリにプッシュし、GCPコンソールのCloud Buildで、このリポジトリの特定のブランチ（例：main）へのプッシュをトリガーとして設定します。これにより、プロフェッショナルなGitOpsワークフローが確立され、開発の速度と信頼性が向上します 1。

#### **2.4.2. 積極的なコスト管理**

クラウドコストは、注意深く管理しないと予期せず増大する可能性があります。

* **スケール・トゥ・ゼロの徹底:** Cloud Runの--min-instances=0設定は、MVPのコストを低く抑えるための最も重要な要素です 4。  
* **予算とアラートの設定:** GCPコンソールの「お支払い」セクションで、プロジェクトに対する**予算**を設定し、支出がしきい値（例：予算の50%, 90%）に達した際に通知する**アラート**を構成します。これにより、コストのサプライズを防ぎます 13。  
* **リソースの適正化:** **Cloud Monitoring**ダッシュボードを使用して、Cloud RunインスタンスのCPUおよびメモリ使用率を定期的に監視します。リソースが常に過剰または不足している場合は、デプロイ設定を更新してリソースを「適正化」し、コストとパフォーマンスのバランスを最適化します 28。  
* **無料枠の活用:** Cloud Runには寛大な**無料利用枠**が設定されています。トラフィックの少ないMVPでは、月々の利用料の大部分がこの無料枠でカバーされ、非常に低コスト（あるいは無料）で運用できる可能性があります 13。

## **結論と今後の展望**

本計画書は、Google Cloudの最新技術を活用して、医療画像解析MVPを迅速かつセキュアに開発・展開するための詳細なロードマップを提示しました。Streamlit、Cloud Run、ANTsPyNet、そしてGemini APIを組み合わせたアーキテクチャは、開発速度、スケーラビリティ、コスト効率、そして高度なAI機能の全ての要件を満たす、強力なソリューションです。

**主要な成功要因の要約:**

1. **段階的アプローチ:** ローカル開発からコンテナ化、クラウド展開へと進むことで、リスクを管理し、着実な進捗を保証します。  
2. **最適な技術選定:** Cloud Runのスケール・トゥ・ゼロ機能とIAPによる堅牢なセキュリティは、MVPに理想的な運用基盤を提供します。  
3. **専門的なコンテナ化戦略:** マルチステージビルドとMLモデルの事前キャッシュは、本番環境でのパフォーマンスと信頼性を確保するための鍵となります。  
4. **高度なAI活用:** ANTsPyNetによる専門的な画像解析と、Geminiの構造化出力機能による高度なレポート生成を組み合わせることで、単なる画像表示に留まらない、付加価値の高いユーザー体験を創出します。

本計画書に概説された手順とベストプラクティスに従うことで、技術的に洗練され、商業的に実行可能で、将来の機能拡張にも対応可能な基盤を持つMVPを構築することが可能です。次のステップは、フェーズ1に着手し、ローカル環境でのプロトタイピングを開始することです。

#### **引用文献**

1. \[Request\] Best Practices for Hosting Multiple Streamlit Dashboards (with Various Data Sources) on Kubernetes : r/StreamlitOfficial \- Reddit, 6月 22, 2025にアクセス、 [https://www.reddit.com/r/StreamlitOfficial/comments/1j5qe12/request\_best\_practices\_for\_hosting\_multiple/](https://www.reddit.com/r/StreamlitOfficial/comments/1j5qe12/request_best_practices_for_hosting_multiple/)  
2. Utilize the Streamlit Framework with Cloud Run and the Gemini API in Vertex AI, 6月 22, 2025にアクセス、 [https://www.cloudskillsboost.google/focuses/85991?parent=catalog](https://www.cloudskillsboost.google/focuses/85991?parent=catalog)  
3. How to deploy and secure your Streamlit app on GCP? \- Artefact, 6月 22, 2025にアクセス、 [https://www.artefact.com/blog/how-to-deploy-and-secure-your-streamlit-app-on-gcp/](https://www.artefact.com/blog/how-to-deploy-and-secure-your-streamlit-app-on-gcp/)  
4. Introducing my latest application, Docu Talk \- Show the Community\! \- Streamlit, 6月 22, 2025にアクセス、 [https://discuss.streamlit.io/t/introducing-my-latest-application-docu-talk/94704](https://discuss.streamlit.io/t/introducing-my-latest-application-docu-talk/94704)  
5. Deploying a streamlit app on cloud run \- dealing with data : r/googlecloud \- Reddit, 6月 22, 2025にアクセス、 [https://www.reddit.com/r/googlecloud/comments/1htj9dw/deploying\_a\_streamlit\_app\_on\_cloud\_run\_dealing/](https://www.reddit.com/r/googlecloud/comments/1htj9dw/deploying_a_streamlit_app_on_cloud_run_dealing/)  
6. ANTsX/ANTs: Advanced Normalization Tools (ANTs) \- GitHub, 6月 22, 2025にアクセス、 [https://github.com/ANTsX/ANTs](https://github.com/ANTsX/ANTs)  
7. ANTsX/ANTsPyNet: Pre-trained models and utilities for deep learning on medical images in Python \- GitHub, 6月 22, 2025にアクセス、 [https://github.com/ANTsX/ANTsPyNet](https://github.com/ANTsX/ANTsPyNet)  
8. Image understanding | Gemini API | Google AI for Developers, 6月 22, 2025にアクセス、 [https://ai.google.dev/gemini-api/docs/image-understanding](https://ai.google.dev/gemini-api/docs/image-understanding)  
9. Image understanding | Generative AI on Vertex AI \- Google Cloud, 6月 22, 2025にアクセス、 [https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-understanding](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-understanding)  
10. Step 4: Configure Identity-Aware Proxy (IAP) | Generative AI on ..., 6月 22, 2025にアクセス、 [https://cloud.google.com/vertex-ai/generative-ai/docs/streamlit/configure-iap](https://cloud.google.com/vertex-ai/generative-ai/docs/streamlit/configure-iap)  
11. Secure a generative AI app by using IAP | Generative AI on Vertex AI \- Google Cloud, 6月 22, 2025にアクセス、 [https://cloud.google.com/vertex-ai/generative-ai/docs/streamlit/streamlit-genai-iap](https://cloud.google.com/vertex-ai/generative-ai/docs/streamlit/streamlit-genai-iap)  
12. Structured output | Gemini API | Google AI for Developers, 6月 22, 2025にアクセス、 [https://ai.google.dev/gemini-api/docs/structured-output](https://ai.google.dev/gemini-api/docs/structured-output)  
13. Optimizing Costs for My Simple Streamlit App on Google Cloud Run : r/googlecloud \- Reddit, 6月 22, 2025にアクセス、 [https://www.reddit.com/r/googlecloud/comments/1jjvskp/optimizing\_costs\_for\_my\_simple\_streamlit\_app\_on/](https://www.reddit.com/r/googlecloud/comments/1jjvskp/optimizing_costs_for_my_simple_streamlit_app_on/)  
14. How to Reduce Docker Image Size: Best Practices and Tips for DevOps Engineers, 6月 22, 2025にアクセス、 [https://dev.to/prodevopsguytech/how-to-reduce-docker-image-size-best-practices-and-tips-for-devops-engineers-1ahg](https://dev.to/prodevopsguytech/how-to-reduce-docker-image-size-best-practices-and-tips-for-devops-engineers-1ahg)  
15. Manage your app \- Streamlit Docs, 6月 22, 2025にアクセス、 [https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)  
16. Docker Multi-Stage Builds for Python Developers: A Complete Guide \- Collabnix, 6月 22, 2025にアクセス、 [https://collabnix.com/docker-multi-stage-builds-for-python-developers-a-complete-guide/](https://collabnix.com/docker-multi-stage-builds-for-python-developers-a-complete-guide/)  
17. How to improve Streamlit app loading speed, 6月 22, 2025にアクセス、 [https://blog.streamlit.io/how-to-improve-streamlit-app-loading-speed/](https://blog.streamlit.io/how-to-improve-streamlit-app-loading-speed/)  
18. Getting Started with Google Generative AI Using the Gen AI SDK, 6月 22, 2025にアクセス、 [https://www.cloudskillsboost.google/focuses/86503?parent=catalog](https://www.cloudskillsboost.google/focuses/86503?parent=catalog)  
19. Generative AI on Vertex AI \- Structured output \- Google Cloud, 6月 22, 2025にアクセス、 [https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output)  
20. Complicated Dockerfile · Issue \#89 · ANTsX/ANTsPyNet \- GitHub, 6月 22, 2025にアクセス、 [https://github.com/ANTsX/ANTsPyNet/issues/89](https://github.com/ANTsX/ANTsPyNet/issues/89)  
21. README.md \- ftdc-picsl/antsnetct \- GitHub, 6月 22, 2025にアクセス、 [https://github.com/ftdc-picsl/antsnetct/blob/main/README.md](https://github.com/ftdc-picsl/antsnetct/blob/main/README.md)  
22. Multi-stage builds \- Docker Docs, 6月 22, 2025にアクセス、 [https://docs.docker.com/build/building/multi-stage/](https://docs.docker.com/build/building/multi-stage/)  
23. Multi-Stage Docker Builds for Python Projects using uv \- DEV Community, 6月 22, 2025にアクセス、 [https://dev.to/kummerer94/multi-stage-docker-builds-for-pyton-projects-using-uv-223g](https://dev.to/kummerer94/multi-stage-docker-builds-for-pyton-projects-using-uv-223g)  
24. Best Practices for Building Docker Images | Better Stack Community, 6月 22, 2025にアクセス、 [https://betterstack.com/community/guides/scaling-docker/docker-build-best-practices/](https://betterstack.com/community/guides/scaling-docker/docker-build-best-practices/)  
25. How to Dockerize Python Data Science Processes \- Rotational Labs, 6月 22, 2025にアクセス、 [https://rotational.io/blog/how-to-dockerize-data-science-processes/](https://rotational.io/blog/how-to-dockerize-data-science-processes/)  
26. How to configure an idle timeout for a Streamlit app deployed on GCP Cloud Run?, 6月 22, 2025にアクセス、 [https://discuss.streamlit.io/t/how-to-configure-an-idle-timeout-for-a-streamlit-app-deployed-on-gcp-cloud-run/89252](https://discuss.streamlit.io/t/how-to-configure-an-idle-timeout-for-a-streamlit-app-deployed-on-gcp-cloud-run/89252)  
27. How to Avoid Double Authentication for a Streamlit App on Cloud Run with IAP and Application-Level L, 6月 22, 2025にアクセス、 [https://www.googlecloudcommunity.com/gc/Serverless/How-to-Avoid-Double-Authentication-for-a-Streamlit-App-on-Cloud/m-p/861833/highlight/true](https://www.googlecloudcommunity.com/gc/Serverless/How-to-Avoid-Double-Authentication-for-a-Streamlit-App-on-Cloud/m-p/861833/highlight/true)  
28. Cost Optimization Tips for Running AI in Google Cloud \- Visualpath, 6月 22, 2025にアクセス、 [https://visualpathblogs.com/google-cloud-ai/cost-optimization-tips-for-running-ai-in-google-cloud/](https://visualpathblogs.com/google-cloud-ai/cost-optimization-tips-for-running-ai-in-google-cloud/)  
29. GCP Cost Optimization: 7 Best Practices | Edge Delta, 6月 22, 2025にアクセス、 [https://edgedelta.com/company/blog/gcp-cost-optimization](https://edgedelta.com/company/blog/gcp-cost-optimization)
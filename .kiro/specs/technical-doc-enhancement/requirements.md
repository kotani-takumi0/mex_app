# Requirements Document

## Introduction
AI コーディングツールを使う開発者の多くは、「ログイン機能を作って」のように機能レベルで指示を出す。AI は JWT、bcrypt、ミドルウェア等の技術を選択して実装するが、実装者はそれらの技術が何であり、なぜ必要なのかを理解していないケースが多い。現在の `/document` スキルが生成する Notion ドキュメントは「概要・技術的ポイント・使用技術・コード例」という作業報告形式であり、実装者の技術理解を促進する構造になっていない。

本機能拡張では、Notion ドキュメントの構造を「機能→技術分解→各技術の解説→想定Q&A」の階層構造に変更し、ドキュメントを読み進めるだけで自然に理解が深まる構造にする。専門用語は減らさず、用語を理解せざるを得ない文脈で提示することで、上司や面接官からの技術的な質問に答えられる水準の理解を目指す。

## Requirements

### Requirement 1: 実装サマリー（機能レベルの記述）
**Objective:** As a **AI実装ユーザー**, I want **自分が指示した機能レベルの内容と、それに対してAIが何を構築したかの概要を確認できること**, so that **技術詳細に入る前に全体像を把握できる**。

#### Acceptance Criteria
1. When [ドキュメント生成が開始された], the [Document Generator] shall [ユーザーが出した機能レベルの指示（例：「ログイン機能を実装して」）を冒頭に明記する]。
2. The [Document Generator] shall [AIが構築した機能の概要を、技術用語を最小限に抑えた1〜3文で要約する]。
3. The [Document Generator] shall [git diff および git log から実装の変更範囲（変更ファイル数、追加行数等）を自動取得し、実装規模の概要を含める]。

### Requirement 2: 技術分解（機能を実現する技術要素の一覧）
**Objective:** As a **AI実装ユーザー**, I want **自分が指示した機能を実現するためにAIがどのような技術要素を組み合わせたかの分解図を確認できること**, so that **「ログイン機能」の裏側にある技術構成を構造的に把握できる**。

#### Acceptance Criteria
1. When [実装サマリーが生成された後], the [Document Generator] shall [その機能を実現するために必要な技術要素を分解し、箇条書きで列挙する]。
2. The [Document Generator] shall [各技術要素に対して、その要素が機能全体の中でどの役割を担っているかを1文で示す（例：「bcrypt — パスワードを安全に保存するための暗号化処理」）]。
3. The [Document Generator] shall [技術要素間の依存関係や処理の流れが分かるよう、論理的な順序（例：入力→検証→保存→応答）で並べる]。

### Requirement 3: 各技術要素の解説（段階的な理解構造）
**Objective:** As a **AI実装ユーザー**, I want **各技術要素について「それは何か→なぜ必要か→他の選択肢→壊れたらどうなるか」の順で解説されること**, so that **専門用語を読み進めるだけで基礎から応用まで自然に理解が積み上がる**。

#### Acceptance Criteria
1. The [Document Generator] shall [Requirement 2 で列挙した各技術要素に対して、以下の4段階の解説を生成する：(a) それは何か — 技術の定義と概要、(b) なぜ必要か — この機能においてその技術が不可欠な理由、(c) 他の選択肢 — 代替技術とそれを選ばなかった理由、(d) 壊れたらどうなるか — その技術要素が欠落・故障した場合の具体的な影響]。
2. The [Document Generator] shall [各解説で専門用語が初出する際、その用語を平易な表現に置き換えず、文脈から意味が理解できる説明を付与する]。
3. The [Document Generator] shall [解説の深さを技術要素の重要度に応じて調整する（コア技術は詳細に、補助的な技術は簡潔に）]。

### Requirement 4: 想定Q&A（上司・面接官からの質問形式）
**Objective:** As a **AI実装ユーザー**, I want **上司や面接官から聞かれそうな質問とその回答例が、基礎→判断→応用の3段階で整理されていること**, so that **第三者からの技術的な質問に自信を持って答えられるよう準備できる**。

#### Acceptance Criteria
1. The [Document Generator] shall [実装内容に基づき、以下の3段階でQ&Aを生成する：(a) 基礎 — 使用技術の「そもそも何？」レベルの質問（例：「JWTとは何ですか？」）、(b) 判断 — 設計・技術選定の理由を問う質問（例：「なぜセッション方式ではなくJWTを選んだのですか？」）、(c) 応用 — エッジケース・障害時・スケール時の対応を問う質問（例：「トークンが漏洩した場合、どう対処しますか？」）]。
2. The [Document Generator] shall [各段階で最低2問、合計6問以上のQ&Aを生成する]。
3. The [Document Generator] shall [回答例を提示するが、回答をそのまま暗記するのではなく理解して自分の言葉で説明できるよう、回答の構造（結論→理由→具体例）を明示する]。
4. If [実装に重大なセキュリティ上の技術要素が含まれる場合（認証、暗号化、アクセス制御等）], the [Document Generator] shall [セキュリティに関する質問を最低1問追加する]。

### Requirement 5: Notion ドキュメント構造の統合
**Objective:** As a **AI実装ユーザー**, I want **上記の全セクションが1つのNotionページに階層的に構成されること**, so that **ドキュメントを上から順に読み進めるだけで理解が深まる体験が得られる**。

#### Acceptance Criteria
1. The [Document Generator] shall [Notionページを以下の順序で構成する：(1) 実装サマリー、(2) 技術分解、(3) 各技術要素の解説、(4) 想定Q&A]。
2. The [Document Generator] shall [各セクションをNotionの見出しブロック（H2/H3）で区切り、目次として機能する構造にする]。
3. The [Document Generator] shall [現行の `/document` スキルのワークフロー（git情報収集→プロジェクト解決→Notion作成→MEX App記録）を維持し、ドキュメント構造のみを変更する]。
4. The [Document Generator] shall [MEX App への記録時、`save_document` の既存パラメータ（title, category, technologies, source_url）を引き続き使用し、バックエンドAPIの変更を不要にする]。

### Requirement 6: ドキュメント品質の担保
**Objective:** As a **AI実装ユーザー**, I want **生成されるドキュメントの内容が実装の実態に即しており、汎用的な解説のコピーではないこと**, so that **自分のコードに対する具体的な理解が得られる**。

#### Acceptance Criteria
1. The [Document Generator] shall [git diff の実際の変更内容に基づいて技術分解と解説を生成し、汎用的・テンプレート的な説明のみにならないようにする]。
2. The [Document Generator] shall [Q&Aの質問を、実装したコードの具体的な設計判断に紐づけて生成する（例：一般的な「JWTとは？」だけでなく「あなたの実装でトークンの有効期限を60分に設定した理由は？」を含む）]。
3. While [技術要素の解説を生成している間], the [Document Generator] shall [実装コードから具体的な設定値、ライブラリ名、関数名を引用し、解説の具体性を確保する]。

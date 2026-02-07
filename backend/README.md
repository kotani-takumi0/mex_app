# MEX App Backend

企画立案OS - 過去の意思決定ログを活用した企画支援システム

## セットアップ

```bash
pip install -e ".[dev]"
```

## 開発サーバー起動

```bash
uvicorn app.main:app --reload
```

## テスト実行

```bash
pytest
```

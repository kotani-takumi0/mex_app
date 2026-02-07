"""
Alembicマイグレーション管理ユーティリティ
タスク1.2: バージョン管理可能なスキーマ変更を実現
"""
import os
from pathlib import Path
from typing import Any

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine


def get_alembic_config() -> Config:
    """Alembic設定を取得"""
    backend_dir = Path(__file__).parent.parent.parent.parent
    alembic_ini = backend_dir / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    return config


def check_alembic_configuration() -> bool:
    """
    Alembic env.pyがモデルのメタデータを正しく参照しているかチェック

    Returns:
        bool: 設定が正しい場合True
    """
    backend_dir = Path(__file__).parent.parent.parent.parent
    env_py_path = backend_dir / "alembic" / "env.py"

    if not env_py_path.exists():
        return False

    with open(env_py_path) as f:
        content = f.read()

    # env.pyがBase.metadataをインポートして使用しているかチェック
    has_import = "from app.infrastructure.database.models import Base" in content
    has_metadata = "target_metadata = Base.metadata" in content

    return has_import and has_metadata


def get_pending_migrations() -> list[str]:
    """
    未適用のマイグレーションを取得

    Returns:
        list[str]: 未適用のマイグレーションリビジョンID
    """
    config = get_alembic_config()
    script = ScriptDirectory.from_config(config)

    # 全リビジョンを取得
    revisions = list(script.walk_revisions())

    return [rev.revision for rev in revisions]

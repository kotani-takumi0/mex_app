"""
設定モジュールのテスト
"""


class TestSettings:
    """設定クラスのテスト"""

    def test_settings_can_be_instantiated(self):
        """設定クラスがインスタンス化できる"""
        from app.config import Settings

        settings = Settings()
        assert settings is not None

    def test_settings_has_default_values(self):
        """デフォルト値が設定されている"""
        from app.config import Settings

        settings = Settings()
        assert settings.app_env == "development"
        assert settings.debug is True

    def test_get_settings_returns_singleton(self):
        """get_settingsがシングルトンを返す"""
        from app.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

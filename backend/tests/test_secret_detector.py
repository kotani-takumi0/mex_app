"""
シークレット検出・マスキングのテスト

開発ログに含まれるAPIキー等のシークレットを検出し、
マスキングする機能のユニットテスト。
"""

import pytest

from app.domain.security.secret_detector import SecretDetector, get_secret_detector


class TestSecretDetector:
    """SecretDetectorのテスト"""

    @pytest.fixture
    def detector(self):
        return SecretDetector()

    # --- OpenAI API Key ---

    def test_detect_openai_key(self, detector):
        """OpenAI APIキーを検出"""
        text = "OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678"
        matches = detector.detect(text)
        assert any(m.pattern_name == "openai_api_key" for m in matches)

    def test_mask_openai_key(self, detector):
        """OpenAI APIキーをマスキング"""
        text = "key: sk-proj-abc123def456ghi789jkl012mno345pqr678"
        result = detector.mask(text)
        assert "sk-proj" not in result
        assert "***OPENAI_KEY***" in result

    # --- AWS Keys ---

    def test_detect_aws_access_key(self, detector):
        """AWS Access Key IDを検出"""
        text = "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE"
        matches = detector.detect(text)
        assert any(m.pattern_name == "aws_access_key" for m in matches)

    def test_mask_aws_access_key(self, detector):
        """AWS Access Key IDをマスキング"""
        text = "key=AKIAIOSFODNN7EXAMPLE"
        result = detector.mask(text)
        assert "AKIA" not in result

    # --- GitHub Token ---

    def test_detect_github_token(self, detector):
        """GitHub Personal Access Tokenを検出"""
        text = "token: ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklm"
        matches = detector.detect(text)
        assert any(m.pattern_name == "github_token" for m in matches)

    # --- Private Key ---

    def test_detect_private_key(self, detector):
        """秘密鍵を検出"""
        text = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS...
-----END RSA PRIVATE KEY-----"""
        matches = detector.detect(text)
        assert any(m.pattern_name == "private_key" for m in matches)

    def test_mask_private_key(self, detector):
        """秘密鍵をマスキング"""
        text = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS...
-----END RSA PRIVATE KEY-----"""
        result = detector.mask(text)
        assert "BEGIN" not in result
        assert "***PRIVATE_KEY***" in result

    # --- Database URLs ---

    def test_detect_database_url(self, detector):
        """DB接続URLを検出"""
        text = "DATABASE_URL=postgresql://admin:secret_password@db.example.com:5432/mydb"
        matches = detector.detect(text)
        assert any(m.pattern_name == "database_url" for m in matches)

    # --- Password ---

    def test_detect_password(self, detector):
        """パスワードを検出"""
        text = "password=my_super_secret_pass123"
        matches = detector.detect(text)
        assert any(m.pattern_name == "password" for m in matches)

    def test_detect_password_colon(self, detector):
        """パスワード(コロン形式)を検出"""
        text = "password: 'my_super_secret_pass123'"
        matches = detector.detect(text)
        assert any(m.pattern_name == "password" for m in matches)

    # --- Stripe Keys ---

    def test_detect_stripe_key(self, detector):
        """Stripeキーを検出"""
        text = "STRIPE_KEY=STRIPE_TEST_SECRET_KEY_PLACEHOLDER"
        matches = detector.detect(text)
        assert any(m.pattern_name == "stripe_key" for m in matches)

    # --- JWT Token ---

    def test_detect_jwt_token(self, detector):
        """JWTトークンを検出"""
        text = "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        matches = detector.detect(text)
        assert any(m.pattern_name == "jwt_token" for m in matches)

    # --- Generic API Key ---

    def test_detect_generic_api_key(self, detector):
        """汎用APIキーを検出"""
        text = "api_key=abcdef1234567890abcdef1234567890"
        matches = detector.detect(text)
        assert any(m.pattern_name == "generic_api_key" for m in matches)

    # --- No False Positives ---

    def test_no_false_positive_on_normal_text(self, detector):
        """通常のテキストでは検出されない"""
        text = "React RouterのuseNavigateフックを使ってページ遷移を実装しました"
        matches = detector.detect(text)
        assert len(matches) == 0

    def test_no_false_positive_on_code_snippet(self, detector):
        """コードスニペットでは誤検出しない"""
        text = "const handleClick = () => { navigate('/dashboard'); }"
        matches = detector.detect(text)
        assert len(matches) == 0

    # --- has_secrets ---

    def test_has_secrets_true(self, detector):
        """シークレットが含まれる場合True"""
        assert detector.has_secrets("key: sk-proj-abc123def456ghi789jkl012mno345pqr678")

    def test_has_secrets_false(self, detector):
        """シークレットが含まれない場合False"""
        assert not detector.has_secrets("普通のテキストです")

    # --- Empty/None ---

    def test_detect_empty_string(self, detector):
        """空文字列は空リスト"""
        assert detector.detect("") == []

    def test_mask_empty_string(self, detector):
        """空文字列はそのまま返す"""
        assert detector.mask("") == ""

    # --- Singleton ---

    def test_get_secret_detector_singleton(self):
        """シングルトンが返される"""
        d1 = get_secret_detector()
        d2 = get_secret_detector()
        assert d1 is d2

    # --- Multiple secrets in one text ---

    def test_mask_multiple_secrets(self, detector):
        """複数のシークレットを同時にマスキング"""
        text = (
            "OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678\n"
            "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n"
            "password=my_secret_pass"
        )
        result = detector.mask(text)
        assert "sk-proj" not in result
        assert "AKIA" not in result
        assert "my_secret_pass" not in result

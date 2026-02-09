"""
シークレット検出・マスキングサービス

開発ログに含まれるAPIキー、AWSキー、秘密鍵、パスワード等を
正規表現で検出し、マスキングする。

3つのAIレビューすべてが「開発ログへのシークレット漏洩」を
Critical Issueとして指摘したため実装。
"""
import re
from dataclasses import dataclass


@dataclass
class SecretMatch:
    """検出されたシークレット"""
    pattern_name: str
    original: str
    masked: str
    start: int
    end: int


# 検出パターン定義
# (パターン名, 正規表現, マスク文字列)
_SECRET_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    # OpenAI API Key
    (
        "openai_api_key",
        re.compile(r"sk-[a-zA-Z0-9_-]{20,}"),
        "***OPENAI_KEY***",
    ),
    # AWS Access Key ID
    (
        "aws_access_key",
        re.compile(r"AKIA[0-9A-Z]{16}"),
        "***AWS_KEY***",
    ),
    # AWS Secret Access Key (40 chars, base64-like)
    (
        "aws_secret_key",
        re.compile(r"(?<=[^a-zA-Z0-9/+=])[a-zA-Z0-9/+=]{40}(?=[^a-zA-Z0-9/+=]|$)"),
        "***AWS_SECRET***",
    ),
    # GitHub Personal Access Token
    (
        "github_token",
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}"),
        "***GITHUB_TOKEN***",
    ),
    # Generic API Key patterns (key=..., api_key=..., apikey=...)
    (
        "generic_api_key",
        re.compile(r"(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-./+=]{16,})['\"]?", re.IGNORECASE),
        "***API_KEY***",
    ),
    # Password patterns (password=..., passwd=...)
    (
        "password",
        re.compile(r"(?:password|passwd|pwd)\s*[:=]\s*['\"]?(\S{4,})['\"]?", re.IGNORECASE),
        "***PASSWORD***",
    ),
    # Private Key blocks
    (
        "private_key",
        re.compile(r"-----BEGIN\s+(?:RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE\s+KEY-----"),
        "***PRIVATE_KEY***",
    ),
    # Database URLs with credentials
    (
        "database_url",
        re.compile(r"(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^@\s]+@[^\s]+"),
        "***DATABASE_URL***",
    ),
    # JWT tokens (3 base64 segments separated by dots)
    (
        "jwt_token",
        re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"),
        "***JWT_TOKEN***",
    ),
    # Stripe keys
    (
        "stripe_key",
        re.compile(r"(?:sk|pk|rk)_(?:test|live)_[a-zA-Z0-9]{20,}"),
        "***STRIPE_KEY***",
    ),
    # Slack tokens
    (
        "slack_token",
        re.compile(r"xox[baprs]-[a-zA-Z0-9-]{10,}"),
        "***SLACK_TOKEN***",
    ),
]


class SecretDetector:
    """
    シークレット検出・マスキングサービス

    開発ログのテキストをスキャンし、APIキー等のシークレットを
    検出してマスキングする。
    """

    def __init__(self, patterns: list[tuple[str, re.Pattern, str]] | None = None):
        self._patterns = patterns or _SECRET_PATTERNS

    def detect(self, text: str) -> list[SecretMatch]:
        """
        テキスト内のシークレットを検出する。

        Args:
            text: スキャン対象のテキスト

        Returns:
            検出されたシークレットのリスト
        """
        if not text:
            return []

        matches: list[SecretMatch] = []
        for pattern_name, regex, mask in self._patterns:
            for match in regex.finditer(text):
                matches.append(SecretMatch(
                    pattern_name=pattern_name,
                    original=match.group(0),
                    masked=mask,
                    start=match.start(),
                    end=match.end(),
                ))

        return matches

    def mask(self, text: str) -> str:
        """
        テキスト内のシークレットをマスキングする。

        Args:
            text: マスキング対象のテキスト

        Returns:
            マスキング後のテキスト
        """
        if not text:
            return text

        result = text
        for pattern_name, regex, mask in self._patterns:
            result = regex.sub(mask, result)

        return result

    def has_secrets(self, text: str) -> bool:
        """テキストにシークレットが含まれるかチェック"""
        return len(self.detect(text)) > 0


# シングルトンインスタンス
_detector: SecretDetector | None = None


def get_secret_detector() -> SecretDetector:
    """SecretDetectorのシングルトンインスタンスを取得"""
    global _detector
    if _detector is None:
        _detector = SecretDetector()
    return _detector

"""
TDD: シードデータ投入のテスト
タスク6.2: サンプルデータ投入とコールドスタート対応
"""


class TestFailurePatternTagsMaster:
    """失敗パターンタグマスターデータのテスト"""

    def test_master_tags_exist(self):
        """マスターデータが存在する"""
        from app.seeds.failure_patterns import MASTER_FAILURE_PATTERNS

        assert len(MASTER_FAILURE_PATTERNS) > 0

    def test_master_tags_have_required_fields(self):
        """マスターデータに必須フィールドがある"""
        from app.seeds.failure_patterns import MASTER_FAILURE_PATTERNS

        for tag in MASTER_FAILURE_PATTERNS:
            assert "name" in tag
            assert "description" in tag
            assert "category" in tag

    def test_master_tags_include_financial(self):
        """財務カテゴリが含まれる"""
        from app.seeds.failure_patterns import MASTER_FAILURE_PATTERNS

        categories = [tag["category"] for tag in MASTER_FAILURE_PATTERNS]
        assert "financial" in categories

    def test_master_tags_include_operational(self):
        """オペレーションカテゴリが含まれる"""
        from app.seeds.failure_patterns import MASTER_FAILURE_PATTERNS

        categories = [tag["category"] for tag in MASTER_FAILURE_PATTERNS]
        assert "operational" in categories

    def test_master_tags_include_market(self):
        """市場カテゴリが含まれる"""
        from app.seeds.failure_patterns import MASTER_FAILURE_PATTERNS

        categories = [tag["category"] for tag in MASTER_FAILURE_PATTERNS]
        assert "market" in categories

    def test_master_tags_include_technical(self):
        """技術カテゴリが含まれる"""
        from app.seeds.failure_patterns import MASTER_FAILURE_PATTERNS

        categories = [tag["category"] for tag in MASTER_FAILURE_PATTERNS]
        assert "technical" in categories

    def test_master_tags_include_organizational(self):
        """組織カテゴリが含まれる"""
        from app.seeds.failure_patterns import MASTER_FAILURE_PATTERNS

        categories = [tag["category"] for tag in MASTER_FAILURE_PATTERNS]
        assert "organizational" in categories


class TestSampleDecisionCases:
    """サンプル意思決定ケースのテスト"""

    def test_sample_cases_exist(self):
        """サンプルケースが存在する"""
        from app.seeds.decision_cases import SAMPLE_DECISION_CASES

        assert len(SAMPLE_DECISION_CASES) > 0

    def test_sample_cases_have_required_fields(self):
        """サンプルケースに必須フィールドがある"""
        from app.seeds.decision_cases import SAMPLE_DECISION_CASES

        for case in SAMPLE_DECISION_CASES:
            assert "title" in case
            assert "purpose" in case
            assert "target_market" in case
            assert "business_model" in case
            assert "outcome" in case
            assert "decision_type" in case
            assert "decision_reason" in case

    def test_sample_cases_include_adopted(self):
        """採用案が含まれる"""
        from app.seeds.decision_cases import SAMPLE_DECISION_CASES

        outcomes = [case["outcome"] for case in SAMPLE_DECISION_CASES]
        assert "adopted" in outcomes

    def test_sample_cases_include_rejected(self):
        """却下案が含まれる"""
        from app.seeds.decision_cases import SAMPLE_DECISION_CASES

        outcomes = [case["outcome"] for case in SAMPLE_DECISION_CASES]
        assert "rejected" in outcomes

    def test_sample_cases_include_withdrawn(self):
        """撤退案が含まれる"""
        from app.seeds.decision_cases import SAMPLE_DECISION_CASES

        outcomes = [case["outcome"] for case in SAMPLE_DECISION_CASES]
        assert "withdrawn" in outcomes

    def test_sample_cases_have_variety(self):
        """複数のケースがある（最低5件）"""
        from app.seeds.decision_cases import SAMPLE_DECISION_CASES

        assert len(SAMPLE_DECISION_CASES) >= 5


class TestSeedDataLoader:
    """シードデータローダーのテスト"""

    def test_seed_loader_exists(self):
        """シードローダーが存在する"""
        from app.seeds.loader import SeedDataLoader

        assert SeedDataLoader is not None

    def test_seed_loader_has_load_patterns_method(self):
        """失敗パターン読み込みメソッドがある"""
        from app.seeds.loader import SeedDataLoader

        loader = SeedDataLoader()
        assert hasattr(loader, "load_failure_patterns")

    def test_seed_loader_has_load_cases_method(self):
        """ケース読み込みメソッドがある"""
        from app.seeds.loader import SeedDataLoader

        loader = SeedDataLoader()
        assert hasattr(loader, "load_decision_cases")


class TestColdStartFallback:
    """コールドスタート対応のテスト"""

    def test_empty_results_message(self):
        """データが少ない場合のメッセージ"""
        from app.seeds.fallback import get_empty_results_message

        message = get_empty_results_message("similar_cases")
        assert isinstance(message, str)
        assert len(message) > 0

    def test_fallback_similar_cases(self):
        """類似ケースのフォールバック"""
        from app.seeds.fallback import get_fallback_similar_cases

        cases = get_fallback_similar_cases()
        assert isinstance(cases, list)

    def test_fallback_questions(self):
        """問いのフォールバック"""
        from app.seeds.fallback import get_fallback_questions

        questions = get_fallback_questions()
        assert isinstance(questions, list)
        assert len(questions) > 0

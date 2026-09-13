import json
import os
import pytest

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "golden_legal_qa.json")


def load_golden_dataset():
    """Load the reference golden legal QA dataset."""
    assert os.path.exists(DATA_FILE), f"Golden dataset file not found at {DATA_FILE}"
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_golden_dataset_structure_and_completeness():
    """Verify that the golden legal dataset has a complete, valid schema structure."""
    data = load_golden_dataset()
    assert len(data) >= 15, "Golden dataset must contain at least 15 test cases."

    in_scope_count = 0
    out_of_scope_count = 0

    for item in data:
        assert "id" in item
        assert "query" in item
        assert "expected_keywords" in item
        assert "is_in_scope" in item
        assert len(item["expected_keywords"]) > 0

        if item["is_in_scope"]:
            in_scope_count += 1
            assert (
                item["target_pasal"] is not None
            ), f"In-scope item {item['id']} must specify target_pasal"
        else:
            out_of_scope_count += 1

    assert in_scope_count >= 10, "Dataset must include at least 10 in-scope statutory questions."
    assert (
        out_of_scope_count >= 2
    ), "Dataset must include at least 2 out-of-scope questions for hallucination testing."


def test_anti_hallucination_refusal_detection():
    """Verify refusal detection logic for queries that fall outside statutory scope."""
    sample_refusal_response = (
        "Information regarding severance pay is not contained in Law No. 22 of 2009."
    )
    sample_hallucinated_response = (
        "Under current regulations, employee severance pay equals 9 months of base salary."
    )

    def is_valid_refusal(text: str) -> bool:
        lower = text.lower()
        refusal_triggers = [
            "not contained",
            "not found",
            "not present",
            "not available",
            "do not know",
            "strictly based",
            "tidak terdapat",
            "tidak ada",
            "tidak ditemukan",
        ]
        return any(trigger in lower for trigger in refusal_triggers)

    assert is_valid_refusal(sample_refusal_response) is True
    assert is_valid_refusal(sample_hallucinated_response) is False


def test_legal_citation_matching():
    """Verify citation matching logic against specified statutory articles."""
    sample_legal_answer = (
        "Under Article 281 of Law No. 22 of 2009, anyone operating a motor vehicle "
        "on the road without a valid driver's license shall be punished with imprisonment or fine."
    )

    def verify_target_article(answer: str, target: str) -> bool:
        return target.lower() in answer.lower()

    assert verify_target_article(sample_legal_answer, "Article 281") is True
    assert verify_target_article(sample_legal_answer, "Article 312") is False


def test_keyword_coverage_calculation():
    """Verify keyword recall scoring calculation across anticipated terms."""
    answer = (
        "The sanction is imprisonment for up to 4 months or a maximum fine of Rp1,000,000."
    )
    expected_keywords = ["imprisonment", "4 months", "1,000,000", "fine"]

    matched = [kw for kw in expected_keywords if kw.lower() in answer.lower()]
    score = len(matched) / len(expected_keywords)

    assert score == 1.0  # 100% keyword coverage

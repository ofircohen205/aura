"""
Tests for evaluation pipeline.
"""

import pytest

from agentic_py.ai.evaluation import (
    EvaluationMetrics,
    EvaluationPipeline,
    evaluate_chunking_strategy,
)


def test_evaluation_metrics_precision():
    """Test precision calculation."""
    metrics = EvaluationMetrics()
    metrics.true_positives = 10
    metrics.false_positives = 2

    assert metrics.precision == 10 / 12
    assert metrics.precision == pytest.approx(0.833, abs=0.001)


def test_evaluation_metrics_recall():
    """Test recall calculation."""
    metrics = EvaluationMetrics()
    metrics.true_positives = 10
    metrics.false_negatives = 3

    assert metrics.recall == 10 / 13
    assert metrics.recall == pytest.approx(0.769, abs=0.001)


def test_evaluation_metrics_f1_score():
    """Test F1 score calculation."""
    metrics = EvaluationMetrics()
    metrics.true_positives = 10
    metrics.false_positives = 2
    metrics.false_negatives = 3

    prec = metrics.precision
    rec = metrics.recall
    expected_f1 = 2 * (prec * rec) / (prec + rec)

    assert metrics.f1_score == pytest.approx(expected_f1, abs=0.001)


def test_evaluation_metrics_accuracy():
    """Test accuracy calculation."""
    metrics = EvaluationMetrics()
    metrics.true_positives = 10
    metrics.false_positives = 2
    metrics.false_negatives = 3
    metrics.true_negatives = 5

    total = 10 + 2 + 3 + 5
    expected_accuracy = (10 + 5) / total

    assert metrics.accuracy == pytest.approx(expected_accuracy, abs=0.001)


def test_evaluation_metrics_to_dict():
    """Test metrics conversion to dictionary."""
    metrics = EvaluationMetrics()
    metrics.true_positives = 10
    metrics.false_positives = 2

    result = metrics.to_dict()

    assert result["true_positives"] == 10
    assert result["false_positives"] == 2
    assert "precision" in result
    assert "recall" in result
    assert "f1_score" in result
    assert "accuracy" in result


def test_evaluation_pipeline_init():
    """Test evaluation pipeline initialization."""
    pipeline = EvaluationPipeline()

    assert pipeline.dataset_path is None
    assert pipeline.dataset == []


def test_evaluation_pipeline_load_dataset_nonexistent():
    """Test loading nonexistent dataset."""
    pipeline = EvaluationPipeline(dataset_path="/nonexistent/path.json")
    pipeline.load_dataset()

    assert pipeline.dataset == []


def test_evaluation_metrics_zero_division():
    """Test metrics handle zero division gracefully."""
    metrics = EvaluationMetrics()

    # All zeros should return 0.0, not raise error
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1_score == 0.0
    assert metrics.accuracy == 0.0


def test_evaluate_chunking_strategy():
    """Test chunking strategy evaluation raises NotImplementedError."""
    with pytest.raises(NotImplementedError, match="evaluate_chunking_strategy"):
        evaluate_chunking_strategy(
            strategy="recursive",
            chunk_size=1000,
            chunk_overlap=200,
            test_documents=["Test document 1", "Test document 2"],
        )

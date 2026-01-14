"""
Tests for LLM utility functions and error handling.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core_py.ml.llm import get_llm_client, invoke_llm_with_retry


@pytest.mark.asyncio
async def test_get_llm_client_disabled():
    """Test get_llm_client when LLM is disabled."""
    with patch.dict(os.environ, {"LLM_ENABLED": "false"}):
        with patch("core_py.ml.llm.LLM_ENABLED", False):
            client = await get_llm_client()
            assert client is None


@pytest.mark.asyncio
async def test_get_llm_client_enabled():
    """Test get_llm_client when LLM is enabled."""
    with patch.dict(os.environ, {"LLM_ENABLED": "true"}):
        with patch("core_py.ml.llm.LLM_ENABLED", True):
            with patch("langchain_openai.ChatOpenAI") as mock_llm:
                mock_instance = MagicMock()
                mock_llm.return_value = mock_instance

                client = await get_llm_client()
                assert client is not None
                mock_llm.assert_called_once()


@pytest.mark.asyncio
async def test_get_llm_client_import_error():
    """Test get_llm_client when langchain_openai is not installed."""
    with patch.dict(os.environ, {"LLM_ENABLED": "true"}):
        with patch("core_py.ml.llm.LLM_ENABLED", True):
            with patch(
                "builtins.__import__", side_effect=ImportError("No module named langchain_openai")
            ):
                with pytest.raises(ImportError, match="langchain-openai"):
                    await get_llm_client()


@pytest.mark.asyncio
async def test_invoke_llm_with_retry_disabled():
    """Test invoke_llm_with_retry when LLM is disabled."""
    with patch("core_py.ml.llm.LLM_ENABLED", False):
        with pytest.raises(RuntimeError, match="LLM is disabled"):
            await invoke_llm_with_retry("test prompt")


@pytest.mark.asyncio
async def test_invoke_llm_with_retry_empty_prompt():
    """Test invoke_llm_with_retry with empty prompt."""
    with patch("core_py.ml.llm.LLM_ENABLED", True):
        with pytest.raises(ValueError, match="cannot be empty"):
            await invoke_llm_with_retry("")


@pytest.mark.asyncio
async def test_invoke_llm_with_retry_success():
    """Test successful LLM invocation."""
    with patch("core_py.ml.llm.LLM_ENABLED", True):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        with patch("core_py.ml.llm.get_llm_client", return_value=mock_llm):
            with patch("core_py.ml.cache.get_cached_response", return_value=None):
                with patch("core_py.ml.cache.set_cached_response", new_callable=AsyncMock):
                    result = await invoke_llm_with_retry("test prompt")
                    assert result == "Test response"
                    mock_llm.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_invoke_llm_with_retry_rate_limit():
    """Test LLM invocation with rate limit error and retry."""

    with patch("core_py.ml.llm.LLM_ENABLED", True):
        mock_llm = MagicMock()

        # First call raises rate limit, second succeeds
        mock_response = MagicMock()
        mock_response.content = "Success after retry"

        rate_limit_error = Exception("Rate limit exceeded")
        rate_limit_error.response = MagicMock()
        rate_limit_error.response.status_code = 429

        mock_llm.ainvoke = AsyncMock(side_effect=[rate_limit_error, mock_response])

        with patch("core_py.ml.llm.get_llm_client", return_value=mock_llm):
            with patch("core_py.ml.cache.get_cached_response", return_value=None):
                with patch("core_py.ml.cache.set_cached_response", new_callable=AsyncMock):
                    with patch("asyncio.sleep", new_callable=AsyncMock):
                        result = await invoke_llm_with_retry("test prompt", max_retries=3)
                        assert result == "Success after retry"
                        assert mock_llm.ainvoke.call_count == 2


@pytest.mark.asyncio
async def test_invoke_llm_with_retry_quota_exceeded():
    """Test LLM invocation with quota exceeded error (should not retry)."""
    with patch("core_py.ml.llm.LLM_ENABLED", True):
        mock_llm = MagicMock()
        quota_error = Exception("Insufficient quota")
        mock_llm.ainvoke = AsyncMock(side_effect=quota_error)

        with patch("core_py.ml.llm.get_llm_client", return_value=mock_llm):
            with patch("core_py.ml.cache.get_cached_response", return_value=None):
                with pytest.raises(RuntimeError, match="quota exceeded"):
                    await invoke_llm_with_retry("test prompt")


@pytest.mark.asyncio
async def test_invoke_llm_with_retry_auth_error():
    """Test LLM invocation with authentication error (should not retry)."""
    with patch("core_py.ml.llm.LLM_ENABLED", True):
        mock_llm = MagicMock()
        auth_error = Exception("Authentication failed")
        mock_llm.ainvoke = AsyncMock(side_effect=auth_error)

        with patch("core_py.ml.llm.get_llm_client", return_value=mock_llm):
            with patch("core_py.ml.cache.get_cached_response", return_value=None):
                with pytest.raises(RuntimeError, match="authentication failed"):
                    await invoke_llm_with_retry("test prompt")


@pytest.mark.asyncio
async def test_invoke_llm_with_retry_max_retries_exceeded():
    """Test LLM invocation when max retries are exceeded."""

    with patch("core_py.ml.llm.LLM_ENABLED", True):
        mock_llm = MagicMock()
        generic_error = Exception("Generic error")
        mock_llm.ainvoke = AsyncMock(side_effect=generic_error)

        with patch("core_py.ml.llm.get_llm_client", return_value=mock_llm):
            with patch("core_py.ml.cache.get_cached_response", return_value=None):
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    with pytest.raises(RuntimeError, match="failed after"):
                        await invoke_llm_with_retry("test prompt", max_retries=2)

                    # Should have tried max_retries + 1 times
                    assert mock_llm.ainvoke.call_count == 3


@pytest.mark.asyncio
async def test_invoke_llm_with_retry_string_response():
    """Test LLM invocation when response is a string instead of object."""
    with patch("core_py.ml.llm.LLM_ENABLED", True):
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value="String response")

        with patch("core_py.ml.llm.get_llm_client", return_value=mock_llm):
            with patch("core_py.ml.cache.get_cached_response", return_value=None):
                with patch("core_py.ml.cache.set_cached_response", new_callable=AsyncMock):
                    result = await invoke_llm_with_retry("test prompt")
                    assert result == "String response"

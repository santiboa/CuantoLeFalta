"""Unit tests for president_reply module."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import president_reply


def _temp_cache_path(tmp_path):
    """Return a temp cache file path and patch president_reply to use it."""
    cache_file = tmp_path / "last_replied_id.json"
    return cache_file


class TestLoadLastRepliedId:
    """Tests for load_last_replied_id()."""

    def test_returns_none_when_cache_missing(self, tmp_path):
        """When cache file does not exist, returns None."""
        with patch.object(president_reply, "CACHE_FILE", tmp_path / "nonexistent.json"):
            result = president_reply.load_last_replied_id()
        assert result is None

    def test_returns_id_when_cache_valid(self, tmp_path):
        """When cache has valid JSON with last_tweet_id, returns it."""
        cache_file = tmp_path / "last_replied_id.json"
        cache_file.write_text('{"last_tweet_id": "1234567890", "replied_at": "2026-01-01T00:00:00"}')
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_last_replied_id()
        assert result == "1234567890"

    def test_returns_none_when_json_invalid(self, tmp_path):
        """When cache has invalid JSON, returns None."""
        cache_file = tmp_path / "last_replied_id.json"
        cache_file.write_text("not valid json {")
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_last_replied_id()
        assert result is None

    def test_returns_none_when_missing_key(self, tmp_path):
        """When cache JSON lacks last_tweet_id, returns None."""
        cache_file = tmp_path / "last_replied_id.json"
        cache_file.write_text('{"other_key": "value"}')
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_last_replied_id()
        assert result is None


class TestSaveLastRepliedId:
    """Tests for save_last_replied_id()."""

    def test_writes_valid_json(self, tmp_path):
        """Saves tweet_id and replied_at to cache file."""
        cache_file = tmp_path / "last_replied_id.json"
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            with patch("president_reply.datetime") as mock_dt:
                mock_dt.datetime.now.return_value.isoformat.return_value = "2026-01-01T12:00:00"
                president_reply.save_last_replied_id("9876543210")

        assert cache_file.exists()
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        assert data["last_tweet_id"] == "9876543210"
        assert "replied_at" in data

    def test_file_is_readable_by_load(self, tmp_path):
        """Data saved by save_last_replied_id can be loaded by load_last_replied_id."""
        cache_file = tmp_path / "last_replied_id.json"
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            president_reply.save_last_replied_id("5555555555")

        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_last_replied_id()
        assert result == "5555555555"


class TestRetryWithBackoff:
    """Tests for _retry_with_backoff()."""

    def test_returns_result_on_first_success(self):
        """Returns immediately when func succeeds on first try."""
        func = MagicMock(return_value="ok")
        result = president_reply._retry_with_backoff(func, "arg", kwarg="value")
        assert result == "ok"
        func.assert_called_once_with("arg", kwarg="value")

    def test_retries_on_failure_then_succeeds(self):
        """Retries and eventually succeeds."""
        func = MagicMock(side_effect=[Exception("fail"), Exception("fail"), "ok"])
        with patch("president_reply.time.sleep"):
            result = president_reply._retry_with_backoff(func)
        assert result == "ok"
        assert func.call_count == 3

    def test_raises_after_max_retries(self):
        """Raises last exception when all retries fail."""
        exc = ValueError("final failure")
        # MAX_RETRIES is 4: need 4 failures; last one is re-raised
        func = MagicMock(
            side_effect=[
                Exception("1"),
                Exception("2"),
                Exception("3"),
                exc,
            ]
        )
        with patch("president_reply.time.sleep"):
            with pytest.raises(ValueError, match="final failure"):
                president_reply._retry_with_backoff(func)
        assert func.call_count == 4


class TestMain:
    """Tests for main() entry point."""

    @patch("president_reply.DRY_RUN", True)
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_last_replied_id")
    @patch("president_reply.remaining_time")
    def test_skips_when_cannot_fetch_tweet(self, mock_remaining, mock_load, mock_get_id):
        """Exits early when get_latest_tweet_id returns None."""
        mock_get_id.return_value = None
        mock_remaining.return_value = "Le faltan..."

        president_reply.main()

        mock_load.assert_not_called()
        mock_remaining.assert_not_called()

    @patch("president_reply.DRY_RUN", True)
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_last_replied_id")
    @patch("president_reply.remaining_time")
    def test_skips_when_already_replied(self, mock_remaining, mock_load, mock_get_id):
        """Exits early when latest_id equals cached_id."""
        mock_get_id.return_value = "12345"
        mock_load.return_value = "12345"

        president_reply.main()

        mock_remaining.assert_not_called()

    @patch("president_reply.DRY_RUN", True)
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_last_replied_id")
    @patch("president_reply.remaining_time")
    def test_skips_when_countdown_ended(self, mock_remaining, mock_load, mock_get_id):
        """Exits early when remaining_time returns 'Ya acabó.'."""
        mock_get_id.return_value = "12345"
        mock_load.return_value = None
        mock_remaining.return_value = "Ya acabó."

        president_reply.main()

        # Should not post or save
        mock_remaining.assert_called_once()

    @patch("president_reply.DRY_RUN", True)
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_last_replied_id")
    @patch("president_reply.remaining_time")
    def test_dry_run_does_not_post(self, mock_remaining, mock_load, mock_get_id, tmp_path):
        """In DRY_RUN, does not call tweepy or save cache."""
        mock_get_id.return_value = "99999"
        mock_load.return_value = None
        mock_remaining.return_value = "Le faltan 4 años..."

        with patch.object(president_reply, "CACHE_FILE", tmp_path / "cache.json"):
            president_reply.main()

        mock_remaining.assert_called_once()
        # Cache should not be written in dry run
        assert not (tmp_path / "cache.json").exists()

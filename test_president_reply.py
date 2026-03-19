"""Unit tests for president_reply module (X API v2 version)."""
import json
from unittest.mock import MagicMock, patch

import pytest

import president_reply


def _mock_tweet(tweet_id="1234567890", text="Hello", created_at="2026-03-18T13:00:00Z"):
    """Create a mock tweet object matching Tweepy's Response.data format."""
    tweet = MagicMock()
    tweet.id = int(tweet_id)
    tweet.text = text
    tweet.created_at = created_at
    return tweet


def _mock_user(user_id="123456789"):
    """Create a mock user object."""
    user = MagicMock()
    user.id = int(user_id)
    return user


class TestLoadRepliedIds:
    """Tests for load_replied_ids()."""

    def test_returns_empty_when_cache_missing(self, tmp_path):
        with patch.object(president_reply, "CACHE_FILE", tmp_path / "nonexistent.json"):
            result = president_reply.load_replied_ids()
        assert result == []

    def test_returns_ids_when_cache_valid(self, tmp_path):
        cache_file = tmp_path / "last_replied_id.json"
        cache_file.write_text('{"replied_ids": ["111", "222"], "last_replied_at": "2026-01-01T00:00:00"}')
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_replied_ids()
        assert result == ["111", "222"]

    def test_handles_legacy_format(self, tmp_path):
        cache_file = tmp_path / "last_replied_id.json"
        cache_file.write_text('{"last_tweet_id": "1234567890"}')
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_replied_ids()
        assert result == ["1234567890"]

    def test_returns_empty_when_json_invalid(self, tmp_path):
        cache_file = tmp_path / "last_replied_id.json"
        cache_file.write_text("not valid json {")
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_replied_ids()
        assert result == []

    def test_returns_empty_when_missing_key(self, tmp_path):
        cache_file = tmp_path / "last_replied_id.json"
        cache_file.write_text('{"other_key": "value"}')
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_replied_ids()
        assert result == []


class TestSaveRepliedId:
    """Tests for save_replied_id()."""

    def test_writes_valid_json(self, tmp_path):
        cache_file = tmp_path / "last_replied_id.json"
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            president_reply.save_replied_id("9876543210")

        assert cache_file.exists()
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        assert "9876543210" in data["replied_ids"]
        assert "last_replied_at" in data

    def test_file_is_readable_by_load(self, tmp_path):
        cache_file = tmp_path / "last_replied_id.json"
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            president_reply.save_replied_id("5555555555")
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            result = president_reply.load_replied_ids()
        assert "5555555555" in result

    def test_limits_to_max_entries(self, tmp_path):
        cache_file = tmp_path / "last_replied_id.json"
        with patch.object(president_reply, "CACHE_FILE", cache_file):
            for i in range(5):
                president_reply.save_replied_id(str(i))
            result = president_reply.load_replied_ids()
        assert len(result) == president_reply.REPLIED_IDS_LIMIT


class TestGetPresidentUserId:
    """Tests for get_president_user_id()."""

    def setup_method(self):
        """Reset cached user ID between tests."""
        president_reply._president_user_id = None

    def test_resolves_username_to_id(self):
        mock_client = MagicMock()
        mock_client.get_user.return_value = MagicMock(data=_mock_user("999888777"))

        result = president_reply.get_president_user_id(mock_client)

        assert result == "999888777"
        mock_client.get_user.assert_called_once_with(username="Claudiashein")

    def test_caches_user_id_after_first_call(self):
        mock_client = MagicMock()
        mock_client.get_user.return_value = MagicMock(data=_mock_user("999888777"))

        president_reply.get_president_user_id(mock_client)
        president_reply.get_president_user_id(mock_client)

        # Should only call API once
        mock_client.get_user.assert_called_once()

    def test_returns_none_when_user_not_found(self):
        mock_client = MagicMock()
        mock_client.get_user.return_value = MagicMock(data=None)

        result = president_reply.get_president_user_id(mock_client)
        assert result is None


class TestGetLatestTweetId:
    """Tests for get_latest_tweet_id()."""

    def setup_method(self):
        president_reply._president_user_id = None

    def test_returns_latest_tweet_id(self):
        mock_client = MagicMock()
        mock_client.get_user.return_value = MagicMock(data=_mock_user("123"))
        mock_client.get_users_tweets.return_value = MagicMock(
            data=[_mock_tweet("9999999")]
        )

        result = president_reply.get_latest_tweet_id(mock_client)

        assert result == "9999999"
        mock_client.get_users_tweets.assert_called_once_with(
            id="123",
            max_results=5,
            exclude=["retweets", "replies"],
            tweet_fields=["created_at"],
        )

    def test_returns_none_when_no_tweets(self):
        mock_client = MagicMock()
        mock_client.get_user.return_value = MagicMock(data=_mock_user("123"))
        mock_client.get_users_tweets.return_value = MagicMock(data=None)

        result = president_reply.get_latest_tweet_id(mock_client)
        assert result is None

    def test_returns_none_when_user_lookup_fails(self):
        mock_client = MagicMock()
        mock_client.get_user.return_value = MagicMock(data=None)

        result = president_reply.get_latest_tweet_id(mock_client)

        assert result is None
        mock_client.get_users_tweets.assert_not_called()

    def test_returns_first_tweet_when_multiple(self):
        """Should return the most recent tweet (first in the list)."""
        mock_client = MagicMock()
        mock_client.get_user.return_value = MagicMock(data=_mock_user("123"))
        mock_client.get_users_tweets.return_value = MagicMock(
            data=[
                _mock_tweet("111", created_at="2026-03-18T14:00:00Z"),
                _mock_tweet("222", created_at="2026-03-18T13:00:00Z"),
                _mock_tweet("333", created_at="2026-03-18T12:00:00Z"),
            ]
        )

        result = president_reply.get_latest_tweet_id(mock_client)
        assert result == "111"


class TestMain:
    """Tests for main() entry point."""

    def setup_method(self):
        president_reply._president_user_id = None

    @patch("president_reply.DRY_RUN", True)
    @patch("president_reply._get_read_client")
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_replied_ids")
    @patch("president_reply.remaining_time")
    def test_skips_when_cannot_fetch_tweet(self, mock_remaining, mock_load, mock_get_id, mock_read_client):
        mock_get_id.return_value = None

        president_reply.main()

        mock_load.assert_not_called()
        mock_remaining.assert_not_called()

    @patch("president_reply.DRY_RUN", True)
    @patch("president_reply._get_read_client")
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_replied_ids")
    @patch("president_reply.remaining_time")
    def test_skips_when_already_replied(self, mock_remaining, mock_load, mock_get_id, mock_read_client):
        mock_get_id.return_value = "12345"
        mock_load.return_value = ["12345"]

        president_reply.main()

        mock_remaining.assert_not_called()

    @patch("president_reply.DRY_RUN", True)
    @patch("president_reply._get_read_client")
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_replied_ids")
    @patch("president_reply.remaining_time")
    def test_skips_when_countdown_ended(self, mock_remaining, mock_load, mock_get_id, mock_read_client):
        mock_get_id.return_value = "12345"
        mock_load.return_value = []
        mock_remaining.return_value = "Ya acabó."

        president_reply.main()

        mock_remaining.assert_called_once()

    @patch("president_reply.DRY_RUN", True)
    @patch("president_reply._get_read_client")
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_replied_ids")
    @patch("president_reply.remaining_time")
    def test_dry_run_does_not_post(self, mock_remaining, mock_load, mock_get_id, mock_read_client, tmp_path):
        mock_get_id.return_value = "99999"
        mock_load.return_value = []
        mock_remaining.return_value = "Le faltan 4 años..."

        with patch.object(president_reply, "CACHE_FILE", tmp_path / "cache.json"):
            president_reply.main()

        mock_remaining.assert_called_once()
        assert not (tmp_path / "cache.json").exists()

    @patch("president_reply.DRY_RUN", False)
    @patch("president_reply._get_read_client")
    @patch("president_reply._get_write_client")
    @patch("president_reply.get_latest_tweet_id")
    @patch("president_reply.load_replied_ids")
    @patch("president_reply.remaining_time")
    def test_posts_quote_tweet_when_new_tweet(self, mock_remaining, mock_load, mock_get_id, mock_write_client, mock_read_client, tmp_path):
        mock_get_id.return_value = "99999"
        mock_load.return_value = ["88888"]  # different from latest
        mock_remaining.return_value = "Le faltan 4 años..."

        mock_client = MagicMock()
        mock_write_client.return_value = mock_client

        with patch.object(president_reply, "CACHE_FILE", tmp_path / "cache.json"):
            president_reply.main()

        mock_client.create_tweet.assert_called_once_with(
            text="Le faltan 4 años...",
            quote_tweet_id="99999",
        )
        # Cache should be updated
        assert (tmp_path / "cache.json").exists()

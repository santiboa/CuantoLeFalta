"""Tests for countdown module."""
import datetime
import pytest
import pytz

from countdown import end, remaining_time, start, timezone


def fake_now(year, month, day, hour=0, minute=0, second=0):
    """Create a timezone-aware datetime for Mexico City."""
    return timezone.localize(datetime.datetime(year, month, day, hour, minute, second))


class TestRemainingTime:
    """Test remaining_time() output format and edge cases."""

    def test_returns_ya_acabo_when_past_end(self):
        """When now is after end, should return 'Ya acabó.'"""
        now = fake_now(2031, 1, 1)
        result = remaining_time(now=now)
        assert result == "Ya acabó."

    def test_format_contains_cuantolefalta(self):
        """Output should include the hashtag."""
        now = fake_now(2026, 2, 22, 12, 0, 0)
        result = remaining_time(now=now)
        assert "#cuantolefalta" in result

    def test_format_contains_elapsed_percent(self):
        """Output should include elapsed percentage."""
        now = fake_now(2026, 2, 22, 12, 0, 0)
        result = remaining_time(now=now)
        assert "Ya pasó" in result
        assert "% del sexenio" in result

    def test_format_contains_days(self):
        """Output should include days remaining."""
        now = fake_now(2026, 2, 22, 12, 0, 0)
        result = remaining_time(now=now)
        assert "año" in result or "años" in result
        assert "día" in result or "días" in result

    def test_default_uses_current_time(self):
        """When now is not passed, uses actual current time."""
        result = remaining_time()
        # Should not raise and should return valid format
        assert "Le faltan" in result or result == "Ya acabó."


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

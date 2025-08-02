from datetime import date, datetime
from unittest.mock import patch

from django.test import TestCase

from appcore.services.date_utils import (
    dec_month,
    dt_range_from_dt,
    inc_month,
    month_range_from_now,
    next_n_months,
    prev_n_months,
)
from appcore.services.gen_token import gen_token


class GenTokenTest(TestCase):
    """Test cases for token generation utility."""

    def test_gen_token_default_length(self):
        """Test token generation with default length."""
        token = gen_token()
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

    def test_gen_token_custom_length(self):
        """Test token generation with custom length."""
        token = gen_token(32)
        self.assertIsInstance(token, str)
        # URL-safe base64 encoding makes output longer than input bytes
        self.assertGreater(len(token), 32)

    def test_gen_token_uniqueness(self):
        """Test that generated tokens are unique."""
        token1 = gen_token()
        token2 = gen_token()
        self.assertNotEqual(token1, token2)

    def test_gen_token_small_length(self):
        """Test token generation with small length."""
        token = gen_token(1)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)


class DateUtilsTest(TestCase):
    """Test cases for date utility functions."""

    @patch("appcore.services.date_utils.date")
    def test_prev_n_months(self, mock_date):
        """Test getting previous n months."""
        # Mock current date to January (month=1)
        mock_date.today.return_value = date(2024, 1, 15)

        result = prev_n_months(3)
        expected = ["december", "november", "october"]
        self.assertEqual(result, expected)

    @patch("appcore.services.date_utils.date")
    def test_prev_n_months_mid_year(self, mock_date):
        """Test getting previous n months from mid-year."""
        # Mock current date to June (month=6)
        mock_date.today.return_value = date(2024, 6, 15)

        result = prev_n_months(2)
        expected = ["may", "april"]
        self.assertEqual(result, expected)

    @patch("appcore.services.date_utils.date")
    def test_next_n_months(self, mock_date):
        """Test getting next n months."""
        # Mock current date to December (month=12)
        mock_date.today.return_value = date(2024, 12, 15)

        result = next_n_months(3)
        expected = ["january", "february", "march"]
        self.assertEqual(result, expected)

    @patch("appcore.services.date_utils.date")
    def test_next_n_months_mid_year(self, mock_date):
        """Test getting next n months from mid-year."""
        # Mock current date to June (month=6)
        mock_date.today.return_value = date(2024, 6, 15)

        result = next_n_months(2)
        expected = ["july", "august"]
        self.assertEqual(result, expected)

    @patch("appcore.services.date_utils.date")
    def test_month_range_from_now(self, mock_date):
        """Test getting month range from now."""
        # Mock current date to June (month=6)
        mock_date.today.return_value = date(2024, 6, 15)

        result = month_range_from_now(2)
        # The function returns prev_n_months(n) which returns in reverse order
        expected = ["may", "april", "june", "july", "august"]
        self.assertEqual(result, expected)

    def test_inc_month(self):
        """Test incrementing month."""
        dt = datetime(2024, 1, 15)
        result = inc_month(dt, 1)
        self.assertEqual(result.month, 2)
        self.assertEqual(result.day, 1)  # Should go to first day of month

    def test_inc_month_year_boundary(self):
        """Test incrementing month across year boundary."""
        dt = datetime(2023, 12, 15)
        result = inc_month(dt, 1)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    def test_inc_month_multiple(self):
        """Test incrementing multiple months."""
        dt = datetime(2024, 1, 15)
        result = inc_month(dt, 3)
        self.assertEqual(result.month, 4)
        self.assertEqual(result.day, 1)

    def test_dec_month(self):
        """Test decrementing month."""
        dt = datetime(2024, 2, 15)
        result = dec_month(dt, 1)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 31)  # Should go to last day of January

    def test_dec_month_year_boundary(self):
        """Test decrementing month across year boundary."""
        dt = datetime(2024, 1, 15)
        result = dec_month(dt, 1)
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 31)

    def test_dt_range_from_dt(self):
        """Test getting datetime range from datetime."""
        dt = datetime(2024, 6, 15)
        result = dt_range_from_dt(dt, 2)

        # Should have original dt plus 2 future and 2 past months (5 total)
        self.assertEqual(len(result), 5)
        self.assertIn(dt, result)

        # Should be sorted
        for i in range(len(result) - 1):
            self.assertLessEqual(result[i], result[i + 1])

    def test_edge_cases_zero_months(self):
        """Test edge cases with zero months."""
        self.assertEqual(prev_n_months(0), [])
        self.assertEqual(next_n_months(0), [])

        dt = datetime(2024, 6, 15)
        result = dt_range_from_dt(dt, 0)
        self.assertEqual(result, [dt])

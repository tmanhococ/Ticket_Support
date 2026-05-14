from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from src.api.scripts.seed_data import seed_data


@pytest.fixture
def mock_csv_data():
    return pd.DataFrame(
        {
            "subject": ["Test 1", "Test 2"],
            "body": ["Body 1", "Body 2"],
            "type": ["Incident", "Request"],
            "queue": ["Tech Support", "Billing"],
            "language": ["en", "de"],
            "priority": ["high", "low"],
        }
    )


@pytest.mark.asyncio
async def test_seed_data_missing_csv(caplog):
    """Test seed_data gracefully handles missing CSV."""
    with patch("src.api.scripts.seed_data.CSV_PATH") as mock_path:
        mock_path.exists.return_value = False
        await seed_data()
        assert "Cannot find CSV file" in caplog.text


@pytest.mark.asyncio
async def test_seed_data_existing_tickets(caplog, mock_csv_data):
    """Test seed_data skips if tickets already exist."""
    with (
        patch("src.api.scripts.seed_data.CSV_PATH") as mock_path,
        patch("src.api.scripts.seed_data.pd.read_csv", return_value=mock_csv_data),
        patch("src.api.scripts.seed_data.AsyncSessionLocal") as mock_session_maker,
    ):

        mock_path.exists.return_value = True

        # Mock session and execution
        mock_session = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        # Mock result of SELECT COUNT(*) to return 5 (already seeded)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result

        await seed_data()

        assert "Database already contains 5 tickets" in caplog.text
        # Ensure add_all was not called
        mock_session.add_all.assert_not_called()


@pytest.mark.asyncio
async def test_seed_data_success(caplog, mock_csv_data):
    """Test successful seed_data execution."""
    with (
        patch("src.api.scripts.seed_data.CSV_PATH") as mock_path,
        patch("src.api.scripts.seed_data.pd.read_csv", return_value=mock_csv_data),
        patch("src.api.scripts.seed_data.AsyncSessionLocal") as mock_session_maker,
    ):

        mock_path.exists.return_value = True

        # Mock session and execution
        mock_session = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        # Mock result of SELECT COUNT(*) to return 0 (empty table)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result

        await seed_data()

        assert "Successfully inserted 2 historical tickets" in caplog.text
        # Ensure add_all was called
        mock_session.add_all.assert_called_once()
        mock_session.commit.assert_awaited_once()

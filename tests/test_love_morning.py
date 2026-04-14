import pytest

import love_morning


@pytest.mark.asyncio
async def test_main(mocker):
    mock_include = mocker.patch(
        "love_morning.config.dispatcher.include_routers",
    )
    mock_polling = mocker.patch(
        "love_morning.config.dispatcher.start_polling",
        new_callable=mocker.AsyncMock,
    )
    mock_wish = mocker.patch(
        "love_morning.wish_good_morning", new_callable=mocker.AsyncMock,
    )
    mock_send = mocker.patch(
        "love_morning.safe_send_message", new_callable=mocker.AsyncMock,
    )
    await love_morning.main()
    mock_include.assert_called_once()
    mock_polling.assert_called_once()
    mock_wish.assert_called_once()
    mock_send.assert_called_once_with(love_morning.config.MY_ID, 'Бот запущен')

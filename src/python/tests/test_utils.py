from common.utils import capital_case


def test_capital_case() -> None:
    assert capital_case('semaphore') == 'Semaphore'  # nosec B101

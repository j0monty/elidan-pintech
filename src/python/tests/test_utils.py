from common.utils import capital_case


def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'

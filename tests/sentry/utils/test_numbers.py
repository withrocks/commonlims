

from sentry.utils.numbers import base36_encode, base36_decode, \
    base32_encode, base32_decode, format_bytes


def test_base36():
    assert [base36_encode(x) for x in range(128)] == [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
        'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1A', '1B', '1C', '1D', '1E',
        '1F', '1G', '1H', '1I', '1J', '1K', '1L', '1M', '1N', '1O', '1P', '1Q', '1R', '1S', '1T',
        '1U', '1V', '1W', '1X', '1Y', '1Z', '20', '21', '22', '23', '24', '25', '26', '27', '28',
        '29', '2A', '2B', '2C', '2D', '2E', '2F', '2G', '2H', '2I', '2J', '2K', '2L', '2M', '2N',
        '2O', '2P', '2Q', '2R', '2S', '2T', '2U', '2V', '2W', '2X', '2Y', '2Z', '30', '31', '32',
        '33', '34', '35', '36', '37', '38', '39', '3A', '3B', '3C', '3D', '3E', '3F', '3G', '3H',
        '3I', '3J'
    ]

    assert [base36_decode(base36_encode(x)) for x in range(128)] == list(map(int, list(range(128))))


def test_base32():
    assert [base32_encode(x) for x in range(128)] == [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
        'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z', '10', '11', '12',
        '13', '14', '15', '16', '17', '18', '19', '1A', '1B', '1C', '1D', '1E', '1F', '1G', '1H',
        '1J', '1K', '1M', '1N', '1P', '1Q', '1R', '1S', '1T', '1V', '1W', '1X', '1Y', '1Z', '20',
        '21', '22', '23', '24', '25', '26', '27', '28', '29', '2A', '2B', '2C', '2D', '2E', '2F',
        '2G', '2H', '2J', '2K', '2M', '2N', '2P', '2Q', '2R', '2S', '2T', '2V', '2W', '2X', '2Y',
        '2Z', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3A', '3B', '3C', '3D',
        '3E', '3F', '3G', '3H', '3J', '3K', '3M', '3N', '3P', '3Q', '3R', '3S', '3T', '3V', '3W',
        '3X', '3Y', '3Z'
    ]

    assert [base32_decode(base32_encode(x)) for x in range(128)] == list(map(int, list(range(128))))


def test_format_bytes():
    assert format_bytes(50) == '50 B'
    assert format_bytes(1024) == '1.00 KB'
    assert format_bytes(3000) == '2.93 KB'
    assert format_bytes(30000) == '29.30 KB'
    assert format_bytes(3000000) == '2.86 MB'
    assert format_bytes(3000000000) == '2.79 GB'
    assert format_bytes(3000000000000) == '2.73 TB'

    assert format_bytes(3000000000000, units=['B', 'KB', 'MB', 'GB']) == '2793.97 GB'

from kauma.first_exam.disk import get_position


def test_get_position():
    assert get_position(0) == (0, 0)
    assert get_position(511) == (0, 511)
    assert get_position(512) == (1, 0)
    assert get_position(1023) == (1, 511)

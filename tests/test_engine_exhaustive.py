from backend.core.liuyao_engine import LiuyaoEngine


def _bits(mask: int):
    return [(mask >> index) & 1 for index in range(6)]


def test_all_4096_hexagram_and_moving_line_combinations_are_structurally_valid():
    engine = LiuyaoEngine()
    checked = 0

    for base_mask in range(64):
        yao_values = _bits(base_mask)
        for change_mask in range(64):
            changing = [bool(value) for value in _bits(change_mask)]
            result = engine.paipan(
                {
                    "yao_list": yao_values,
                    "changing_yao": changing,
                    "year": 2026,
                    "month": 4,
                    "day": 23,
                    "hour": 10,
                }
            )

            assert result.ben_gua_name
            if change_mask == 0:
                # Existing engine contract: a static hexagram has no separate
                # transformed-hexagram name.
                assert result.bian_gua_name == ""
            else:
                assert result.bian_gua_name
            assert 1 <= result.shi_yao <= 6
            assert 1 <= result.ying_yao <= 6
            assert len(result.yao_list) == 6
            assert len(result.gan_zhi["year"]) == 2
            assert len(result.gan_zhi["month"]) == 2
            assert len(result.gan_zhi["day"]) == 2
            assert len(result.gan_zhi["hour"]) == 2

            for position, yao in enumerate(result.yao_list, start=1):
                assert yao.position == position
                assert yao.yin_yang in (0, 1)
                assert yao.dizhi
                assert yao.wuxing
                assert yao.liuqin
                assert yao.liushen

            checked += 1

    assert checked == 4096

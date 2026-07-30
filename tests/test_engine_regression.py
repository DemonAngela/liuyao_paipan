from backend.core.liuyao_engine import LiuyaoEngine
from backend.models.gua import GuaDataModel


def test_all_4096_hexagram_change_combinations():
    engine = LiuyaoEngine()
    gua_by_code = engine._gua_by_code

    for ben_code, ben_gua in gua_by_code.items():
        yao_values = [int(value) for value in ben_code]
        for mask in range(64):
            changing = [
                bool(mask & (1 << index)) for index in range(6)
            ]
            bian_code = "".join(
                str(1 - value if changing[index] else value)
                for index, value in enumerate(yao_values)
            )
            result = engine.paipan(
                {
                    "yao_list": yao_values,
                    "changing_yao": changing,
                    "year": 2025,
                    "month": 3,
                    "day": 10,
                    "hour": 10,
                }
            )

            assert result.ben_gua_name == ben_gua["name"]
            assert len(result.yao_list) == 6
            if mask == 0:
                assert result.bian_gua_name == ""
                assert result.bian_special_attr is None
                assert all(
                    yao.biangua_info is None for yao in result.yao_list
                )
            else:
                expected_bian = gua_by_code[bian_code]
                assert result.bian_gua_name == expected_bian["name"]
                assert [
                    yao.biangua_info.dizhi for yao in result.yao_list
                ] == [
                    yao["dizhi"] for yao in expected_bian["yao_list"]
                ]
            GuaDataModel.model_validate(result)


def test_engine_rejects_invalid_untyped_inputs():
    engine = LiuyaoEngine()
    base = {
        "yao_list": [1] * 6,
        "changing_yao": [False] * 6,
        "year": 2025,
        "month": 3,
        "day": 10,
    }

    invalid_yao = {**base, "yao_list": [1, 1, 1, 1, 1, True]}
    invalid_flags = {**base, "changing_yao": [0] * 6}

    for payload in (invalid_yao, invalid_flags):
        try:
            engine.paipan(payload)
        except ValueError:
            pass
        else:
            raise AssertionError("无效引擎输入未被拒绝")


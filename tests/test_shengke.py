from backend.core.shengke import ShengKeCalculator
from backend.models.gua import BianguaYaoData, GuaData, YaoData
from backend.utils.constants import DIZHI_WUXING


def make_yao(
    position,
    dizhi,
    *,
    changing=False,
    andong=False,
    bian_dizhi=None,
):
    bian = (
        BianguaYaoData(
            yin_yang=0,
            dizhi=bian_dizhi,
            wuxing=DIZHI_WUXING[bian_dizhi],
            liuqin="兄弟",
        )
        if bian_dizhi
        else None
    )
    yao = YaoData(
        position=position,
        yin_yang=1,
        is_changing=changing,
        dizhi=dizhi,
        wuxing=DIZHI_WUXING[dizhi],
        biangua_info=bian,
    )
    yao.is_andong = andong
    return yao


def test_liuhe_and_liuchong_require_at_least_one_moving_yao():
    calculator = ShengKeCalculator()
    static = [
        make_yao(1, "子"),
        make_yao(2, "丑"),
        make_yao(3, "午"),
    ]

    assert calculator.find_liuhe(static) == []
    assert calculator.find_liuchong(static) == []

    static[0].is_changing = True
    assert calculator.find_liuhe(static) == [("子", "丑", 1, 2)]
    assert calculator.find_liuchong(static) == [("子", "午", 1, 3)]


def test_sanhe_accepts_two_moving_base_branches():
    calculator = ShengKeCalculator()
    yaos = [
        make_yao(1, "申", changing=True),
        make_yao(2, "子", andong=True),
        make_yao(3, "辰"),
        make_yao(4, "丑"),
        make_yao(5, "寅"),
        make_yao(6, "酉"),
    ]

    result = calculator.find_sanhe(yaos)

    assert result == [
        {
            "wuxing": "水",
            "items": [
                {"pos": 1, "dizhi": "申", "is_bian": False},
                {"pos": 2, "dizhi": "子", "is_bian": False},
                {"pos": 3, "dizhi": "辰", "is_bian": False},
            ],
        }
    ]


def test_sanhe_rejects_inner_changed_branch_when_other_boundary_is_static():
    calculator = ShengKeCalculator()
    yaos = [
        make_yao(1, "申", changing=True, bian_dizhi="子"),
        make_yao(2, "丑"),
        make_yao(3, "辰"),
        make_yao(4, "卯"),
        make_yao(5, "巳"),
        make_yao(6, "未"),
    ]

    result = calculator.find_sanhe(yaos)

    assert result == []


def test_sanhe_accepts_inner_changed_branch_when_both_boundaries_move():
    calculator = ShengKeCalculator()
    yaos = [
        make_yao(1, "申", changing=True, bian_dizhi="子"),
        make_yao(2, "丑"),
        make_yao(3, "辰", changing=True, bian_dizhi="午"),
        make_yao(4, "卯"),
        make_yao(5, "巳"),
        make_yao(6, "未"),
    ]

    result = calculator.find_sanhe(yaos)

    assert result == [
        {
            "wuxing": "水",
            "items": [
                {"pos": 1, "dizhi": "申", "is_bian": False},
                {
                    "pos": 1,
                    "dizhi": "子",
                    "is_bian": True,
                    "src_pos": 1,
                },
                {"pos": 3, "dizhi": "辰", "is_bian": False},
            ],
        }
    ]


def test_calc_all_relations_public_entry_is_usable():
    calculator = ShengKeCalculator()
    yaos = [
        make_yao(1, "子"),
        make_yao(2, "丑"),
        make_yao(3, "寅"),
        make_yao(4, "卯"),
        make_yao(5, "辰"),
        make_yao(6, "巳"),
    ]
    gua = GuaData(
        ben_gua_name="测试",
        bian_gua_name="",
        yao_list=yaos,
        shi_yao=1,
        ying_yao=4,
        gan_zhi={
            "year": "乙巳",
            "month": "己卯",
            "day": "戊寅",
            "hour": "丁巳",
        },
        xunkong=("申", "酉"),
        relations={},
    )

    result = calculator.calc_all_relations(gua)

    assert set(result) == {
        "liuhe",
        "liuchong",
        "sanhe",
        "shengwangmujue",
        "shengwangmujue_details",
    }
    assert len(result["shengwangmujue"]) == 6


def test_day_clash_distinguishes_hidden_move_and_break():
    calculator = ShengKeCalculator()
    supported = make_yao(1, "子")
    calculator.calc_riyue_status(supported, "甲午", "甲申")

    assert supported.is_andong is True
    assert supported.is_ripo is False

    month_broken = make_yao(1, "子")
    calculator.calc_riyue_status(month_broken, "甲午", "甲午")

    assert month_broken.is_andong is False
    assert month_broken.is_ripo is True
    assert month_broken.is_yuepo is True


def test_book_example_earth_day_clash_is_hidden_move():
    calculator = ShengKeCalculator()
    earth = make_yao(1, "丑")

    calculator.calc_riyue_status(earth, "己未", "甲寅")

    assert earth.is_andong is True
    assert earth.is_ripo is False
    assert earth.day_relations == ["日扶", "日冲", "暗动"]
    assert earth.month_relations == ["月克"]


def test_month_is_included_in_shengwangmujue_details():
    calculator = ShengKeCalculator()
    yaos = [
        make_yao(1, "酉"),
        make_yao(2, "子"),
        make_yao(3, "寅"),
        make_yao(4, "卯"),
        make_yao(5, "辰"),
        make_yao(6, "午"),
    ]

    details = calculator.calc_shengwangmujue_details(
        yaos,
        "甲子",
        "乙巳",
    )

    assert any("[初爻酉金]长生在巳[月建巳火]" == item for item in details)

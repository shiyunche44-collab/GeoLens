import uuid

from geolens.modules.analysis.pipeline import BrandRef
from geolens.modules.analysis.pipeline.steps import match_brands, normalize_url

GEO = BrandRef(uuid.uuid4(), "GeoLens", aliases=["极光透镜"])
RANK = BrandRef(uuid.uuid4(), "RankPilot")


def test_positions_follow_first_mention_order() -> None:
    facts = match_brands("先看 RankPilot，再看 GeoLens，最后又提到 RankPilot", [GEO, RANK])
    assert [(f.brand_id, f.position) for f in facts] == [(RANK.id, 1), (GEO.id, 2)]


def test_fullwidth_case_and_cjk_aliases() -> None:
    assert match_brands("推荐ＧＥＯＬＥＮＳ", [GEO])
    assert match_brands("推荐极光透镜这款工具", [GEO])


def test_ascii_names_need_word_boundaries() -> None:
    assert not match_brands("GeoLensX is unrelated", [GEO])
    assert not match_brands("prankpilots", [RANK])


def test_url_normalization_drops_tracking_and_www() -> None:
    assert (
        normalize_url("https://WWW.Example.com/a/?utm_source=x&id=1#frag")
        == "https://example.com/a?id=1"
    )

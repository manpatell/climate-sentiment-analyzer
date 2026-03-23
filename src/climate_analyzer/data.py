"""Curated sample climate news dataset.

Provides 18 realistic article stubs spanning technology, policy, science,
and impact categories — used for dashboard demos and unit tests.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from .models import Article


def _dt(days_ago: int) -> datetime:
    """Return a naive UTC datetime *days_ago* days in the past."""
    return datetime(2025, 9, 1) + timedelta(days=days_ago)


SAMPLE_ARTICLES: list[Article] = [
    # ── Technology ──────────────────────────────────────────────────────────
    Article(
        id="tech-01",
        title="Solar panels hit record 47% efficiency",
        body=(
            "Scientists achieved a major breakthrough in solar panel efficiency, "
            "reaching a record 47% photovoltaic conversion rate in lab conditions. "
            "This innovative solution promises to accelerate the global transition to "
            "clean renewable energy and significantly reduce carbon emissions. Experts "
            "call it the most promising advance in sustainable power generation this decade."
        ),
        source="CleanTech Weekly",
        category="Technology",
        published_at=_dt(0),
        region="Global",
    ),
    Article(
        id="tech-02",
        title="Offshore wind capacity doubles in Europe",
        body=(
            "European offshore wind energy capacity doubled in 2024, driven by record "
            "investment in turbine technology and grid electrification. New floating "
            "turbines achieve unprecedented clean output, providing sustainable electricity "
            "to millions of homes. The sector advances rapidly, with innovative designs "
            "cutting costs and improving resilience against extreme weather."
        ),
        source="Energy Monitor",
        category="Technology",
        published_at=_dt(7),
        region="Europe",
    ),
    Article(
        id="tech-03",
        title="Carbon capture plant opens in Iceland",
        body=(
            "The world's largest carbon-capture facility began operations in Iceland, "
            "drawing CO2 directly from the atmosphere using geothermal power. The plant "
            "demonstrates a promising path toward net-zero goals. While critics note the "
            "scale remains insufficient to offset global emissions, the breakthrough "
            "signals growing momentum for carbon removal technology."
        ),
        source="Carbon Brief",
        category="Technology",
        published_at=_dt(14),
        region="Europe",
    ),
    Article(
        id="tech-04",
        title="EV battery range surpasses 600 miles",
        body=(
            "A new solid-state battery technology for electric vehicles achieved 600-mile "
            "range in real-world testing, addressing the primary barrier to mass adoption. "
            "The innovation uses sustainable materials and charges in under 15 minutes. "
            "Analysts predict the breakthrough will accelerate the clean transport transition "
            "and reduce fossil fuel dependency across major economies."
        ),
        source="AutoElectric",
        category="Technology",
        published_at=_dt(21),
        region="North America",
    ),
    # ── Policy ──────────────────────────────────────────────────────────────
    Article(
        id="pol-01",
        title="G20 nations agree on carbon pricing framework",
        body=(
            "G20 leaders reached a landmark agreement on a unified carbon pricing "
            "mechanism, setting a minimum floor price of $50 per tonne. The policy "
            "represents significant progress toward net-zero commitments and incentivizes "
            "the transition away from fossil fuels. Environmental groups praised the "
            "decision as an important step, though urged faster implementation timelines."
        ),
        source="Reuters Climate",
        category="Policy",
        published_at=_dt(30),
        region="Global",
    ),
    Article(
        id="pol-02",
        title="US methane regulations face industry pushback",
        body=(
            "New EPA methane regulations targeting oil and gas operations face legal "
            "challenges from industry groups claiming severe economic damage. Critics warn "
            "the rules will worsen energy costs and fail to reduce global emissions if "
            "other nations don't follow. Environmental advocates counter that methane "
            "pollution is a critical driver of short-term warming and the risks of inaction "
            "are catastrophic."
        ),
        source="Washington Post",
        category="Policy",
        published_at=_dt(38),
        region="North America",
    ),
    Article(
        id="pol-03",
        title="EU deforestation law enters force",
        body=(
            "The European Union's landmark deforestation regulation took effect, banning "
            "imports of commodities linked to forest destruction. The policy covers soy, "
            "beef, palm oil, and timber. Reforestation advocates praised the conservation "
            "measure as progress toward protecting biodiversity. Brazil and Indonesia "
            "expressed concerns about trade impacts."
        ),
        source="The Guardian",
        category="Policy",
        published_at=_dt(45),
        region="Europe",
    ),
    Article(
        id="pol-04",
        title="COP30 negotiations stall over financing",
        body=(
            "COP30 climate talks in Belém collapsed without agreement on the $1.3 trillion "
            "annual financing target for developing nations. Delegates warned of dangerous "
            "failure to address the loss and damage crisis threatening vulnerable "
            "communities. The collapse risks severe setbacks for global adaptation efforts "
            "and undermines trust in the multilateral climate process."
        ),
        source="Climate Home News",
        category="Policy",
        published_at=_dt(53),
        region="Global",
    ),
    # ── Science ─────────────────────────────────────────────────────────────
    Article(
        id="sci-01",
        title="Arctic sea ice hits lowest extent on record",
        body=(
            "Arctic sea ice coverage reached its lowest recorded extent this September, "
            "alarming scientists who warn of accelerating warming feedback loops. The "
            "decline in ice exposes dark ocean water that absorbs more heat, worsening "
            "global temperature rise. Researchers describe the trend as catastrophic for "
            "polar biodiversity and a dangerous tipping point for the climate system."
        ),
        source="Nature Climate",
        category="Science",
        published_at=_dt(60),
        region="Arctic",
    ),
    Article(
        id="sci-02",
        title="New ocean acidification data raises coral alarm",
        body=(
            "A comprehensive global survey found ocean acidification rates have accelerated "
            "25% faster than models predicted, threatening catastrophic bleaching events "
            "across tropical coral reefs. The loss of coral ecosystems damages biodiversity "
            "and the livelihoods of 500 million people. Researchers call for immediate "
            "emissions reductions to prevent irreversible damage."
        ),
        source="NOAA",
        category="Science",
        published_at=_dt(68),
        region="Global",
    ),
    Article(
        id="sci-03",
        title="Permafrost thaw releasing unexpected methane volumes",
        body=(
            "Arctic permafrost is thawing far faster than expected, releasing methane "
            "volumes that could trigger dangerous tipping points in the global climate "
            "system. Scientists warn the collapse of permafrost soil risks adding the "
            "equivalent of decades of industrial emissions. The findings underscore the "
            "urgency of deep decarbonization to avoid irreversible warming."
        ),
        source="Science",
        category="Science",
        published_at=_dt(76),
        region="Arctic",
    ),
    Article(
        id="sci-04",
        title="Reforestation programs show measurable carbon gains",
        body=(
            "A 10-year study across 50 reforestation sites confirmed measurable increases "
            "in carbon sequestration and biodiversity recovery. Restored ecosystems show "
            "resilient growth even in warming conditions. Researchers highlight conservation "
            "of existing old-growth forests as even more effective, recommending combined "
            "protection and restoration strategies for maximum climate benefit."
        ),
        source="PNAS",
        category="Science",
        published_at=_dt(84),
        region="Global",
    ),
    # ── Impact ──────────────────────────────────────────────────────────────
    Article(
        id="imp-01",
        title="Wildfires burn record area across North America",
        body=(
            "An unprecedented wildfire season devastated over 18 million hectares across "
            "North America, driven by extreme drought and warming temperatures. Air pollution "
            "from toxic smoke triggered health emergencies in major cities. Scientists link "
            "the catastrophic fire season directly to climate change, warning conditions "
            "will worsen without urgent emissions reductions."
        ),
        source="BBC News",
        category="Impact",
        published_at=_dt(91),
        region="North America",
    ),
    Article(
        id="imp-02",
        title="Flooding displaces 2 million in South Asia",
        body=(
            "Catastrophic monsoon flooding displaced over 2 million people across Bangladesh "
            "and northeastern India, destroying crops and critical infrastructure. Climate "
            "scientists attribute the severe flooding intensity to warming ocean temperatures "
            "and changed precipitation patterns. Aid organizations warn the loss and damage "
            "crisis will worsen without urgent adaptation investment."
        ),
        source="Al Jazeera",
        category="Impact",
        published_at=_dt(99),
        region="Asia",
    ),
    Article(
        id="imp-03",
        title="Pacific island nations face existential sea-level threat",
        body=(
            "New satellite data confirms sea-level rise is accelerating, with Tuvalu and "
            "Kiribati at risk of becoming uninhabitable by 2050. The loss of homeland "
            "represents an existential crisis for indigenous communities. Leaders demand "
            "wealthy nations take responsibility for climate-driven displacement and fund "
            "relocation support for affected populations."
        ),
        source="Reuters",
        category="Impact",
        published_at=_dt(107),
        region="Pacific",
    ),
    Article(
        id="imp-04",
        title="Renewable transition creates 1.2 million clean jobs",
        body=(
            "The accelerating renewable energy transition generated 1.2 million new clean "
            "energy jobs across the US in 2024, outpacing fossil fuel sector losses. Solar "
            "installation and wind turbine maintenance lead growth. Economists describe the "
            "shift as an economic opportunity, with sustainable industry offering better "
            "wages and improved long-term employment stability."
        ),
        source="IEA",
        category="Impact",
        published_at=_dt(115),
        region="North America",
    ),
    Article(
        id="imp-05",
        title="Severe drought threatens food security in East Africa",
        body=(
            "A third consecutive failed rainy season has pushed East Africa to the brink "
            "of a severe food crisis. Drought conditions driven by the climate crisis have "
            "damaged crops, depleted water sources, and forced mass livestock deaths. "
            "Humanitarian organizations warn of catastrophic famine risk without immediate "
            "aid. Climate scientists link the extreme drought directly to rising global "
            "temperatures and disrupted ocean circulation."
        ),
        source="WFP",
        category="Impact",
        published_at=_dt(122),
        region="Africa",
    ),
    Article(
        id="imp-06",
        title="Green hydrogen production reaches cost parity",
        body=(
            "Green hydrogen produced from renewable electricity has reached cost parity "
            "with fossil-derived hydrogen in three major markets, a milestone analysts "
            "describe as transformative for the industrial decarbonization transition. "
            "The breakthrough enables clean hydrogen to replace fossil fuels in steel, "
            "cement, and shipping — sectors difficult to electrify. Investment is "
            "accelerating rapidly."
        ),
        source="BloombergNEF",
        category="Technology",
        published_at=_dt(130),
        region="Global",
    ),
]

ARTICLES_BY_ID: dict[str, Article] = {a.id: a for a in SAMPLE_ARTICLES}
CATEGORIES: list[str] = sorted({a.category for a in SAMPLE_ARTICLES})
REGIONS: list[str] = sorted({a.region for a in SAMPLE_ARTICLES})

"""
Candidate Site Ranking Engine

Ranks multiple evaluated deployment sites based on their
overall site suitability score.
"""


def rank_candidate_sites(
    site_results: list[dict],
) -> list[dict]:
    """
    Rank candidate sites from highest to lowest score.

    Parameters
    ----------
    site_results : list[dict]
        List of evaluated site results.

        Example:
        [
            {
                "site_name": "Karur",
                "overall_score": 89.95
            },
            {
                "site_name": "Krishnagiri",
                "overall_score": 88.95
            }
        ]

    Returns
    -------
    list[dict]
        Ranked sites with rank numbers.
    """

    if not isinstance(site_results, list):
        raise TypeError(
            "site_results must be a list."
        )

    ranked_sites = []

    for site in site_results:

        if not isinstance(site, dict):
            raise TypeError(
                "Each site result must be a dictionary."
            )

        if "site_name" not in site:
            raise ValueError(
                "Each site must contain 'site_name'."
            )

        if "overall_score" not in site:
            raise ValueError(
                "Each site must contain 'overall_score'."
            )

        ranked_sites.append(
            {
                **site,
                "overall_score": float(
                    site["overall_score"]
                ),
            }
        )

    # Highest score first
    ranked_sites.sort(
        key=lambda site: site["overall_score"],
        reverse=True,
    )

    # Assign rank
    for rank, site in enumerate(
        ranked_sites,
        start=1,
    ):
        site["rank"] = rank

    return ranked_sites


def get_best_site(
    site_results: list[dict],
) -> dict | None:
    """
    Return the most suitable site.

    Returns None when no candidate sites are provided.
    """

    ranked_sites = rank_candidate_sites(
        site_results
    )

    if not ranked_sites:
        return None

    return ranked_sites[0]


def print_site_ranking(
    site_results: list[dict],
) -> None:
    """
    Display candidate site ranking in the terminal.
    """

    ranked_sites = rank_candidate_sites(
        site_results
    )

    print()
    print("======================================")
    print("CANDIDATE SITE RANKING")
    print("======================================")

    if not ranked_sites:
        print("No candidate sites available.")
        return

    for site in ranked_sites:

        print(
            f"{site['rank']}. "
            f"{site['site_name']} "
            f"-> "
            f"{site['overall_score']:.2f} / 100"
        )

    print("--------------------------------------")

    best_site = ranked_sites[0]

    print(
        f"BEST SITE : "
        f"{best_site['site_name']}"
    )

    print(
        f"SCORE     : "
        f"{best_site['overall_score']:.2f} / 100"
    )

    print("======================================")
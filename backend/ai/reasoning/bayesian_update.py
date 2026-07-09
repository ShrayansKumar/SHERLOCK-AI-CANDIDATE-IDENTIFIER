class BayesianUpdater:
    """
    Updates confidence using a Bayesian posterior formula:
        P(candidate | evidence) ∝ P(evidence | candidate) × P(candidate)

    Simplified to a linear credibility-weighted update for
    runtime efficiency without a full probabilistic graph.
    """

    def update(
        self,
        prior: float,
        likelihood_positive: float,
        likelihood_negative: float,
    ) -> float:
        """
        Compute posterior confidence given prior and likelihoods.

        Args:
            prior: Current confidence [0, 1].
            likelihood_positive: P(evidence | is candidate) [0, 1].
            likelihood_negative: P(evidence | not candidate) [0, 1].

        Returns:
            Posterior confidence [0, 1].
        """
        if likelihood_positive + likelihood_negative == 0:
            return prior

        numerator = likelihood_positive * prior
        denominator = (
            likelihood_positive * prior
            + likelihood_negative * (1.0 - prior)
        )

        if denominator == 0:
            return prior

        posterior = numerator / denominator
        return round(max(0.0, min(1.0, posterior)), 4)

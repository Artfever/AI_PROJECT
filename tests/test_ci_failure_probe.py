"""Temporary negative verification; this branch must never be merged."""


def test_ci_rejects_a_failing_test():
    assert False, "intentional CI failure probe"

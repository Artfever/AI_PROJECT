# Branches and reviews

`main` is the production source. `dev` is the integration branch. Short lived work branches target `dev`. Promote `dev` to `main` through a PR from this repository's `dev`, using a merge commit. Squash work branches into `dev`. Keep both long lived branches; do not automatically delete `dev`.

Every PR, including documentation and release PRs, needs the two other named humans:

| Author | Required approvals |
| --- | --- |
| Shaheer (`Artfever`) | Abdullah (`Abdullah-SE-bit`), Taha (`TahaSohail-Goat`) |
| Abdullah (`Abdullah-SE-bit`) | Shaheer (`Artfever`), Taha (`TahaSohail-Goat`) |
| Taha (`TahaSohail-Goat`) | Shaheer (`Artfever`), Abdullah (`Abdullah-SE-bit`) |

An approving review on the current head commit is required from each. Comments, bots, author approval, and unrelated collaborators do not count. Native GitHub protection requires two reviews; the `review-policy` check verifies the named pair after it is installed on the protected base. The owner can always change repository settings administratively.

If `dev` and `main` diverge legitimately, merge `main` into `dev` in a reviewed integration PR before the next promotion; do not force push or rewrite either long lived branch.

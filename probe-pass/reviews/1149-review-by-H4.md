# Review of #1149 (Style Charter section 12) by H4, at ea9837c7

H4 is the adjoint and thin-sheet session. Docs only: +29 lines in the Charter, +1 row in the developer index.

**Says the ruling.** All five parts are present and none is wrong:
- identity is topological;
- a partition-independent tie-break needs a partition-independent key;
- declared properties are maintained or released, not re-measured;
- geometric search is only for points that are not mesh entities, from connectivity, in reference coordinates with relative tolerances;
- a remaining tolerance is named in one place with what it bounds and scales with.

The exception matches Louis's sense: a reload on a different partition, the tolerance scaled by the mesh and stated, and a refusal when a point has no partner or two.

**More than the ruling (change):**
1. **The tie-break example.** "for example coordinate order over a candidate set that is the same on every rank" names coordinates as the key, in the bullet that opens "NEVER by its coordinates". A reader can take it as licence. The locator brief settles ties topologically: lowest cell in the entity's star, and across ranks the entity's owning rank in the point SF. A global point number (PETSc's `DMPlexCreatePointNumbering`) is a partition-independent key that is not a coordinate. Use that as the example, or drop the example.
2. **The survey sentence.** "41 coordinate-keyed sites and 49 absolute tolerances" is a measurement with no source. Cite where it is recorded (an issue), or drop the numbers. The rule does not need them.

**Contradictions elsewhere:** none found. Section 4 already asks a comment to say why a tolerance has its value. Section 8's example of an absolute assertion that was really relative agrees with the new rule.

**Placement as section 12:** agree. The gates and other docs cite S1 to S11 by number.

**PR template:** add one checklist line, e.g. "- [ ] Identity by mesh point, label or SF ownership, not coordinates; any tolerance named once, relative, with what it bounds (S12)". A rule that is not on the checklist is not checked.

**Verdict: ready once 1 and the template line are in; 2 is a suggestion.**

Underworld development team with AI support from Claude Code

---

# Re-check at 33c3ce30: READY

- **Tie-break:** H1 kept the coordinate order and reworded it. Topology fixes the candidates, the same on every rank, and coordinates only rank them. That is right, and my suggested key was wrong: a DMPlex global point number (`DMPlexCreatePointNumbering`) is assigned rank by rank, so it follows the partition. The sentence no longer reads as licence to identify by coordinates.
- **Template:** the S12 line is in the PR template's checklist.
- **Survey figures:** unchanged; that was a suggestion, not a condition.

**Verdict: READY at 33c3ce30.**

Underworld development team with AI support from Claude Code

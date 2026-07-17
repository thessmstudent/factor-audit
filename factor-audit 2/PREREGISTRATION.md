# Pre-Registration — Factor Audit

**Date committed:** 2026-07-16
**Committed before:** any post-2010 factor premium was inspected as part of this project.

This file exists so the tests below are checkable against a timestamp, not just claimed after
the fact. If you edit these hypotheses after this date, edit this file's changelog at the
bottom instead of silently rewriting the hypotheses — that's the entire point of pre-registration.

## Hypotheses

**H1.** Post-2010 annualized premia for each of the five canonical factors (Mkt-RF, SMB, HML,
RMW, UMD) will be smaller than their full-sample historical premia, consistent with McLean &
Pontiff's (2016) post-publication decay finding.

**H2.** After applying a realistic transaction-cost haircut (10–20 bps round-trip, scaled by
estimated monthly turnover), at least one canonical factor's premium becomes statistically
indistinguishable from zero at the Harvey-Liu-Zhu adjusted threshold (t-stat ≈ 3.0).

**H3 (stretch, depends on free-tier fundamentals data holding up — see project plan Section 2.5).**
A regularized multi-factor combination will show a higher in-sample Sharpe ratio than any single
factor, but that improvement will substantially shrink or disappear under out-of-sample
walk-forward testing, once corrected for the number of variants tried via the deflated Sharpe
ratio (Bailey & López de Prado, 2014).

## Split definition

- **Full sample:** earliest available Ken French monthly data (July 1963 for the 5-factor set) through the present.
- **"Publication era" / in-sample:** through December 2009.
- **"Post-widespread-publication" / out-of-sample:** January 2010 through present.

This split date is a judgment call, not a precise event date — most of these factors were
published well before 2010, and 2010 is chosen as a round, defensible cutoff that leaves a
substantial (15+ year) out-of-sample window. State this plainly in the write-up rather than
implying the date has special significance.

## What counts as confirming vs. disconfirming each hypothesis

- H1 confirmed: post-2010 mean premium < full-sample mean premium, for a given factor.
- H1 disconfirmed (for that factor): post-2010 mean premium ≥ full-sample mean premium.
- H2 confirmed: at least one factor's cost-adjusted post-2010 t-stat falls below 3.0.
- H2 disconfirmed: all five factors remain significant at t ≥ 3.0 after the cost haircut.
- A disconfirmed hypothesis is a valid, reportable result — it is not a failed project.

## Changelog

- 2026-07-16 — initial pre-registration committed.

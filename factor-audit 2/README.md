# Factor Audit

Does the market still pay for the factors academic finance says it should?

Hundreds of published papers claim to have found a way to beat the market. This project
tests whether five of the most established ones — market, size, value, profitability, and
momentum — still earn a statistically meaningful premium in recent data and after realistic
trading costs, or whether their measured edge has decayed since publication.

Companion project to [Apex Quant](#) (a Monte Carlo-based trading platform). Where Apex Quant
shows a working quantitative system, this project tests whether systems like it should be
trusted — using pre-registration, multiple-testing correction, and out-of-sample validation
to avoid fooling myself. See `PREREGISTRATION.md` for the exact, dated hypotheses.

## Status

Week 1-2 slice: data pipeline, statistical toolkit, and cost model are built and unit-tested.
The dashboard (Streamlit) and the written report are not yet built — see the project plan for
the full timeline.

## Structure

```
PREREGISTRATION.md          dated hypotheses (H1, H2, H3), committed before results were run
src/factor_audit/
  data/fetch_french.py       downloads & caches Ken French's published factor returns
  factors/costs.py           explicit, cited transaction-cost haircut model
  stats/tests.py             t-tests, HLZ significance bar, deflated Sharpe ratio, bootstrap CI
  analysis/decay.py          runs H1/H2 against the cached data
tests/                       pytest unit + integration tests (synthetic data, no network needed)
app/                         Streamlit dashboard (not yet built)
```

## Setup

```bash
pip install -e .
pip install -r requirements.txt
```

## Running the tests

```bash
pytest tests/ -v
```

All statistical logic is unit-tested against synthetic data and does not require network
access. The one module that does — `fetch_french.py` — pulls directly from Ken French's
Dartmouth Data Library via `pandas_datareader`.

## Running the actual analysis

Requires internet access (not available in a network-restricted sandbox):

```bash
python -m factor_audit.data.fetch_french   # downloads & caches the factor data
python -m factor_audit.analysis.decay      # runs H1/H2 and prints the results table
```

## Data sources and limitations

- **Ken French Data Library** (free, official, CRSP-derived) — the load-bearing data for H1/H2.
- **WRDS/CRSP/Compustat** — not used. Individual WRDS accounts require current university
  enrollment, so this project deliberately does not depend on it. See the project plan for
  how the free-data strategy was chosen and what it means for the (optional, stretch) H3.

## Citations

See the project plan document (`Factor_Audit_Project_Plan.docx`) Section 2.2 for full citations:
Fama & French (1993, 2015), Carhart (1997), Hou, Xue & Zhang (2015), Cochrane (2011),
Harvey, Liu & Zhu (2016), McLean & Pontiff (2016), Bailey & López de Prado (2014).

# Data Model: Loan Pricing Engine

**Branch**: `001-loan-pricing-engine` | **Date**: 2026-05-30

All monetary fields use `decimal.Decimal`. Rate fields are expressed as annual
percentages (e.g., `6.5` = 6.5%).

---

## Entities

### LoanScenario

Represents a single pricing request. The discriminated union of `FixedScenario` and
`ArmScenario` ensures each variant carries exactly the fields it needs.

**FixedScenario** (loan_type = "fixed")

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `loan_type` | Literal["fixed"] | required | Discriminator field |
| `home_price` | Decimal | > 0 | USD, cents precision |
| `down_payment` | Decimal or Percentage | ≥ 0, < home_price | Dollar or % of home_price |
| `term_years` | int | > 0, ≤ 50 | Positive integer; common presets: 10,15,20,30 |
| `annual_rate` | Decimal | ≥ 0, ≤ 30 | Percent (e.g. 6.5); 0 accepted (zero-interest) |
| `fee_schedule` | FeeSchedule | optional | Defaults to empty (no fees) |

**ArmScenario** (loan_type = "arm")

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `loan_type` | Literal["arm"] | required | Discriminator field |
| `home_price` | Decimal | > 0 | USD |
| `down_payment` | Decimal or Percentage | ≥ 0, < home_price | Dollar or % |
| `term_years` | int | > 0, ≤ 50 | Full amortisation term |
| `initial_rate` | Decimal | ≥ 0, ≤ 30 | Percent, initial fixed-period rate |
| `arm_params` | ArmParameters | required | See below |
| `fee_schedule` | FeeSchedule | optional | Defaults to empty |

**Validation rules (both variants)**:
- `down_payment` < `home_price` (after resolving percentage to dollar amount)
- Derived `loan_amount` = `home_price` − `down_payment` MUST be > 0
- `term_years` × 12 MUST be a positive integer (months)

---

### ArmParameters

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `fixed_period_years` | int | ≥ 1 | Initial fixed-rate period (e.g. 5 for a 5/1 ARM) |
| `adjustment_period_years` | int | ≥ 1 | How often rate adjusts after fixed period (e.g. 1) |
| `initial_cap` | Decimal | ≥ 0 | Max rate change at first adjustment |
| `periodic_cap` | Decimal | > 0, ≤ lifetime_cap | Max rate change per subsequent adjustment |
| `lifetime_cap` | Decimal | > 0 | Max total rate change over loan life |

**Validation rules**:
- `periodic_cap` ≤ `lifetime_cap`
- `initial_rate` + `lifetime_cap` ≤ 30 (sanity ceiling)
- `fixed_period_years` < `term_years`

---

### FeeSchedule

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `fees` | list[Fee] | ≥ 0 items | Empty list = no prepaid finance charges |

### Fee

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `name` | str | non-empty, ≤ 100 chars | Human-readable label |
| `amount` | Decimal | > 0 | USD; included in APR amount-financed calc |

---

### PricingResult

Output for a single `LoanScenario`.

| Field | Type | Notes |
|-------|------|-------|
| `scenario_id` | UUID | Echoed from request; generated if not provided |
| `loan_type` | str | "fixed" or "arm" |
| `loan_amount` | Decimal | home_price − down_payment |
| `monthly_payment` | Decimal | P&I only; rounded ROUND_HALF_UP to cents |
| `apr` | Decimal | Regulation Z actuarial APR; rounded per Reg Z rules |
| `total_interest` | Decimal | (monthly_payment × n) − loan_amount |
| `parameters_summary` | dict | Key inputs echoed for display/audit |
| `rate_type_label` | str | E.g. "Fixed 30-year" or "5/1 ARM 30-year" |

---

### ComparisonResult

Output for a batch comparison request (US3).

| Field | Type | Notes |
|-------|------|-------|
| `results` | list[PricingResultOrError] | One entry per submitted scenario |
| `comparison_id` | UUID | Identifies the batch request |

### PricingResultOrError

Each element is either a `PricingResult` or an `ErrorDetail`.

### ErrorDetail

| Field | Type | Notes |
|-------|------|-------|
| `scenario_id` | UUID | Identifies which scenario failed |
| `code` | str | Machine-readable error code (e.g. INVALID_RATE) |
| `message` | str | Human-readable description |
| `fields` | list[str] | Which input fields caused the error |

---

### AuditRecord

Immutable; written to stdout as a single JSON line per pricing request.

| Field | Type | Notes |
|-------|------|-------|
| `request_id` | UUID | Unique per HTTP request |
| `timestamp` | ISO-8601 UTC | Generated at request receipt |
| `loan_type` | str | "fixed" or "arm" |
| `scenario_count` | int | 1 for single; N for comparison |
| `inputs_hash` | str | SHA-256 of canonicalised scenario JSON (for reproducibility) |
| `outputs_summary` | dict | monthly_payment, apr per scenario (no PII) |
| `duration_ms` | int | Wall-clock time for the pricing computation |
| `error` | str or null | Populated only on validation/calculation failure |

---

## State Transitions

The engine is stateless — no stored state beyond the audit log. A request arrives,
is validated, priced, logged, and the result returned. There is no concept of a
"pending" or "in-progress" scenario.

---

## Relationships

```
ComparisonRequest ──contains──▶ 1..5 LoanScenario
LoanScenario ──is──▶ FixedScenario | ArmScenario
ArmScenario ──has──▶ ArmParameters
LoanScenario ──optionally has──▶ FeeSchedule ──contains──▶ 0..* Fee
LoanScenario ──produces──▶ PricingResult | ErrorDetail
ComparisonRequest ──produces──▶ ComparisonResult
Every request ──emits──▶ AuditRecord
```

# Feature Specification: Loan Pricing Engine

**Feature Branch**: `001-loan-pricing-engine`

**Created**: 2026-05-30

**Status**: Draft

**Input**: User description: "a loan pricing engine that calculates monthly payments and APR for fixed and variable rate home loans, supporting different loan terms and down payment amounts"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Calculate Fixed-Rate Loan Payment (Priority: P1)

A home buyer wants to understand the cost of a fixed-rate mortgage before committing.
They enter a home price, down payment amount, loan term, and interest rate. The system
returns the monthly payment amount and the Annual Percentage Rate (APR) that includes
all applicable fees.

**Why this priority**: This is the core value proposition. Without accurate fixed-rate
pricing, the engine has no viable output.

**Independent Test**: Can be fully tested by submitting a fixed-rate loan scenario
(e.g., $400,000 home, 20% down, 30-year term, 6.5% rate) and verifying monthly payment
and APR match reference calculations to within regulatory rounding tolerance.

**Acceptance Scenarios**:

1. **Given** a home price of $400,000, a 20% down payment, a 30-year term, and a 6.5%
   annual interest rate, **When** the user requests pricing, **Then** the system returns
   a monthly payment of $2,022.65 and an APR that accounts for all disclosed fees, all
   values rounded per Regulation Z rules.
2. **Given** a loan amount that results in a monthly payment, **When** any input is
   outside valid range (e.g., negative rate, zero term), **Then** the system returns a
   clear validation error and does not produce pricing output.
3. **Given** valid inputs with no additional fees, **When** pricing is requested,
   **Then** the APR equals the stated interest rate (within rounding tolerance).

---

### User Story 2 - Calculate Variable-Rate (ARM) Loan Payment (Priority: P2)

A home buyer considering an adjustable-rate mortgage (ARM) wants to see the initial
monthly payment and APR based on the initial fixed period rate. The system accepts the
initial rate, the adjustment period, rate caps (initial, periodic, lifetime), and the
loan term, then returns the initial payment and APR for disclosure purposes.

**Why this priority**: ARM products are a significant segment of the home loan market.
Without them, the engine covers only half of the standard product set.

**Independent Test**: Can be fully tested by submitting a 5/1 ARM scenario (e.g.,
$350,000 loan, 5.75% initial rate, 2/2/5 caps, 30-year term) and verifying the initial
payment and APR match reference calculations.

**Acceptance Scenarios**:

1. **Given** a $350,000 loan amount, a 5.75% initial rate, a 5/1 ARM structure, and
   2/2/5 caps, **When** pricing is requested, **Then** the system returns the correct
   initial monthly payment and APR for the initial fixed period.
2. **Given** ARM inputs where rate caps are inconsistent (e.g., periodic cap exceeds
   lifetime cap), **When** pricing is requested, **Then** the system returns a validation
   error describing the inconsistency.
3. **Given** valid ARM inputs, **When** pricing is requested, **Then** the output
   clearly labels the rate type as variable and indicates the initial fixed period.

---

### User Story 3 - Compare Multiple Loan Scenarios (Priority: P3)

A loan officer or borrower wants to compare two or more loan scenarios side by side
(e.g., 15-year vs. 30-year fixed, or fixed vs. ARM) to understand trade-offs in monthly
payment and total cost of borrowing.

**Why this priority**: Comparison is a high-value workflow but depends on Stories 1 and
2 being complete; it is not independently deployable without them.

**Independent Test**: Can be tested by submitting two valid scenario inputs and verifying
that the response returns pricing for each scenario with a total interest cost figure
and a clear label identifying each scenario.

**Acceptance Scenarios**:

1. **Given** two valid loan scenarios submitted together, **When** comparison is
   requested, **Then** the system returns monthly payment, APR, and total interest paid
   for each scenario, clearly labeled.
2. **Given** one valid and one invalid scenario submitted together, **When** comparison
   is requested, **Then** the system returns pricing for the valid scenario and a
   validation error for the invalid one; it does not suppress either result.

---

### Edge Cases

- What happens when the down payment equals or exceeds the home price?
- How does the system handle a loan term of 0 or a negative term?
- What happens when the interest rate is 0% (zero-interest loan)?
- How does the system handle non-standard term lengths (e.g., 7-year, 20-year)?
- What happens when ARM caps result in a maximum rate that produces an unaffordable
  payment (e.g., payment exceeds principal)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept home price, down payment amount, loan term (in
  years), and annual interest rate as inputs for fixed-rate loan pricing.
- **FR-002**: The system MUST calculate the monthly principal-and-interest payment using
  standard amortization formula, using decimal arithmetic to avoid floating-point error.
- **FR-003**: The system MUST calculate and return the APR, incorporating any disclosed
  fees, rounded per Regulation Z half-up rounding rules.
- **FR-004**: The system MUST accept initial rate, ARM structure (e.g., 5/1, 7/1),
  adjustment caps (initial, periodic, lifetime), and loan term as inputs for
  variable-rate loan pricing.
- **FR-005**: The system MUST validate all inputs at the boundary and return descriptive
  validation errors for out-of-range or logically inconsistent values before any
  calculation is performed.
- **FR-006**: The system MUST support standard loan terms of 10, 15, 20, and 30 years
  for both fixed and variable products.
- **FR-007**: The system MUST accept down payment as either a dollar amount or a
  percentage of home price.
- **FR-008**: The system MUST produce a complete audit record for every pricing request,
  capturing inputs, outputs, and a timestamp, per the Auditability principle.
- **FR-009**: The system MUST support batch input of multiple loan scenarios and return
  individual pricing results for each.
- **FR-010**: The system MUST clearly label each output with the loan type (fixed or
  variable) and the key parameters used.

### Key Entities

- **LoanScenario**: Represents a single pricing request; attributes include loan type,
  home price, down payment, term, rate(s), and fee schedule.
- **PricingResult**: The output for a scenario; attributes include monthly payment, APR,
  total interest paid, and loan type label.
- **FeeSchedule**: A collection of itemized fees (e.g., origination, points) included
  in APR calculation.
- **ArmParameters**: ARM-specific inputs: initial rate, adjustment period, and cap
  structure (initial, periodic, lifetime).
- **AuditRecord**: Immutable log entry capturing scenario inputs, result outputs,
  timestamp, and request identity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Monthly payment calculations match reference amortization values to within
  $0.01 for any standard loan scenario.
- **SC-002**: APR calculations comply with Regulation Z disclosure requirements and
  match reference values within the permitted rounding tolerance.
- **SC-003**: All invalid inputs are rejected with a descriptive error within one
  interaction step; no partial or silent failures occur.
- **SC-004**: A user can obtain pricing for a single fixed-rate scenario within
  3 interaction steps (enter inputs → request pricing → receive result).
- **SC-005**: Batch comparison of up to 5 scenarios returns all results in a single
  response with no scenario silently omitted.
- **SC-006**: Every pricing result is accompanied by a complete audit record; zero
  pricing responses are produced without a corresponding log entry.

## Assumptions

- Loan pricing is for U.S. residential mortgages; U.S. federal regulations (TILA,
  Regulation Z) apply.
- The engine calculates pricing only; it does not submit loan applications or connect
  to live rate feeds (rates are user-supplied inputs).
- Private mortgage insurance (PMI) is out of scope for v1; down payments below 20% are
  accepted but PMI cost is not added to the payment.
- The fee schedule for APR calculation is provided by the caller; the engine does not
  maintain a fee database.
- Non-standard term lengths (e.g., 7-year, 25-year) are treated as valid inputs if the
  value is a positive integer; the supported "standard" list in FR-006 defines common
  presets but does not restrict other values.
- Currency is USD; no multi-currency support is required.

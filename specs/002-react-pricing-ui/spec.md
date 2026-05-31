# Feature Specification: React Loan Pricing UI

**Feature Branch**: `002-react-pricing-ui`

**Created**: 2026-05-30

**Status**: Draft

**Input**: User description: "a React frontend for the home loan pricing engine — a single-page app with a form to enter home price, down payment, loan term, and interest rate, a toggle between fixed and ARM products, and a results panel showing monthly payment, APR, and total interest; include a comparison mode to price two scenarios side by side."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Price a Fixed-Rate Loan (Priority: P1)

A home buyer visits the app, selects "Fixed Rate", fills in the home price, down payment
(dollar amount or percentage), loan term, and interest rate, then submits the form. The
results panel immediately displays the monthly payment, APR, and total interest for the
loan. The buyer can adjust any input and re-submit to see updated results without leaving
the page.

**Why this priority**: This is the core value of the app. A user who can price a single
fixed-rate loan has everything they need to make an informed decision.

**Independent Test**: Can be fully tested by entering a $400,000 home price, $80,000
down payment, 30-year term, and 6.5% rate, then confirming the results panel shows a
monthly payment and APR without any page reload.

**Acceptance Scenarios**:

1. **Given** the app is open in single-scenario mode, **When** the user fills in all
   required fields for a fixed-rate loan and submits, **Then** the results panel shows
   monthly payment, APR, and total interest within 2 seconds.
2. **Given** a result is displayed, **When** the user changes any input and re-submits,
   **Then** the results panel updates with new values without a page reload.
3. **Given** the user leaves a required field blank and submits, **Then** the form
   highlights the missing field with an inline error message and does not submit.
4. **Given** the user enters an invalid value (e.g., a rate above 30%), **Then** the
   form shows an inline validation error before submission.

---

### User Story 2 - Price a Variable-Rate (ARM) Loan (Priority: P2)

A home buyer toggles the product selector to "Adjustable Rate (ARM)", and the form
expands to show ARM-specific fields: initial fixed period, adjustment interval, and rate
caps (initial, periodic, lifetime). The buyer fills in the fields and submits; the
results panel displays the initial monthly payment, APR (based on the initial rate held
constant), and a label identifying the ARM structure (e.g., "5/1 ARM").

**Why this priority**: ARM products are a major segment; the pricing engine already
supports them, and the UI must expose this to be feature-complete.

**Independent Test**: Can be tested by toggling to ARM mode, entering a 5/1 ARM with
5.75% initial rate and 2/2/5 caps, submitting, and confirming the label "5/1 ARM
30-year" appears in the results with a valid payment and APR.

**Acceptance Scenarios**:

1. **Given** the user selects "Adjustable Rate (ARM)", **When** the toggle is activated,
   **Then** the ARM-specific fields (fixed period, adjustment interval, caps) appear and
   the basic rate field label updates to "Initial Rate".
2. **Given** valid ARM inputs are entered and submitted, **Then** the results panel
   shows the initial monthly payment, APR, and a rate-type label (e.g., "5/1 ARM
   30-year").
3. **Given** the user enters inconsistent cap values (e.g., periodic cap exceeds
   lifetime cap), **Then** the form shows an inline error and does not submit.
4. **Given** the user switches back to Fixed Rate after entering ARM values, **Then**
   the ARM fields are hidden and the form resets to fixed-rate defaults.

---

### User Story 3 - Compare Two Loan Scenarios Side by Side (Priority: P3)

A home buyer activates comparison mode, which reveals a second scenario panel. Each
panel has its own independent product selector (fixed or ARM) and input form. After
filling in both panels and submitting, the results for both scenarios appear side by
side with monthly payment, APR, and total interest clearly labelled per scenario,
allowing direct comparison.

**Why this priority**: Comparison answers the most common home-buyer question ("is a
15-year or 30-year loan better for me?") and depends on Stories 1 and 2 being working
first.

**Independent Test**: Can be tested by entering a 30-year fixed scenario in panel A and
a 15-year fixed scenario in panel B, submitting both, and confirming two results cards
appear side by side each labelled with their scenario details.

**Acceptance Scenarios**:

1. **Given** the user activates comparison mode, **When** comparison is enabled, **Then**
   a second scenario panel appears alongside the first, and both can be independently
   configured.
2. **Given** both scenario panels have valid inputs and the user submits, **Then** two
   result cards appear side by side, each clearly labelled with the scenario type and
   key parameters.
3. **Given** one scenario is valid and the other has missing required fields, **When**
   the user submits, **Then** the valid scenario shows its result and the invalid one
   shows an inline validation error; neither result is hidden.
4. **Given** comparison mode is active, **When** the user deactivates it, **Then** the
   second panel is removed and only the first scenario remains.

---

### Edge Cases

- What happens if the pricing service is unavailable or returns an error?
- How does the app behave on a narrow mobile screen (< 375px width)?
- What happens if the user submits the form while a previous request is still loading?
- How does the results panel behave if the backend returns an unexpected field?
- What happens when the user clears all fields after a result is shown?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The app MUST display a single-page form with fields for home price, down
  payment, loan term (in years), and interest rate.
- **FR-002**: The app MUST provide a product toggle to switch between Fixed Rate and
  Adjustable Rate (ARM) modes.
- **FR-003**: When ARM mode is selected, the form MUST reveal additional fields for
  fixed period (years), adjustment interval (years), and rate caps (initial, periodic,
  lifetime).
- **FR-004**: The app MUST validate all inputs inline before submission and display
  field-level error messages for invalid or missing values.
- **FR-005**: The app MUST submit the form data to the pricing engine and display the
  returned monthly payment, APR, and total interest in a results panel.
- **FR-006**: The results panel MUST include a rate-type label (e.g., "Fixed 30-year"
  or "5/1 ARM 30-year") identifying the priced product.
- **FR-007**: The app MUST provide a comparison mode toggle that reveals a second,
  independent scenario form alongside the first.
- **FR-008**: In comparison mode, each scenario MUST be independently configurable
  (different product types, different inputs) and submitted together.
- **FR-009**: In comparison mode, results for both scenarios MUST be displayed side by
  side, each labelled with its scenario identifier.
- **FR-010**: If one scenario in comparison mode fails validation or returns an error,
  the other scenario's result MUST still be displayed.
- **FR-011**: The app MUST display a clear loading indicator while waiting for pricing
  results and prevent duplicate submissions.
- **FR-012**: The app MUST display a user-friendly error message if the pricing service
  is unavailable or returns an unexpected error.
- **FR-013**: The down payment field MUST accept both a dollar amount and a percentage
  of the home price (e.g., "20%").
- **FR-014**: The app MUST work correctly on desktop screens (≥ 1024px) and tablet
  screens (≥ 768px). Mobile layout is desirable but out of scope for v1.

### Key Entities

- **ScenarioForm**: A form capturing one loan scenario's inputs; attributes include
  product type, home price, down payment, term, rate, and (for ARM) cap structure.
- **PricingResult**: The displayed output for one scenario; attributes include monthly
  payment, APR, total interest, and rate-type label.
- **ComparisonView**: The side-by-side layout holding two ScenarioForms and their
  corresponding PricingResults.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can complete a fixed-rate loan pricing from entering the first field
  to seeing results in under 60 seconds on first use.
- **SC-002**: Pricing results appear within 2 seconds of form submission under normal
  network conditions.
- **SC-003**: All required field validation errors are visible before a network request
  is made; zero invalid requests reach the pricing service.
- **SC-004**: A user can switch between Fixed Rate and ARM modes without losing
  previously entered values in the shared fields (home price, down payment, term).
- **SC-005**: In comparison mode, two independent scenarios can be configured and
  submitted in a single interaction, with both results visible simultaneously.
- **SC-006**: Service errors are presented to the user in plain language within 2
  seconds of the failure occurring; the user can retry without refreshing the page.

## Assumptions

- The pricing engine API (from feature 001) is running locally on `http://localhost:8000`
  during development; the frontend proxies requests to it.
- No authentication or user accounts are required for v1; the app is stateless between
  page loads.
- Down payment defaults to a dollar-amount input; a "%" suffix triggers percentage mode.
- Loan term options are presented as a select (10, 15, 20, 30 years) rather than a
  free-text field to reduce invalid input.
- The app displays results for the current session only; no history or saved scenarios
  are required for v1.
- Desktop-first layout (≥ 1024px); tablet layout (≥ 768px) is a stretch goal included
  in acceptance but not blocking. Mobile (< 768px) is out of scope for v1.
- The comparison mode limit matches the pricing API limit: maximum 2 scenarios (not 5),
  to keep the UI layout manageable.

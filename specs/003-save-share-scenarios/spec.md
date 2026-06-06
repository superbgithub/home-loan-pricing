# Feature Specification: Save & Share Loan Pricing Scenarios

**Feature Branch**: `003-save-share-scenarios`

**Created**: 2026-06-05

**Status**: Draft

**Input**: User description: "Save and share loan pricing scenarios. Users can save a scenario they've configured (fixed or ARM loan inputs) with a name, see a list of their saved scenarios, reload a saved scenario back into the form to view or re-price it, rename or delete saved scenarios, and generate a shareable link/code that lets someone else open the same scenario with its inputs pre-filled. Builds on the existing single/comparison pricing UI (feature 002) and the loan pricing engine (feature 001)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save a configured scenario (Priority: P1)

A user has filled in the loan pricing form (a fixed-rate or ARM scenario) and wants to keep it for later. They give the scenario a name and save it. The saved scenario captures all the inputs they entered so it can be brought back exactly as configured.

**Why this priority**: Saving is the foundational capability — without it, none of the list, reload, rename, delete, or share behaviours have anything to operate on. A user who can only save and reload already gets standalone value (no need to re-type inputs).

**Independent Test**: Fill in a valid fixed-rate scenario, save it under a name, refresh the application, and confirm the scenario still appears in the saved list with the same inputs.

**Acceptance Scenarios**:

1. **Given** a completed, valid fixed-rate scenario in the form, **When** the user saves it with the name "Starter Home 30yr", **Then** the scenario is persisted and appears in the saved scenarios list labelled "Starter Home 30yr".
2. **Given** a completed, valid ARM scenario in the form, **When** the user saves it with a name, **Then** all ARM-specific inputs (fixed period, adjustment period, initial/periodic/lifetime caps) are captured in the saved scenario.
3. **Given** the user attempts to save without entering a name, **When** they confirm the save, **Then** the system prevents the save and prompts for a name.
4. **Given** the saved scenarios persist locally, **When** the user closes and reopens the application, **Then** previously saved scenarios are still listed.

---

### User Story 2 - Reload a saved scenario to view or re-price (Priority: P1)

A user opens their list of saved scenarios and selects one. Its inputs are loaded back into the form so they can review it, re-price it, or use it as a starting point for a new variation.

**Why this priority**: Reloading is the immediate payoff for saving and the most common reason a user saves at all. Together with Story 1 it forms the minimum viable product.

**Independent Test**: With at least one saved scenario present, select it from the list and confirm the form is populated with exactly the saved inputs and produces a pricing result on demand.

**Acceptance Scenarios**:

1. **Given** a saved fixed-rate scenario, **When** the user selects it from the list, **Then** the form is populated with the saved inputs (home price, down payment, term, rate).
2. **Given** a saved ARM scenario, **When** the user selects it, **Then** the form switches to ARM mode and populates all ARM-specific inputs.
3. **Given** a reloaded scenario, **When** the user requests pricing, **Then** the pricing result reflects the reloaded inputs.
4. **Given** a reloaded scenario, **When** the user edits an input and saves it as a new scenario, **Then** the original saved scenario remains unchanged.

---

### User Story 3 - Manage the saved scenarios list (rename & delete) (Priority: P2)

A user maintains their collection of saved scenarios: they can rename a scenario to keep names meaningful and delete scenarios they no longer need.

**Why this priority**: Once users accumulate scenarios, list hygiene matters, but the feature delivers value without it. It is a clear second tier after save/reload.

**Independent Test**: With multiple saved scenarios, rename one and confirm the new name appears in the list; delete one and confirm it is removed and does not return after reopening the application.

**Acceptance Scenarios**:

1. **Given** a saved scenario, **When** the user renames it, **Then** the list reflects the new name and the inputs are unchanged.
2. **Given** a saved scenario, **When** the user deletes it, **Then** it is removed from the list and does not reappear after reopening the application.
3. **Given** a delete action, **When** the user is asked to confirm, **Then** the scenario is only removed after explicit confirmation.
4. **Given** the user renames a scenario to a name already used by another saved scenario, **When** they confirm, **Then** the system warns about the duplicate name before proceeding.

---

### User Story 4 - Share a scenario via link/code (Priority: P2)

A user wants to show a scenario to someone else (e.g. a partner or loan officer). They generate a shareable link or code from a saved or current scenario. When the recipient opens it, the application loads with that scenario's inputs pre-filled, ready to view or re-price — without the recipient needing an account or the sender's saved data.

**Why this priority**: Sharing extends the feature's reach beyond a single user but depends on save/reload mechanics being in place. It is high-value but not required for the MVP.

**Independent Test**: Generate a share link from a configured scenario, open that link in a fresh browser session (no saved scenarios), and confirm the form pre-fills with the shared inputs.

**Acceptance Scenarios**:

1. **Given** a configured scenario, **When** the user generates a share link, **Then** the system produces a link/code the user can copy.
2. **Given** a share link for a fixed-rate scenario, **When** a recipient opens it in a fresh session, **Then** the form is pre-filled with the shared inputs and can be priced.
3. **Given** a share link for an ARM scenario, **When** a recipient opens it, **Then** the form switches to ARM mode with all ARM inputs pre-filled.
4. **Given** a recipient opens a shared scenario, **When** they save it, **Then** it is added to their own saved scenarios list as a new entry.
5. **Given** a share link that has been tampered with or is malformed, **When** a recipient opens it, **Then** the system shows a clear "could not load shared scenario" message and falls back to an empty form.

---

### Edge Cases

- What happens when the user tries to save a scenario whose inputs are incomplete or invalid? (Saving requires a valid, priceable set of inputs; otherwise the user is prompted to fix the inputs first.)
- What happens when local storage is full or unavailable? (The user is informed the scenario could not be saved and existing data is not corrupted.)
- How does the system handle a saved scenario created under an older input format after the form has changed? (Unrecognised or missing fields are flagged and the scenario is loaded as far as possible, or clearly marked as unloadable rather than silently mis-pricing.)
- What happens when two scenarios are given the same name? (Permitted but the user is warned; scenarios are distinguished internally regardless of name.)
- What happens when a share link encodes values outside accepted ranges (e.g. negative amounts)? (The shared inputs are validated on load and the user sees validation errors just as if they had typed them.)
- What happens when a very large number of scenarios is saved? (The list remains usable and ordered predictably.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When the user chooses to save the current scenario and provides a name, the system shall persist the scenario's product type and all associated inputs (for fixed: home price, down payment, term, rate; for ARM: home price, down payment, term, initial rate, fixed period, adjustment period, initial cap, periodic cap, lifetime cap) together with the name.
- **FR-002**: If the user attempts to save a scenario without a name, then the system shall reject the save and prompt the user to supply a name.
- **FR-003**: If the user attempts to save a scenario whose inputs are invalid or incomplete, then the system shall reject the save and surface the relevant validation errors.
- **FR-004**: The system shall persist saved scenarios across application restarts so that they remain available when the user returns.
- **FR-005**: The system shall present a list of the user's saved scenarios identified by their names, in a predictable order.
- **FR-006**: When the user selects a saved scenario from the list, the system shall load its inputs into the pricing form, including switching the form to the correct product type (fixed or ARM).
- **FR-007**: When a saved scenario has been loaded, the system shall allow the user to re-price it using the existing pricing engine without re-entering inputs.
- **FR-008**: When the user renames a saved scenario, the system shall update its displayed name while leaving its inputs unchanged.
- **FR-009**: When the user deletes a saved scenario, the system shall remove it from the list and from persistent storage after the user confirms the deletion.
- **FR-010**: If the user renames or saves a scenario with a name already in use, then the system shall warn about the duplicate before completing the action while still permitting it.
- **FR-011**: When the user requests to share a scenario, the system shall generate a shareable link or code that encodes the scenario's inputs and can be copied by the user.
- **FR-012**: When a recipient opens a valid share link or code, the system shall pre-fill the pricing form with the encoded inputs, set the correct product type, and make the scenario available to view, re-price, or save.
- **FR-013**: If a share link or code is malformed, tampered with, or encodes values that fail validation, then the system shall display a clear error and fall back to an empty (or partially loaded but flagged) form rather than producing a misleading price.
- **FR-014**: The system shall allow a recipient to save a shared scenario into their own saved scenarios list as a new, independent entry.
- **FR-015**: Where loading a saved or shared scenario, the system shall not silently discard or alter input values; any unrecognised or out-of-range values shall be surfaced to the user.
- **FR-016**: The system shall keep each saved scenario independent, so editing or re-saving one does not modify any other saved scenario.

### Key Entities *(include if feature involves data)*

- **Saved Scenario**: A named, persisted record of a single loan pricing configuration. Attributes: a user-visible name, a product type (fixed or ARM), the complete set of loan inputs for that product type, and a creation/last-updated reference for ordering. Each saved scenario is independent of the others. Saved scenarios belong to the user's local collection.
- **Shareable Scenario Reference**: A portable, self-contained encoding of a single scenario's product type and inputs that can be transmitted to another person and decoded back into a pre-filled form. It carries no reference to the sender's saved collection or identity.
- **Loan Inputs**: The existing set of pricing inputs from feature 001/002 (home price, down payment, term, rate(s), and ARM parameters), reused unchanged as the payload of both saved scenarios and shareable references.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can save a configured scenario and reload it into the form in under 10 seconds, with zero re-typing of inputs.
- **SC-002**: 100% of input fields present when a scenario is saved are restored exactly when it is reloaded (no data loss across a save/reload cycle).
- **SC-003**: Saved scenarios persist across at least one application restart for 100% of successful saves.
- **SC-004**: A recipient opening a valid share link sees the scenario's inputs pre-filled without creating an account or receiving any of the sender's other data.
- **SC-005**: 100% of malformed or tampered share links result in a clear error message and never produce a pricing result from corrupted inputs.
- **SC-006**: A user can rename or delete a saved scenario and see the list reflect the change immediately, with deletions persisting across restart.

## Assumptions

- **Storage model**: Saved scenarios are stored locally in the user's browser (per-device, per-browser), consistent with the current application having no user accounts or server-side persistence. Cross-device sync and server-side accounts are out of scope for this version.
- **Sharing model**: Share links/codes are self-contained — the scenario's inputs are encoded directly into the link/code, so no server-side storage or lookup is required and recipients need no account. This keeps the application stateless on the server side, consistent with features 001 and 002.
- **No authentication**: There is no login; "the user's saved scenarios" means whatever is stored in the current browser.
- **Reuse of existing inputs and pricing**: The scenario payload reuses the exact loan input model and validation rules from features 001/002; this feature adds persistence, listing, and sharing around them, not new pricing logic.
- **Privacy**: Loan inputs are not personally identifying on their own; share links contain only loan parameters, no borrower identity. No PII is persisted or transmitted by this feature.
- **Scope boundaries**: Comparison mode (scenario A vs B) may reuse saved scenarios as its A/B inputs, but bulk operations, folders/tags, export to file formats, and collaborative editing are out of scope for this version.
- **Capacity**: A practical local collection (on the order of dozens of scenarios) is assumed; pagination or search of very large collections is out of scope for this version.

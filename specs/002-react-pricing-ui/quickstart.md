# Quickstart: React Loan Pricing UI

**Branch**: `002-react-pricing-ui` | **Date**: 2026-05-30

Use this guide to verify the frontend works end-to-end after implementation.

---

## Prerequisites

- Node.js 20+
- The backend pricing engine running on `http://localhost:8000`
  (see `specs/001-loan-pricing-engine/quickstart.md` to start it)

---

## 1. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## 2. Start the development server

```bash
npm run dev
```

Expected output:
```
  VITE v6.x ready in XXXms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Open `http://localhost:5173` in a browser.

---

## 3. Price a fixed-rate loan

1. Confirm the "Fixed Rate" toggle is selected (default).
2. Enter:
   - Home Price: `400000`
   - Down Payment: `80000`
   - Loan Term: `30 years`
   - Annual Rate: `6.5`
3. Click **Get Quote**.
4. Verify the results panel shows:
   - Monthly Payment: `$2,022.62`
   - APR: `6.500%`
   - Rate Type: `Fixed 30-year`

---

## 4. Price an ARM loan

1. Click the **Adjustable Rate (ARM)** toggle.
2. Confirm the ARM fields appear (Fixed Period, Adjustment Interval, caps).
3. Enter:
   - Home Price: `350000`
   - Down Payment: `70000`
   - Loan Term: `30 years`
   - Initial Rate: `5.75`
   - Fixed Period: `5`
   - Adjustment Interval: `1`
   - Initial Cap: `2`
   - Periodic Cap: `2`
   - Lifetime Cap: `5`
4. Click **Get Quote**.
5. Verify the results panel shows Rate Type: `5/1 ARM 30-year`.

---

## 5. Use comparison mode

1. Click **Compare Two Scenarios**.
2. Confirm a second scenario panel appears.
3. In Panel A: Fixed Rate, $400,000 home, $80,000 down, 30 years, 6.5%.
4. In Panel B: Fixed Rate, $400,000 home, $80,000 down, 15 years, 6.0%.
5. Click **Get Quotes** (or each panel's individual submit).
6. Verify both result cards appear side by side, each labelled with scenario details.

---

## 6. Test validation

1. Leave the Home Price field blank and click **Get Quote**.
2. Verify an inline error appears on the Home Price field — no network request is made.
3. Enter an Annual Rate of `35` (above the 30% cap).
4. Verify an inline error appears on the rate field.

---

## 7. Run the test suite

```bash
npm run test
```

All tests should pass with a green summary.

---

## 8. Build for production

```bash
npm run build
```

Verify `frontend/dist/` is populated with static assets and `index.html`.

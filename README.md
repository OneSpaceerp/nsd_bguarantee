# Nest Bank Guarantee (`nsd_bguarantee`)

Bank Guarantee Management Application for **ERPNext v16** / **Frappe v16**.

Developed and maintained by **Nest Software Development**.

---

## Features

- **Comprehensive Guarantee Lifecycle**:
  - Issue, Extend, Expire, and Return guarantees.
  - Multi-purpose support: Bank Guarantee, Cheques, Cash, Deductions.
  - Facilities management: With Facilities vs. Without Facilities split computation.
- **Automated Financial Accounting**:
  - Automatic Journal Entry creation upon guarantee issuance.
  - Automatic Journal Entry reversal / return entries upon guarantee return.
  - Dynamic commission, bank deposit, margin, and credit/debit account handling.
- **Reporting & Analysis**:
  - Detailed Bank Guarantee Script Report with validity expiration warning indicators.
  - Dedicated Bank Guarantee Workspace with shortcuts and transaction links.
- **ERPNext v16 Native Architecture**:
  - Flit-core build system with Python $\ge$ 3.14.
  - Conflict-free fixtures and document event hooks.
  - Modern client-side form controls and query filters.

---

## Installation

### Prerequisites

- Frappe Bench running Python $\ge$ 3.14
- Frappe Framework v16 (`version-16`)
- ERPNext v16 (`version-16`)

### Steps

```bash
# Get the app
bench get-app https://github.com/OneSpaceerp/nsd_bguarantee

# Install on your site
bench --site <your-site-name> install-app nsd_bguarantee

# Run migrations to sync fixtures and schema
bench --site <your-site-name> migrate
```

---

## License

MIT License — Copyright (c) 2026 Nest Software Development.
See [license.txt](license.txt) for details.
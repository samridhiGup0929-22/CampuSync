# Data import readiness
No student CSV/XLSX dataset was present among the supplied attachments. The attached PDF includes the campus blueprint on page 1 and room/branch descriptions on pages 1–2. Do not treat seeded student records or capacities as official.

Recommended import columns: roll_number, name, branch, academic_year, section, batch, date_of_birth. Validate duplicates and required fields before committing. Store date of birth with appropriate access controls and never return it in lookup results.

## Blueprint reconciliation
The PDF page 1 diagram visibly includes additional room labels beyond the prose inventory. These are seeded as VERIFY-only entries with zero capacity. Confirm the official room list, floors, capacities, facilities and permitted uses with campus administration before enabling them.

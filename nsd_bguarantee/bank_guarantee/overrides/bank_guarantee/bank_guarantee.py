# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

"""
Backwards-compatibility module forwarding to nsd_bguarantee.events.bank_guarantee.
"""

from nsd_bguarantee.events.bank_guarantee import (
	bg_issue,
	bg_return,
	get_company,
	on_submit,
	on_update_after_submit,
)

# Legacy alias mappings
on_submit_1 = on_submit
on_update_after_submit_1 = on_update_after_submit

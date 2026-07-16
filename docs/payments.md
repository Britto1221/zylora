# Payments

Razorpay is implemented behind server-side endpoints. The API creates orders,
calculates credit value on the server, verifies checkout signatures, verifies
webhook signatures, deduplicates events, records payment metadata, and credits
the tenant only after trusted confirmation.

Manual payments and manual credit adjustments remain available to the super
admin. Domain renewal payments are separate from WhatsApp credits.

A browser success screen is never sufficient to add credits.

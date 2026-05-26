---
name: Clothing Scraper Logging Reminder
description: User wants a logging feature for the clothing scraper that detects anomalies and surfaces them on the dashboard
type: project
---

Add a logging feature to the clothing scraper that tracks:
1. If the same product keeps showing up across polls → flag as anomaly on dashboard
2. If a brand has no new items for an entire day → flag as anomaly on dashboard

Both anomalies should be displayed in real-time on the Rich live dashboard alongside brand stats.

**Why:** User explicitly asked to be reminded about this during the integration design conversation.
**How to apply:** When implementing the clothing scraper dashboard or storage layer, add this logging/anomaly detection as a required feature, not an afterthought.

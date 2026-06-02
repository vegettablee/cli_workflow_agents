TARGET Company: __
TARGET Website: __

ROLE: Company hiring intelligence extractor.

TASK: Research the given company. Return a single raw JSON array matching the schema below. No markdown. No explanation. No commentary. Output must be directly parseable by JSON.parse().

---

DECISION GATE:
IF company website, approximate size, and at least one of [careers page, LinkedIn, named employee] cannot be confirmed:
  → Fill company fields only. Return emails: [], recruiters: [], jobs: [].
ELSE:
  → Proceed to all phases.

---

PHASE 1 — COMPANY
Extract: legal name, website, size, industry category, city, state, one-sentence description.

PHASE 2 — EMAILS (non-recruiter, in priority order)
1. careers@ / hiring@
2. hr@ / people@ / talent@
3. Named founder or CEO email (small companies only)
4. hello@ / info@

INTEGRITY CONSTRAINT: Only return emails directly observed on a public page. Do not infer, construct, or pattern-match unless the naming convention was explicitly confirmed on that domain. If uncertain → omit.

PHASE 3 — RECRUITERS (in priority order)
1. recruiter@ / recruiting@ / recruitment@ / staffing@
2. Named individuals with titles: "Recruiter", "Talent Acquisition", "TA Partner", "Sourcer" → find their email
3. ta@ / talentacquisition@ / sourcingteam@
4. IF recruiter email domain ≠ company domain → treat as third-party, deprioritize
5. IF no email found → return LinkedIn profile URL. Set linkedin field, leave recruiter_emails: [{}]

CONSTRAINT: Every recruiter entry MUST have email OR linkedin. If neither exists → omit the recruiter entirely.

PHASE 4 — JOBS
Include ONLY currently open roles matching: Software Engineer, SWE, Backend / Frontend / Fullstack Engineer, ML / AI Engineer, DevOps / SRE, Mobile Engineer, Data Engineer, Platform / Infrastructure Engineer.
Exclude: Data Analyst, IT Support, manual QA, Product Manager (unless "Technical PM").
IF no qualifying roles → return jobs: [{}]

---

OUTPUT RULES:
- Raw JSON array only
- No markdown fences, no json prefix, no trailing commas, no comments
- All fields present in every object, no exceptions
- Unknown strings → ""
- Unknown linkedin → "Unknown"
- Missing dates/IDs → null
- Empty arrays → [{}]

---

SCHEMA:
[
  {
    "company": {
      "cname": "",
      "company_website": "",
      "company_size": "",
      "category": "",
      "company_city": "",
      "company_state": "",
      "company_description": "",
      "contact_status": "N/A"
    },
    "emails": [
      {
        "email": "",
        "num_sent": 0,
        "num_replied": 0,
        "template_id": null,
        "last_date_sent": null,
        "contact_status": "N/A"
      }
    ],
    "recruiters": [
      {
        "fname": "",
        "lname": "",
        "linkedin": "Unknown",
        "recruiter_emails": [
          {
            "email": ""
          }
        ]
      }
    ],
    "jobs": [
      {
        "role_name": "",
        "source_url": "",
        "is_open": true
      }
    ]
  }
]

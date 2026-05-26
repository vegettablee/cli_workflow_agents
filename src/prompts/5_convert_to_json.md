ROLE: Data transformation agent - convert semi-structured company research into valid JSON.

TASK: Take the semi-structured company research below and convert it into a raw JSON array matching the exact schema from find_emails.md. No markdown. No explanation. No commentary. Output must be directly parseable by JSON.parse().

---

INPUT: Paste the semi-structured company research from Gemini Deep Research here (1-10 companies in === COMPANY === format)

---

CONVERSION RULES:

1. **All fields must be present** - no exceptions, even if empty
2. **Unknown/missing data handling:**
   - Unknown strings → ""
   - Unknown linkedin → "Unknown"
   - Missing dates/IDs → null
   - Empty arrays → [{}]
3. **Email validation:**
   - Only include emails explicitly mentioned in the research
   - Do NOT construct or infer email patterns
   - If no emails found → emails: [{}]
4. **Recruiter validation:**
   - Every recruiter MUST have fname AND lname
   - Every recruiter MUST have email OR linkedin
   - If recruiter has no email → recruiter_emails: [{}]
   - If recruiter has no email AND no linkedin → omit the recruiter entirely
5. **Jobs validation:**
   - Only include currently open roles
   - If no open roles → jobs: [{}]
6. **Contact status:**
   - Always set to "N/A" for new entries
7. **No trailing commas** in JSON objects or arrays

---

OUTPUT RULES:
- Raw JSON array only
- No markdown fences, no ```json prefix, no trailing commas, no comments
- All fields present in every object
- Directly parseable by JSON.parse()

---

SCHEMA (EXACT STRUCTURE REQUIRED):
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

---

EXAMPLE INPUT:

```
=== COMPANY: Stripe ===
Website: https://stripe.com
Size: Large
Category: Fintech
Location: San Francisco, CA
Description: Builds payment processing infrastructure for internet businesses.

EMAILS:
- jobs@stripe.com (type: careers)

RECRUITERS:
- Sarah Chen | Technical Recruiter | https://linkedin.com/in/sarahchen
- Michael Torres | Engineering Recruiting Lead | recruiting@stripe.com

OPEN ROLES:
- Backend Engineer | https://stripe.com/jobs/backend-eng-123
- Fullstack Engineer | https://stripe.com/jobs/fullstack-eng-456

TECH STACK:
Ruby, Go, JavaScript, React, distributed systems

---

=== COMPANY: Lattice ===
Website: https://lattice.com
Size: Mid-size
Category: HR Tech
Location: San Francisco, CA
Description: Performance management platform for growing companies.

EMAILS:
- careers@lattice.com (type: careers)

RECRUITERS:
- No recruiters identified

OPEN ROLES:
- Software Engineer, Backend | https://lattice.com/careers/backend-swe

TECH STACK:
Python, React, PostgreSQL

---
```

EXAMPLE OUTPUT (copy this structure exactly):

[
  {
    "company": {
      "cname": "Stripe",
      "company_website": "https://stripe.com",
      "company_size": "Large",
      "category": "Fintech",
      "company_city": "San Francisco",
      "company_state": "CA",
      "company_description": "Builds payment processing infrastructure for internet businesses.",
      "contact_status": "N/A"
    },
    "emails": [
      {
        "email": "jobs@stripe.com",
        "num_sent": 0,
        "num_replied": 0,
        "template_id": null,
        "last_date_sent": null,
        "contact_status": "N/A"
      }
    ],
    "recruiters": [
      {
        "fname": "Sarah",
        "lname": "Chen",
        "linkedin": "https://linkedin.com/in/sarahchen",
        "recruiter_emails": [{}]
      },
      {
        "fname": "Michael",
        "lname": "Torres",
        "linkedin": "Unknown",
        "recruiter_emails": [
          {
            "email": "recruiting@stripe.com"
          }
        ]
      }
    ],
    "jobs": [
      {
        "role_name": "Backend Engineer",
        "source_url": "https://stripe.com/jobs/backend-eng-123",
        "is_open": true
      },
      {
        "role_name": "Fullstack Engineer",
        "source_url": "https://stripe.com/jobs/fullstack-eng-456",
        "is_open": true
      }
    ]
  },
  {
    "company": {
      "cname": "Lattice",
      "company_website": "https://lattice.com",
      "company_size": "Mid-size",
      "category": "HR Tech",
      "company_city": "San Francisco",
      "company_state": "CA",
      "company_description": "Performance management platform for growing companies.",
      "contact_status": "N/A"
    },
    "emails": [
      {
        "email": "careers@lattice.com",
        "num_sent": 0,
        "num_replied": 0,
        "template_id": null,
        "last_date_sent": null,
        "contact_status": "N/A"
      }
    ],
    "recruiters": [{}],
    "jobs": [
      {
        "role_name": "Software Engineer, Backend",
        "source_url": "https://lattice.com/careers/backend-swe",
        "is_open": true
      }
    ]
  }
]

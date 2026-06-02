TARGET COMPANIES (5-10):
1. 
2. 
...

---

ROLE: Company intelligence researcher for cold email preparation.

TASK: Research each company and provide semi-structured summaries that can be parsed into JSON. Focus on information useful for personalizing cold emails to internship recruiters.

---

RESEARCH OBJECTIVES FOR EACH COMPANY:

1. **Company Overview**
   - Legal name
   - Approximate company size (Startup/Small/Mid-size/Large)
   - Industry category (Fintech, SaaS, AI/ML, etc.)
   - Location: city, state
   - One-sentence description of what they build

2. **Contact Information** (in priority order)
   - HR/recruiting emails (careers@, hiring@, hr@, talent@)
   - General contact emails (hello@, info@)
   - Named recruiters (first name, last name, title)
   - Recruiter emails or LinkedIn profile URLs
   - If no recruiter found → note "No recruiter identified"

3. **Open Engineering Roles** (if available)
   - Role titles matching: SWE, Backend, Frontend, Fullstack, ML/AI, Data Engineer, DevOps, Mobile
   - Job posting URLs
   - If no open roles → note "No open engineering roles"

4. **Tech Stack / Engineering Focus** (optional, if easily found)
   - Programming languages, frameworks, or technologies mentioned
   - Engineering blog or GitHub presence

---

OUTPUT FORMAT (per company):

Use this template structure for EACH company:

```
=== COMPANY: [Company Name] ===
Website: [URL]
Size: [Startup|Small|Mid-size|Large]
Category: [Industry]
Location: [City, State]
Description: [One sentence about what they build]

EMAILS:
- [email@company.com] (type: careers/hr/general)
- [email@company.com] (type: careers/hr/general)
- [If none found: "No emails identified"]

RECRUITERS:
- [First Last] | [Title] | [email@company.com OR LinkedIn URL]
- [First Last] | [Title] | [email@company.com OR LinkedIn URL]
- [If none found: "No recruiters identified"]

OPEN ROLES:
- [Role Title] | [Job posting URL]
- [Role Title] | [Job posting URL]
- [If none found: "No open engineering roles"]

TECH STACK:
[Brief mention of technologies/languages if found, otherwise "Unknown"]

---
```

---

REQUIREMENTS:
- Only include information you can directly verify from company websites, LinkedIn, or job boards
- If a field cannot be determined, explicitly mark it as "Unknown" or "Not found"
- Prioritize quality over completeness - don't guess or infer email patterns
- Keep descriptions concise and factual
- Separate each company with "===" dividers for easy parsing

---

EXAMPLE OUTPUT:

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
Description: Performance management and employee engagement platform for growing companies.

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

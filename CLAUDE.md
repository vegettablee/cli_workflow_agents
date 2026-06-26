# Your role as an agent 
- You are to act as a collaborator who asks clarifying and thought-provoking questions, and does not build with assumptions apart from low-level implementation details that are non-trivial. IF at any point, you are confused on how to implement, stop and ask me directly. 

# Reference Materials 
- Before generating, modifying, or validating any system prompt / agent prompt / LLM-facing instruction, read `prompt_engineering/CLAUDE.md` and apply the best practices documented there. This applies to new agents, heal/classify prompts, tool descriptions consumed by LLMs, and any prompt revisions.

# System Overview for Personalized Cold-Email Internship Automation Tool 

Personalized Automation Email Generation Workflow: 
1. Pings the SQLite database for any emails that have not been sent yet. 
2. Put all emails into a queue and pull up company information tied with the emails. 
3. For each email in the queue, use company and personal info to draft a personalized email. 
4. Find most relevant resume and attach to the email.
5. Email gets sent to the recruiter/company.

Tech Stack: 
- SQLite
- Python

# Backend Architecture 

Main components
- tools
- - db query functions
- - google email tools  
- data pipeline 
- - transforms data.json into usable, cleaned data 
- rate limiting
- - config.json controls these parameters

Emails can be tied to the company directly or tied directly to a recruiter, who is then tied to the company. There are some important scenarios that should be considered to prevent collisions/invalid insertions, these include: 
- A company MUST exist before an email or recruiter is added to the DB 
- If a recruiter has an email, then the recruiter MUST be added to the database before inserting into the recruiter_emails table 
- If an email is found associated with an HR dept, then insert directly into the emails table 
- If a recruiter is found, but no email can be located, do not insert recruiter into the DB

Important checks before DB operations: 
- Check if an email exists within the emails table AND the recruiter_emails table before any kind of insertion/modification  
- Check status of both the email AND the recruiter, as they can be different depending on the company 

3 main layers of Separation: 
Gmail API Layer: handles direct network calls to Google API
Service Layer: invokes higher functionality(check, create, send) and acts as a separation layer between the agent and the Gmail API 
Orchestration Layer: Acts as an entry point to workflow requests and manages all of the separate workflows/agents(this will without a doubt be the most complex, so the priority is to have some foundation laid out first, like classes and placeholder functions, because designing the rate limiting and the other features are a lot more difficult until there is some foundation) 

Boundaries:
  ├─ Gmail API Layer: only knows Google API structure 
  ├─ Service Layer: only knows the Gmail API request functions  
  ├─ Orchestration Layer: only knows which workflows can be used and when to use them, within this layer includes /agent and /workflows which directly interact with the service layer when needed to complete higher functionality 

Data that crosses boudaries: 
- Orchestration -> Service: Workflow coordinates agents for the task completion, and the agent passes the name of the tool/function to be used(check email, create email, send email) to the service layer
- Service -> Gmail API: Service invokes the calls needed from the API to make the request. 
- Gmail API -> API: Gmail API layer invokes HTTP request to Google API.  

Gmail API will have its own separate layer and this will allow an agent to be able to call this layer and do certain controlled database operations. The tools available will be limited due to security concerns and will encompass these three core functionalities: 
- Check for an email 
- Create an email(draft)
- Send an email 

Application flow per command:  
1. commands.py takes the user input and parses it and routes it to the correct command handler.
2. this command handler calls a method in the orchestrator class which has all of the separate workflows that can be used, and within these workflows, contains the calling of agents to complete a higher-level task(like for a drafting a cold email workflow)

Overview: This goes over the high-level documentation for how the Gmail API integration integration and Gmail workflow management for sending cold personalized emails to companies. 

Scope: This scope is focused on a hybrid approach, not full automation, because it will include a phase where I will personally need to review it to see what needs improvement. The main focus for this section is to incorporate(in order): 
- Gmail API integration: what API functionalies/scopes are needed specifically, boundaries between usage, and rate limiting 
- - this is not as simple as it looks, as context engineering is critical for this to work well. 
- Session State: this state manages all of the workflow storage for the current session(draft, review, queued)
- SQL queries/functions that retrieve: 
- - Recruiters marked as safe to contact and the emails that have not been sent 
- - Emails that have not been sent
- - Companies that not been contacted or marked as 'N/A'
- - Check if a given company is able to be contacted 
- - Check if an email is able to be contacted 
- - Company information 
- Agent LLM Integration: separate agents specifically for drafting a personalized email and one for picking a resume given a job description. 

SQL Update Constraints: 
- If updating contact_status on a recruiter to rejected/ghosted, then you must find all of the emails and mark them the same as well. 
- If updating contact_status on a company, then find all of the emails tied to the company and mark as non-contactable(the emails)

Orchestration Layer Architecture and Interaction Patterns: 

Orchestration Layer Implementation: 
- contains multiple classes that instantiate a workflow class, and simply call the relevant workflow classes with key fields that are required, one of these fields include a rate-limiting variable pulled from the config.json file. 

Orchestration layer data flow in more detail: 
1. Commands.py calls the orchestrator class with its relevant workflow(draft, review, queue) 
2. Orchestrator reads the config.json file and pulls the rate-limiting variables 
3. Orchestrator calls workflow function with relevant arguments, including the rate-limiting variables 
4. Workflow handles and return what was successfully completed: 
- Query database for data needed
- Coordinate multiple steps in sequence
- Call agents with prepared context
- Update session state
- Handle workflow-specific errors
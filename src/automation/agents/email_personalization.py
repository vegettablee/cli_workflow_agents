"""
Email personalization agent for generating customized cold emails.

This module handles the generation of personalized cold emails to companies and recruiters
based on context (company info, recruiter info, personal info) and selected resume type.
"""

import os
import json
from typing import Dict, Tuple, Optional

# Resume file paths relative to project root
RESUME_PATHS = {
    "Fullstack": "./src/resumes/fullstack.pdf",
    "Backend": "./src/resumes/backend.pdf",
    "AI Engineer": "./src/resumes/ai_engineer.pdf",
    "Solutions": "./src/resumes/solutions_engineer.pdf",
    "Machine Learning": "./src/resumes/machine_learning.pdf"
}


def run_draft_agent(context: dict, agent: any, resume_type: str, is_recruiter: bool) -> Tuple[bool, Optional[Dict]]:
    """
    Run the email personalization agent to generate a personalized cold email.

    This function orchestrates the email draft generation by:
    1. Resolving the correct resume path based on resume_type
    2. Calling generate_instructions() to create the email content
    3. Returning the structured email data

    Args:
        context: Dictionary containing company/recruiter information (follows SQLAlchemy model structure)
        agent: PydanticAI Agent instance for email personalization
        resume_type: One of: Backend, Fullstack, AI Engineer, Solutions, Machine Learning
        is_recruiter: True if context includes recruiter info, False if company only

    Returns:
        Tuple of (success: bool, email_dict: dict or None)
        - success: True if the agent successfully generated an email
        - email_dict: Dictionary with keys: 'to', 'subject', 'body', 'raw_html' if successful, None otherwise
    """
    try:
        # Get the resume path for the specified resume type
        resume_path = get_resume_path(resume_type)

        if not resume_path:
            print(f"Error: Invalid resume type '{resume_type}'")
            # TODO: Add logging here
            return (False, None)

        # Generate the email using the agent
        success, email_data = generate_instructions(
            context=context,
            agent=agent,
            resume_type=resume_type,
            resume_path=resume_path,
            is_recruiter=is_recruiter
        )

        if success:
            return (True, email_data)
        else:
            return (False, None)

    except Exception as e:
        print(f"Error in run_draft_agent: {str(e)}")
        # TODO: Add logging here
        return (False, None)


def generate_instructions(
    context: dict,
    agent: any,
    resume_type: str,
    resume_path: str,
    is_recruiter: bool
) -> Tuple[bool, Optional[Dict]]:
    """
    Generate the instruction prompt and call the agent to draft a personalized email.

    This function:
    1. Reads personal context from config.json
    2. Reads template information from templates.json based on current_template_id
    3. Builds a comprehensive prompt with company/recruiter context
    4. Calls the agent to generate the email
    5. Returns structured email data ready for Gmail API

    Args:
        context: Dictionary containing company/recruiter information
        agent: PydanticAI Agent instance for email personalization
        resume_type: The type of resume being attached
        resume_path: Path to the resume file
        is_recruiter: True if context includes recruiter info, False if company only

    Returns:
        Tuple of (success: bool, email_dict: dict or None)
        - success: True if the agent successfully generated an email
        - email_dict: Dictionary with keys: 'to', 'subject', 'body', 'raw_html' if successful, None otherwise
    """
    try:
        # Read personal context from config.json
        config_path = "MCPServer/config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        personal_name = config.get('Name', 'Preston Rank')
        personal_school = config.get('school', 'University of Texas at Dallas')
        personal_year = config.get('year', 'Junior')
        personal_major = config.get('major', 'Computer Science')
        personal_grad = config.get('expected_grad', 'Dec 2027')

        # Get email style preferences from config.json
        email_style = config.get('email_style', {})
        tone = email_style.get('tone', 'professional-casual')
        max_words = email_style.get('max_length_words', 150)

        # Read template information from templates.json
        templates_path = "MCPServer/src/automation/agents/templates.json"
        current_template_id = config.get('current_template_id', '')

        template_outline = ""
        if current_template_id:
            try:
                with open(templates_path, 'r') as f:
                    templates = json.load(f)
                    if current_template_id in templates:
                        template_data = templates[current_template_id]
                        template_outline = f"Subject approach: {template_data.get('subject', 'N/A')}\nBody approach: {template_data.get('body', 'N/A')}"
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load template from templates.json: {str(e)}")
                # TODO: Add logging here

        # Extract recipient email
        recipient_email = context.get('email', 'unknown@example.com')

        # Build the instruction prompt
        if is_recruiter:
            prompt = _build_recruiter_email_prompt(
                context=context,
                personal_name=personal_name,
                personal_school=personal_school,
                personal_year=personal_year,
                personal_major=personal_major,
                personal_grad=personal_grad,
                resume_type=resume_type,
                template_outline=template_outline,
                recipient_email=recipient_email,
                tone=tone,
                max_words=max_words
            )
        else:
            prompt = _build_company_email_prompt(
                context=context,
                personal_name=personal_name,
                personal_school=personal_school,
                personal_year=personal_year,
                personal_major=personal_major,
                personal_grad=personal_grad,
                resume_type=resume_type,
                template_outline=template_outline,
                recipient_email=recipient_email,
                tone=tone,
                max_words=max_words
            )

        # Call the agent to generate the email
        result = agent.run_sync(prompt)

        # Extract the email draft from result
        # result.output is an EmailDraft Pydantic model
        email_draft = result.output

        # Convert to dictionary for return, including resume metadata
        email_dict = {
            'to': email_draft.to,
            'subject': email_draft.subject,
            'body': email_draft.body,
            'raw_html': email_draft.raw_html,
            'resume_path': resume_path,
            'resume_type': resume_type
        }

        return (True, email_dict)

    except Exception as e:
        print(f"Error in generate_instructions: {str(e)}")
        # TODO: Add logging here
        return (False, None)


def get_resume_path(resume_type: str) -> Optional[str]:
    """
    Get the file path for the specified resume type.

    Args:
        resume_type: One of: Backend, Fullstack, AI Engineer, Solutions, Machine Learning

    Returns:
        The file path to the resume PDF, or None if resume_type is invalid
    """
    return RESUME_PATHS.get(resume_type)


def _build_company_email_prompt(
    context: dict,
    personal_name: str,
    personal_school: str,
    personal_year: str,
    personal_major: str,
    personal_grad: str,
    resume_type: str,
    template_outline: str,
    recipient_email: str,
    tone: str,
    max_words: int
) -> str:
    """
    Build the instruction prompt for generating a cold email to a company.

    Args:
        context: Company context dictionary
        personal_name: Student's name
        personal_school: Student's school
        personal_year: Student's year (e.g., Junior)
        personal_major: Student's major
        personal_grad: Expected graduation date
        resume_type: Type of resume being sent
        template_outline: Template structure from templates.json
        recipient_email: The company email address
        tone: Email tone from config.json
        max_words: Maximum word count from config.json

    Returns:
        Formatted instruction prompt string for the agent
    """
    company_name = context.get('cname', 'the company')
    company_description = context.get('company_description', 'N/A')
    company_size = context.get('company_size', 'N/A')
    company_category = context.get('category', 'N/A')
    company_location = f"{context.get('company_city', '')}, {context.get('company_state', '')}".strip(', ')
    company_website = context.get('company_website', 'N/A')

    prompt = f"""You are drafting a personalized cold email for an internship opportunity.

# Your Information (Sender)
- Name: {personal_name}
- School: {personal_school}
- Year: {personal_year}
- Major: {personal_major}
- Expected Graduation: {personal_grad}
- Resume Type Being Sent: {resume_type}

# Company Information (Recipient)
- Company Name: {company_name}
- Email: {recipient_email}
- Description: {company_description}
- Size: {company_size}
- Category: {company_category}
- Location: {company_location}
- Website: {company_website}

# Email Guidelines
- Tone: {tone}
- Maximum Length: {max_words} words
- Format: Plain text (keep raw_html field empty for now)

# Template Outline (Follow this structure/approach)
{template_outline if template_outline else "Use a professional, concise approach that highlights relevant experience and expresses genuine interest."}

# Task
Draft a personalized cold email that:
1. Follows the template outline structure
2. Addresses the company directly and shows you've researched them
3. Briefly highlights how your {resume_type} experience aligns with their work
4. Expresses genuine interest in internship opportunities
5. Keeps it concise and respectful of their time
6. Sounds authentic and not overly formal
7. Stays within the {max_words} word limit

# Output Format
Provide your response in the following JSON format:
{{
    "to": "{recipient_email}",
    "subject": "Concise, attention-grabbing subject line (5-8 words)",
    "body": "Full email body in plain text",
    "raw_html": "leave blank"
}}
"""

    return prompt


def _build_recruiter_email_prompt(
    context: dict,
    personal_name: str,
    personal_school: str,
    personal_year: str,
    personal_major: str,
    personal_grad: str,
    resume_type: str,
    template_outline: str,
    recipient_email: str,
    tone: str,
    max_words: int
) -> str:
    """
    Build the instruction prompt for generating a cold email to a recruiter.

    Args:
        context: Combined company + recruiter context dictionary
        personal_name: Student's name
        personal_school: Student's school
        personal_year: Student's year (e.g., Junior)
        personal_major: Student's major
        personal_grad: Expected graduation date
        resume_type: Type of resume being sent
        template_outline: Template structure from templates.json
        recipient_email: The recruiter's email address
        tone: Email tone from config.json
        max_words: Maximum word count from config.json

    Returns:
        Formatted instruction prompt string for the agent
    """
    # Company information
    company_name = context.get('cname', 'the company')
    company_description = context.get('company_description', 'N/A')
    company_size = context.get('company_size', 'N/A')
    company_category = context.get('category', 'N/A')
    company_location = f"{context.get('company_city', '')}, {context.get('company_state', '')}".strip(', ')
    company_website = context.get('company_website', 'N/A')

    # Recruiter information
    recruiter_fname = context.get('fname', '')
    recruiter_lname = context.get('lname', '')
    recruiter_linkedin = context.get('linkedin', 'N/A')

    prompt = f"""You are drafting a personalized cold email to a recruiter for an internship opportunity.

# Your Information (Sender)
- Name: {personal_name}
- School: {personal_school}
- Year: {personal_year}
- Major: {personal_major}
- Expected Graduation: {personal_grad}
- Resume Type Being Sent: {resume_type}

# Recruiter Information
- Name: {recruiter_fname} {recruiter_lname}
- Email: {recipient_email}
- LinkedIn: {recruiter_linkedin}

# Company Information
- Company Name: {company_name}
- Description: {company_description}
- Size: {company_size}
- Category: {company_category}
- Location: {company_location}
- Website: {company_website}

# Email Guidelines
- Tone: {tone}
- Maximum Length: {max_words} words
- Format: Plain text (keep raw_html field empty for now)

# Template Outline (Follow this structure/approach)
{template_outline if template_outline else "Use a professional, concise approach that highlights relevant experience and expresses genuine interest."}

# Task
Draft a personalized cold email that:
1. Follows the template outline structure
2. Addresses the recruiter by name ({recruiter_fname})
3. Shows you've researched both the recruiter and the company
4. Briefly highlights how your {resume_type} experience aligns with the company's work
5. Expresses genuine interest in internship opportunities at {company_name}
6. Keeps it concise and respectful of their time
7. Sounds authentic and not overly formal
8. Stays within the {max_words} word limit

# Output Format
Provide your response in the following JSON format:
{{
    "to": "{recipient_email}",
    "subject": "Concise, attention-grabbing subject line (5-8 words)",
    "body": "Full email body in plain text",
    "raw_html": ""
}}
"""

    return prompt

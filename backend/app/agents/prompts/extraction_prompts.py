"""
Prompts for clause extraction from contracts.
"""

EXTRACT_CLAUSES_PROMPT = """
You are a legal contract extraction specialist. Your task is to CAREFULLY extract ALL relevant clauses and statements from this contract.

IMPORTANT: Extract EVERYTHING relevant, including:
- Explicit clauses (e.g., "Payment Terms:")
- Implied statements (e.g., "No insurance requirements")
- Missing elements (e.g., "No termination clause is provided")
- Scattered information that relates to the same topic

CONTRACT TEXT:
{contract_text}

Extract and categorize ALL content into these sections:
1. SCOPE OF WORK/SERVICES - What work will be done? How is scope defined?
2. PAYMENT TERMS - How much? When? What conditions? Any limitations?
3. INSURANCE & LIABILITY REQUIREMENTS - What insurance is required? What are liability caps?
4. INDEMNIFICATION - Who indemnifies whom? How broad is it?
5. TERMINATION PROVISIONS - How can parties exit? What notice is required?
6. INTELLECTUAL PROPERTY - Who owns deliverables? Who owns pre-existing work?
7. CONFIDENTIALITY & PROTECTIONS - What information must be protected?
8. DISPUTE RESOLUTION - How are conflicts resolved? What law governs?
9. MISSING/ABSENT CLAUSES - What IMPORTANT elements are NOT included?

For each item, provide:
- "section": category name
- "title": specific topic (e.g., "Payment Schedule", "Insurance Requirement", "Missing Termination Clause")
- "text": exact quote from contract OR description if missing
- "status": "present" or "missing"
- "severity": "critical" if missing and should be present, "present" if exists

Return as JSON array. Be exhaustive - extract 15-25 items minimum.
Include negations like "No insurance required" or "No termination clause provided".
"""

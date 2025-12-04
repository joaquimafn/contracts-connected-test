"""
Prompts for risk detection in contracts.
"""

DETECT_RISKS_PROMPT = """
You are an expert contract risk analyst with 20+ years of legal and business experience.
Your job is to identify EVERY material risk in this contract that could harm the business.

CONTRACT CLAUSES & CONTENT:
{extracted_clauses}

ANALYZE FOR THESE 6 RISK CATEGORIES:

1. **MISSING_INSURANCE** - Insurance requirements that SHOULD exist but DON'T
   Examples: No requirement to maintain liability insurance, no workers comp coverage required,
   no professional liability insurance, gaps in coverage that expose company

2. **UNCAPPED_LIABILITY** - Liability exposure WITHOUT reasonable caps or limits
   Examples: "liable for any and all damages", no limit to damages, unlimited indemnification,
   no exclusion for indirect/consequential damages

3. **VAGUE_PAYMENT_TERMS** - Payment criteria that are UNCLEAR or PROBLEMATIC
   Examples: "as deemed acceptable" (who decides?), no specific due dates, "upon satisfactory progress"
   (who defines satisfactory?), undefined pricing, unilateral rate changes

4. **BROAD_INDEMNIFICATION** - Indemnification obligations that are TOO WIDE or ONE-SIDED
   Examples: Indemnifying for ALL claims, defending for third-party acts outside contractor's control,
   no limits on indemnification scope, no exception for other party's negligence

5. **MISSING_TERMINATION** - Termination rights or processes that are ABSENT or UNBALANCED
   Examples: No termination clause at all, no notice period required, unequal notice periods,
   no exit mechanism defined, impossible termination requirements

6. **AMBIGUOUS_SCOPE** - Scope of work that is VAGUE, UNLIMITED, or UNDEFINED
   Examples: "services as requested", "as directed by" other party, no defined deliverables,
   scope can be changed unilaterally, "as needed" work with no limits

FOR EACH RISK DETECTED, PROVIDE:
{
  "category": "EXACT_CATEGORY_NAME",
  "title": "Specific risk title",
  "description": "What the risk is and why it matters",
  "affected_clause": "Reference to contract section with problem",
  "explanation": "Why this is problematic - concrete business consequences",
  "evidence": ["Direct quote 1", "Direct quote 2", "Evidence of missing element"],
  "financial_impact": "LOW|MEDIUM|HIGH - estimated financial exposure",
  "likelihood": "LOW|MEDIUM|HIGH - probability this will cause problems"
}

CRITICAL INSTRUCTIONS:
1. Look for MISSING elements, not just bad wording. "No insurance requirement" is a BIG RISK.
2. Look for one-sided or unbalanced terms. "Can terminate without notice" vs "must give 90 days" = RISK.
3. Look for vague words: "as needed", "as directed", "as deemed", "satisfactory", "adequate"
4. If you see "and all" or "unlimited" or "any and all" - THAT'S UNCAPPED LIABILITY.
5. Be AGGRESSIVE in identifying risks. Contract purpose is to assess risks, not minimize them.
6. Every contract should have: clear scope, payment terms, termination clause, insurance, liability caps.
7. If any of these are MISSING or VAGUE, report it as a risk.

Return a JSON array with ALL identified risks. Aim for 4-8 risks minimum per contract.
"""

SCORING_PROMPT = """
You are evaluating how severe this contract risk is. Provide a detailed severity score from 0-100.

RISK TO SCORE:
Category: {category}
Title: {title}
Description: {description}
Evidence: {evidence}
Financial Impact: {financial_impact}
Likelihood: {likelihood}
Contract Context: {contract_context}

SCORING GUIDANCE:

**Financial Exposure** (0-40 points):
- 0-5: < $5K exposure (rarely problematic)
- 6-15: $5K-$50K exposure (moderate concern)
- 16-25: $50K-$500K exposure (significant concern)
- 26-35: $500K-$5M exposure (very concerning)
- 36-40: $5M+ or unlimited exposure (critical)

**Legal/Compliance Risk** (0-30 points):
- 0-5: Minimal legal exposure
- 6-10: Low legal risk, minor dispute
- 11-15: Moderate legal exposure
- 16-20: High legal exposure, likely litigation
- 21-30: Severe - regulatory violation, major lawsuit

**Operational Impact** (0-20 points):
- 0-3: Minimal operational disruption
- 4-7: Minor delays or issues
- 8-12: Moderate business disruption
- 13-17: Significant operational impact
- 18-20: Severe - business continuity threatened

**Likelihood Multiplier** (0.3 to 1.5x):
- LOW likelihood (25%): 0.3-0.6x (reduce final score)
- MEDIUM likelihood (50%): 0.8-1.0x (normal)
- HIGH likelihood (75%+): 1.2-1.5x (amplify score)

SPECIAL SCORING RULES:
- Missing insurance + MEDIUM/HIGH work = +15 points automatically
- Uncapped liability + ANY financial transaction = +20 points automatically
- Vague payment terms + large contract = +15 points automatically
- Ambiguous scope + client discretion = +15 points automatically
- One-sided termination = +10 points automatically

EXAMPLES:
- "No insurance, $75K contract, construction" = 75-85 (HIGH)
- "Vague payment, 'upon satisfaction', $50K" = 80-85 (HIGH)
- "Unlimited liability for all damages" = 85-95 (CRITICAL)
- "Termination: client=anytime, contractor=90 days" = 70-80 (HIGH)

Return JSON with:
{
  "overall_score": 0-100 integer,
  "breakdown": {
    "financial": 0-40,
    "legal": 0-30,
    "operational": 0-20
  },
  "likelihood_multiplier": 0.3-1.5,
  "final_calculation": "Description of how score was calculated",
  "justification": "Why this score is justified"
}
"""

REMEDIATION_PROMPT = """
You are an expert contract negotiator. Provide specific, actionable remediation for this risk.

RISK DETAILS:
Category: {category}
Title: {title}
Description: {description}
Current Language: {evidence}
Severity Score: {severity_score}

PROVIDE REMEDIATION WITH 3 OPTIONS:

OPTION 1 - IDEAL SOLUTION (Best-case negotiation)
Provide the exact language you'd want in the contract. Be specific and complete.
This is what you ask for first in negotiations.

OPTION 2 - FALLBACK SOLUTION (Compromise position)
If Option 1 is rejected, what's the minimum acceptable fix?
This is your backup position that's still protective.

OPTION 3 - NEGOTIATION TACTICS (How to get there)
- What leverage points can you use?
- What arguments should you make?
- How to justify why this change is fair?
- What alternatives could you offer?

FOR EACH OPTION, PROVIDE ACTUAL LANGUAGE/WORDING WHERE RELEVANT.

SCORING THE REMEDIATION:
- "priority": CRITICAL|HIGH|MEDIUM|LOW (based on risk severity)
- "effort": HIGH|MEDIUM|LOW (to negotiate/implement)
- "likelihood_of_acceptance": HIGH|MEDIUM|LOW (market standard vs aggressive)

EXAMPLES:

Risk: "No payment schedule defined"
Option 1: "Client agrees to pay $50,000 in three installments: (1) $20,000 upon execution,
          (2) $20,000 upon 50% completion, (3) $10,000 upon final delivery.
          Each invoice due within 15 days."
Option 2: "Payment of $50,000 due within 30 days of project completion,
          with milestone-based payments subject to mutual agreement."
Option 3: Argument - "Vague payment terms create cash flow uncertainty. Let's define clear milestones
         so both parties know expectations. Industry standard is milestone-based payment."

Risk: "No insurance requirement"
Option 1: "Contractor shall maintain minimum $1,000,000 general liability insurance
         and provide proof of coverage upon request."
Option 2: "Contractor shall maintain appropriate insurance consistent with the scope of work
         and provide certificate of insurance before commencing work."
Option 3: Argument - "Insurance protects both of us. Minimal cost for contractor,
         major protection for client in case of accident or negligence."

Return JSON with:
{
  "ideal_solution": "Option 1 - exact language",
  "fallback_solution": "Option 2 - compromise language",
  "negotiation_tactics": {
    "leverage": ["point 1", "point 2"],
    "arguments": ["arg 1", "arg 2"],
    "alternatives": ["alternative 1", "alternative 2"]
  },
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",
  "effort": "HIGH|MEDIUM|LOW",
  "likelihood_of_acceptance": "HIGH|MEDIUM|LOW"
}
"""

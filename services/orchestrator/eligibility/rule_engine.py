import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class EligibilityResult:
    scheme_id: str
    scheme_name: str
    is_potentially_eligible: bool
    match_score: float  # 0.0 to 1.0
    matched_criteria: List[str]
    unmatched_criteria: List[str]
    unknown_criteria: List[str]
    explanation: str

def parse_age_range(eligibility_text: str) -> Optional[tuple]:
    """
    Extracts age range from eligibility text using regex patterns.
    Examples: '18-60 years', 'between 18 and 35', 'above 60', 'minimum 18'
    """
    if not eligibility_text or not isinstance(eligibility_text, str):
        return None
        
    text = eligibility_text.lower()
    
    # Pattern for range: 18-60 or 18 to 60 or 18 - 60
    range_match = re.search(r'(\d+)\s*(?:-|to|and)\s*(\d+)\s*years?', text)
    if range_match:
        return int(range_match.group(1)), int(range_match.group(2))
        
    # Pattern for minimum age: "above 18", "minimum 18", "18 years and above", "age of 18"
    min_match = re.search(r'(?:above|minimum|at least|from|age of)\s*(\d+)', text)
    if min_match:
        return int(min_match.group(1)), 150
        
    min_match_alt = re.search(r'(\d+)\s*years?(?:\s*and)?\s*above', text)
    if min_match_alt:
        return int(min_match_alt.group(1)), 150
        
    # Pattern for maximum age: "under 60", "below 60", "up to 60", "maximum 60"
    max_match = re.search(r'(?:under|below|up to|maximum|below the age of)\s*(\d+)', text)
    if max_match:
        return 0, int(max_match.group(1))
        
    return None

def parse_income_limit(eligibility_text: str) -> Optional[float]:
    """
    Extracts maximum income limit from text.
    Examples: 'income should not exceed ₹ 2,00,000', 'less than 1.5 Lakh', 'below 75,000'
    """
    if not eligibility_text or not isinstance(eligibility_text, str):
        return None
        
    text = eligibility_text.lower().replace(',', '')
    
    # Look for Lakh patterns: '2.5 lakh', '1.5lakh', '2 lakh'
    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|L)', text)
    if lakh_match:
        return float(lakh_match.group(1)) * 100000.0
        
    # Look for pure numbers associated with limit keywords
    limit_match = re.search(r'(?:exceed|below|less than|maximum|limit of|up to|₹|rs\.?)\s*(\d{5,6})', text)
    if limit_match:
        return float(limit_match.group(1))
        
    return None

def evaluate_eligibility(user_profile: Dict[str, Any], scheme_dict: Dict[str, Any]) -> EligibilityResult:
    """
    Evaluates user profile against scheme eligibility criteria.
    Uses rules extracted from the scheme eligibility free-text or metadata.
    """
    scheme_id = str(scheme_dict.get("id", ""))
    scheme_name = scheme_dict.get("scheme_name", "Unknown Scheme")
    eligibility_text = scheme_dict.get("eligibility", "")
    
    matched = []
    unmatched = []
    unknown = []
    
    # 1. Evaluate Age
    user_age = user_profile.get("age")
    age_rule = parse_age_range(eligibility_text)
    if user_age is not None and age_rule is not None:
        min_age, max_age = age_rule
        if min_age <= user_age <= max_age:
            matched.append(f"Age {user_age} falls in range {min_age}-{max_age}")
        else:
            unmatched.append(f"Age {user_age} does not fall in range {min_age}-{max_age}")
    elif user_age is not None:
        unknown.append("Age rule not explicitly extracted, but age provided")
    else:
        unknown.append("Age not provided in user profile")

    # 2. Evaluate Income
    user_income_str = user_profile.get("income_bracket")
    income_rule = parse_income_limit(eligibility_text)
    
    # Helper to convert income string to numerical value
    # e.g., '150000' or 'less than 2.5L' etc.
    def get_numeric_income(inc_str):
        if not inc_str:
            return None
        nums = re.findall(r'\d+', str(inc_str).replace(',', ''))
        if nums:
            val = float(nums[0])
            if 'lakh' in str(inc_str).lower() or 'l' in str(inc_str).lower():
                val = val * 100000
            return val
        return None

    user_income = get_numeric_income(user_income_str)
    if user_income is not None and income_rule is not None:
        if user_income <= income_rule:
            matched.append(f"Income ₹{user_income:,.2f} is below limit ₹{income_rule:,.2f}")
        else:
            unmatched.append(f"Income ₹{user_income:,.2f} exceeds limit ₹{income_rule:,.2f}")
    elif user_income is not None:
        unknown.append("Income limit rule not explicitly extracted from description")
    else:
        unknown.append("Income details not provided in profile")

    # 3. Category / Caste Evaluation
    user_category = user_profile.get("category")
    if user_category and isinstance(user_category, str):
        cat_lower = user_category.lower()
        # Look for mentions of SC, ST, OBC, General in eligibility text
        sc_mentioned = 'sc' in eligibility_text.lower() or 'scheduled caste' in eligibility_text.lower()
        st_mentioned = 'st' in eligibility_text.lower() or 'scheduled tribe' in eligibility_text.lower()
        obc_mentioned = 'obc' in eligibility_text.lower() or 'backward' in eligibility_text.lower()
        
        if (sc_mentioned and 'sc' in cat_lower) or (st_mentioned and 'st' in cat_lower) or (obc_mentioned and 'obc' in cat_lower):
            matched.append(f"Category matched: {user_category}")
        elif sc_mentioned or st_mentioned or obc_mentioned:
            # Scheme is restricted to some categories, check if user matches none
            unmatched.append(f"Scheme targets specific categories, user is {user_category}")
        else:
            unknown.append("No specific caste/category restriction detected")
            
    # 4. State / Location Evaluation
    user_state = user_profile.get("location_state")
    if user_state and isinstance(user_state, str):
        # If the scheme has level = 'State' but the name of the state is not in the text, we might flag
        # If the state name (e.g. 'Puducherry', 'Madhya Pradesh', 'Karnataka') is mentioned in the text
        # Let's check
        state_match = re.search(r'\b(Madhya Pradesh|Karnataka|Puducherry|West Bengal|Rajasthan|Chhattisgarh|Andhra Pradesh)\b', eligibility_text, re.IGNORECASE)
        if state_match:
            state_found = state_match.group(1).lower()
            if state_found in user_state.lower():
                matched.append(f"Location state matched: {user_state}")
            else:
                unmatched.append(f"Scheme is for state {state_match.group(1)}, user state is {user_state}")
        else:
            # Check level of scheme
            level = scheme_dict.get("level", "Central")
            if level == "Central":
                matched.append("Central scheme, open to all states")
            else:
                unknown.append("State scheme, but targeted state not detected in criteria text")

    # Calculate match score
    total_checks = len(matched) + len(unmatched)
    if total_checks > 0:
        match_score = len(matched) / total_checks
    else:
        match_score = 0.5  # Neutral default when no filters matched

    is_potentially_eligible = len(unmatched) == 0

    # Build plain language explanation
    matched_str = "; ".join(matched) if matched else "None"
    unmatched_str = "; ".join(unmatched) if unmatched else "None"
    explanation = f"Potential match checks. Passed: [{matched_str}]. Failed: [{unmatched_str}]."

    return EligibilityResult(
        scheme_id=scheme_id,
        scheme_name=scheme_name,
        is_potentially_eligible=is_potentially_eligible,
        match_score=match_score,
        matched_criteria=matched,
        unmatched_criteria=unmatched,
        unknown_criteria=unknown,
        explanation=explanation
    )

def rank_schemes_for_user(user_profile: Dict[str, Any], schemes: List[Dict[str, Any]]) -> List[EligibilityResult]:
    """
    Evaluates eligibility for a list of schemes and ranks them.
    """
    results = []
    for scheme in schemes:
        result = evaluate_eligibility(user_profile, scheme)
        results.append(result)
        
    # Sort by match_score descending, then by potential eligibility
    results.sort(key=lambda x: (x.is_potentially_eligible, x.match_score), reverse=True)
    return results

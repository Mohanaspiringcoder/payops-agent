import re


def validate_investigation_response(
    response: str,
    evidence: dict,
) -> dict:
    """
    Validate an investigation response against verified evidence.

    Returns a structured validation result rather than modifying
    the LLM response.
    """

    errors = []

    # ---------------------------------------------------------
    # 1. Required sections
    # ---------------------------------------------------------

    required_sections = [
        "OBSERVED EVIDENCE:",
        "INTERPRETATION:",
        "LIMITATIONS:",
        "NEXT INVESTIGATION:",
    ]

    for section in required_sections:
        if section not in response:
            errors.append(f"Missing required section: {section}")

    # ---------------------------------------------------------
    # 2. Numeric validation
    # ---------------------------------------------------------

    allowed_numbers = set()

    for value in evidence.values():
        if isinstance(value, (int, float)):
            allowed_numbers.add(value)

    failure_reasons = evidence.get("failure_reasons", {})

    for count in failure_reasons.values():
        if isinstance(count, (int, float)):
            allowed_numbers.add(count)

    numbers = [
        float(value)
        for value in re.findall(r"\b\d+(?:\.\d+)?\b", response)
    ]

    unsupported_numbers = [
        number
        for number in numbers
        if number not in allowed_numbers
    ]

    if unsupported_numbers:
        errors.append(
            "Response contains numeric values that are not present "
            "in the verified evidence."
        )

    response_lower = response.lower()

    # ---------------------------------------------------------
    # 3. Unsupported numerical relationships
    # ---------------------------------------------------------

    comparison_patterns = [
        r"\btimes more\b",
        r"\btimes less\b",
        r"\btimes higher\b",
        r"\btimes lower\b",
        r"\bmore frequent than\b",
        r"\bless frequent than\b",
        r"\bhigher than\b",
        r"\blower than\b",
        r"\bgreater than\b",
        r"\bless than\b",
        r"\bdoubled\b",
        r"\btripled\b",
        r"\bhalf of\b",
        r"\btwice\b",
        r"\bthree times\b",
    ]

    unsupported_comparison = any(
        re.search(pattern, response_lower)
        for pattern in comparison_patterns
    )

    if unsupported_comparison:
        errors.append(
            "Response contains numeric values in a comparison or "
            "relationship that has not been explicitly verified "
            "by the evidence."
        )

    # ---------------------------------------------------------
    # 4. Split response into sections
    # ---------------------------------------------------------

    sections = {}
    current_section = None

    for line in response.splitlines():
        stripped = line.strip()

        if stripped in required_sections:
            current_section = stripped
            sections[current_section] = []
            continue

        if current_section:
            sections[current_section].append(line)

    # ---------------------------------------------------------
    # 5. Unsupported causal claims
    # ---------------------------------------------------------

    causal_patterns = [
    r"\bcaused by\b",
    r"\bdue to\b",
    r"\bbecause of\b",
    r"\bresulted from\b",
    r"\battributable to\b",
    r"\bdriven by\b",
    r"\bcaused\b",
    r"\bsuggests that\b.*\b(?:cause|caused|causing|primary cause)\b",
    r"\bindicates that\b.*\b(?:cause|caused|causing|primary cause)\b",
    r"\bappears to be caused by\b",
    r"\blikely caused by\b",
	]

    limitation_phrases = [
        "cannot establish",
        "does not establish",
        "cannot determine",
        "does not determine",
        "not enough evidence",
        "insufficient evidence",
        "not established",
        "not proven",
    ]

    sections_to_check = [
        "INTERPRETATION:",
        "NEXT INVESTIGATION:",
    ]

    for section_name in sections_to_check:
        section_text = "\n".join(
            sections.get(section_name, [])
        ).lower()

        if not section_text:
            continue

        has_causal_language = any(
            re.search(pattern, section_text)
            for pattern in causal_patterns
        )

        has_limitation_language = any(
            phrase in section_text
            for phrase in limitation_phrases
        )

        if has_causal_language and not has_limitation_language:
            errors.append(
                f"Unsupported causal claim detected in {section_name} "
                "The response attributes an outcome to a cause that "
                "is not established by the verified evidence."
            )

    # ---------------------------------------------------------
    # 6. Unsupported relationship / attribution claims
    # ---------------------------------------------------------
    #
    # These are not always explicit causal statements.
    # Examples:
    #
    #   "SBI is responsible for most TIMEOUT failures."
    #   "TIMEOUT failures are correlated with high amounts."
    #   "The failures are related to infrastructure capacity."
    #
    # These statements still assert a relationship that must be
    # supported by verified evidence.
    #
    # We check these patterns only in INTERPRETATION because
    # NEXT INVESTIGATION is allowed to propose relationships
    # that should be investigated.
    # ---------------------------------------------------------

    interpretation_text = "\n".join(
        sections.get("INTERPRETATION:", [])
    ).lower()

    unsupported_relationship_patterns = [
        r"\bis responsible for\b",
        r"\bwas responsible for\b",
        r"\bare responsible for\b",
        r"\bwere responsible for\b",
        r"\bis correlated with\b",
        r"\bare correlated with\b",
        r"\bwas correlated with\b",
        r"\bwere correlated with\b",
        r"\bis related to\b",
        r"\bare related to\b",
        r"\bwas related to\b",
        r"\bwere related to\b",
        r"\bis linked to\b",
        r"\bare linked to\b",
        r"\bwas linked to\b",
        r"\bwere linked to\b",
        r"\bis associated with\b",
        r"\bare associated with\b",
        r"\bwas associated with\b",
        r"\bwere associated with\b",
        r"\bis connected to\b",
        r"\bare connected to\b",
        r"\bhas a relationship with\b",
        r"\bhave a relationship with\b",
    ]

    unsupported_relationship = any(
        re.search(pattern, interpretation_text)
        for pattern in unsupported_relationship_patterns
    )

    if unsupported_relationship:
        errors.append(
            "Response contains an unsupported relationship or "
            "attribution claim in INTERPRETATION that is not "
            "established by the verified evidence."
        )

    # ---------------------------------------------------------
    # 7. Unsupported operational / infrastructure assertions
    # ---------------------------------------------------------
    #
    # These patterns catch claims such as:
    #
    #   "The infrastructure is experiencing a capacity problem."
    #   "The server is overloaded."
    #   "The system has a capacity issue."
    #
    # We only check INTERPRETATION so that investigation
    # recommendations such as "Review server metrics" remain valid.
    # ---------------------------------------------------------

    infrastructure_patterns = [
        r"\binfrastructure is experiencing\b",
        r"\binfrastructure is suffering\b",
        r"\binfrastructure has\b",
        r"\binfrastructure has a\b",
        r"\bserver is overloaded\b",
        r"\bservers are overloaded\b",
        r"\bserver overload\b",
        r"\bsystem is overloaded\b",
        r"\bsystem overload\b",
        r"\bcapacity problem\b",
        r"\bcapacity issue\b",
        r"\bcapacity constraint\b",
        r"\bperformance problem\b",
        r"\bperformance issue\b",
        r"\bnetwork outage\b",
        r"\bnetwork failure\b",
    ]

    unsupported_infrastructure = any(
        re.search(pattern, interpretation_text)
        for pattern in infrastructure_patterns
    )

    if unsupported_infrastructure:
        errors.append(
            "Response contains an unsupported infrastructure, "
            "network, or system assertion in INTERPRETATION that "
            "is not established by the verified evidence."
        )

    # ---------------------------------------------------------
    # 8. Final validation result
    # ---------------------------------------------------------

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }

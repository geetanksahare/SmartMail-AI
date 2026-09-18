def build_newsletter_system_prompt() -> str:
    return """
You are SmartMail AI, an expert email marketing assistant.

Your job is to create high-quality newsletter drafts.

Rules:

1. Never invent facts, statistics, prices, dates,
   customer results, product claims, or announcements.
2. Use only information supplied by the user.
3. Match the requested audience and tone.
4. Write clear, useful, engaging email content.
5. Keep the content appropriate for a newsletter.
6. Do not include markdown code fences.
7. Do not include explanations outside the requested fields.
8. Create a useful call-to-action.
9. Do not invent a URL.
10. Return only the requested structured output.
""".strip()


def build_newsletter_user_prompt(
    *,
    topic: str,
    audience: str,
    tone: str,
    length: str,
    key_points: list[str],
) -> str:

    if key_points:
        formatted_key_points = "\n".join(
            f"- {point}"
            for point in key_points
        )
    else:
        formatted_key_points = "- No additional key points provided."

    return f"""
Create a newsletter using the following information.

Topic:
{topic}

Target audience:
{audience}

Tone:
{tone}

Desired length:
{length}

Key points:
{formatted_key_points}

Return:

1. Subject
2. Preview text
3. Newsletter body
4. Call-to-action text

Requirements:

- Make the subject clear and compelling.
- Keep preview text concise.
- Make the body appropriate for the requested audience.
- Make the CTA actionable but do not create a URL.
- Do not invent facts or unsupported claims.
""".strip()

def build_campaign_analysis_system_prompt() -> str:
    return """
You are SmartMail AI, an expert email marketing analyst.

Analyze campaign performance using only the supplied
campaign and analytics data.

Rules:

1. Never invent metrics or facts.
2. Do not infer information that cannot be supported
   by the supplied data.
3. Distinguish clearly between observations and recommendations.
4. Recommendations must be practical and relevant to email marketing.
5. Do not blame or negatively characterize individual subscribers.
6. Do not recommend changing metrics artificially.
7. Return only the requested structured output.
""".strip()


def build_campaign_analysis_user_prompt(
    *,
    title: str,
    subject: str,
    audience: str | None,
    total_recipients: int,
    sent: int,
    delivered: int,
    opened: int,
    clicked: int,
    bounced: int,
    complained: int,
    unsubscribed: int,
    failed: int,
    delivery_rate: float,
    open_rate: float,
    click_rate: float,
    bounce_rate: float,
    complaint_rate: float,
    unsubscribe_rate: float,
) -> str:

    return f"""
Analyze the following email campaign.

Campaign title:
{title}

Subject:
{subject}

Audience:
{audience or "Not specified"}

Performance:

Total recipients: {total_recipients}
Sent: {sent}
Delivered: {delivered}
Opened: {opened}
Clicked: {clicked}
Bounced: {bounced}
Complained: {complained}
Unsubscribed: {unsubscribed}
Failed: {failed}

Delivery rate: {delivery_rate}%
Open rate: {open_rate}%
Click rate: {click_rate}%
Bounce rate: {bounce_rate}%
Complaint rate: {complaint_rate}%
Unsubscribe rate: {unsubscribe_rate}%

Return:

1. A concise overall summary.
2. The strongest aspects of the campaign.
3. The main issues visible from the metrics.
4. Practical recommendations for improving future campaigns.

Do not invent any information not present above.
""".strip()
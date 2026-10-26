import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


class AICounselorService:
    """
    AI Education Counselor Service for EduVerse AI.
    Integrates with Google Gemini API when GEMINI_API_KEY is configured,
    and provides a robust, personalized rule-based counseling engine as a fallback.
    """

    SYSTEM_INSTRUCTION = (
        "You are EduVerse AI Counselor, an expert higher-education and career guidance counselor "
        "designed specifically for students after 12th standard in Tamil Nadu. "
        "Your role is to help students choose suitable undergraduate courses, understand TNEA engineering cutoffs, "
        "explore Tamil Nadu college options, and evaluate career pathways. "
        "Always follow these guidelines:\n"
        "1. Be student-friendly, encouraging, clear, and structured.\n"
        "2. Never guarantee admission or promise specific salary/job outcomes.\n"
        "3. Use transparent guidance phrasing such as 'Based on your profile, you may explore...', 'A suitable path to consider...'\n"
        "4. Emphasize both technical skills to build and higher-study possibilities (e.g. MCA, MBA, M.Sc, CA).\n"
        "5. Keep responses concise, well-formatted with bullet points and bold key terms."
    )

    @staticmethod
    def get_counselor_response(user_message: str, student_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for generating counselor answers.
        Attempts Gemini API call; gracefully falls back to rule-based engine on missing key or network issue.
        """
        clean_msg = (user_message or '').strip()
        if not clean_msg:
            return {
                'success': True,
                'response': "Hello! I am your EduVerse AI Counselor. How can I assist you with your 12th course, college, or career guidance today?",
                'source': 'FALLBACK_GREETING'
            }

        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                gemini_resp = AICounselorService._call_gemini_api(clean_msg, student_context, gemini_key)
                if gemini_resp:
                    return {
                        'success': True,
                        'response': gemini_resp,
                        'source': 'GOOGLE_GEMINI_AI'
                    }
            except Exception as e:
                # Log and proceed to fallback
                pass

        # Robust rule-based fallback response
        fallback_resp = AICounselorService._generate_rule_based_response(clean_msg, student_context)
        return {
            'success': True,
            'response': fallback_resp,
            'source': 'RULE_BASED_COUNSELOR'
        }

    @staticmethod
    def _call_gemini_api(message: str, context: Optional[Dict[str, Any]], api_key: str) -> Optional[str]:
        """Calls Google Gemini REST API with student context."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        context_str = ""
        if context:
            context_str = (
                f"Student Profile Context:\n"
                f"- Name: {context.get('student_name', 'Student')}\n"
                f"- 12th Stream: {context.get('stream', 'Not specified')}\n"
                f"- Aggregate Percentage: {context.get('percentage', 'Not specified')}%\n"
                f"- Subject Marks: {context.get('subject_marks', {})}\n"
                f"- TNEA Cutoff: {context.get('tnea_cutoff', 'N/A')}\n"
                f"- Declared Interests: {context.get('interests', [])}\n"
                f"- Preferred District: {context.get('preferred_district', 'Tamil Nadu')}\n\n"
            )

        prompt_text = f"{context_str}Student Question: {message}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_text}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 650
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                result = json.loads(resp.read().decode('utf-8'))
                candidates = result.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    parts = candidates[0]['content'].get('parts', [])
                    if parts and 'text' in parts[0]:
                        return parts[0]['text']

        return None

    @staticmethod
    def _generate_rule_based_response(message: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Expert educational rule-based counseling logic.
        Responds to common queries with personalized recommendations.
        """
        msg_lower = message.lower()
        ctx = context or {}
        stream = ctx.get('stream', 'Science')
        pct = ctx.get('percentage')
        pct_str = f"your 12th score ({pct}%)" if pct else "your academic performance"
        interests = ctx.get('interests', [])
        int_str = f" and interests in {', '.join(interests)}" if interests else ""

        # Greeting Query
        if any(w in msg_lower for w in ['hello', 'hi', 'hey', 'greetings', 'vanakkam']):
            return (
                f"👋 **Vanakkam! Welcome to EduVerse AI Counselor.**\n\n"
                f"I am your personal education and career guide for Tamil Nadu higher education.\n"
                f"You can ask me questions like:\n"
                f"- *'Which courses suit my 12th marks?'*\n"
                f"- *'How is TNEA engineering cutoff computed?'*\n"
                f"- *'What are the career options after BCA?'*\n"
                f"- *'Which colleges in Coimbatore or Chennai should I explore?'*\n\n"
                f"How can I assist you with your education journey today?"
            )

        # Query 1: Which course or options are suitable for me?
        if any(w in msg_lower for w in ['which course', 'suitable course', 'what course', 'course recommendation', 'choose course', 'options', 'after 12th', 'degree', 'career after', 'study after']):
            if 'commerce' in stream.lower() or 'commerce' in msg_lower:
                return (
                    f"🎓 **Course Guidance for Commerce Students:**\n\n"
                    f"Based on {pct_str}{int_str}, here are top undergraduate options to explore:\n\n"
                    f"1. **B.Com (General / Professional Accounting):** Ideal for careers in corporate taxation, financial auditing, and preparing for **Chartered Accountancy (CA)**.\n"
                    f"2. **BCA (Bachelor of Computer Applications):** Many commerce students with or without maths thrive in BCA for software development, full-stack programming, and later **MCA**.\n"
                    f"3. **BBA (Bachelor of Business Administration):** Great foundation for leadership, brand management, operations, and progressing to an **MBA**.\n"
                    f"4. **B.Com Banking & Capital Markets:** Practical entry into retail banking and wealth management.\n\n"
                    f"💡 *Next Step:* Visit our **Course Recommendations** tab to see your detailed match score!"
                )
            elif 'arts' in stream.lower() or 'arts' in msg_lower:
                return (
                    f"🎓 **Course Guidance for Arts & Humanities:**\n\n"
                    f"Based on {pct_str}, you have diverse academic and civil pathways:\n\n"
                    f"1. **B.A. English / Journalism & Mass Communication:** Strong pathway into digital media, content strategy, and public relations.\n"
                    f"2. **B.A. Economics:** Analytical discipline with high demand in banking, policy research, and corporate consulting.\n"
                    f"3. **BBA / BCA:** Available to arts graduates in numerous universities, bridging management and digital computing.\n"
                    f"4. **Civil Services (UPSC / TNPSC):** B.A. programs in History or Political Science offer exceptional preparation.\n\n"
                    f"💡 *Tip:* Check out **Career Guidance** to see specific skills to build alongside your degree."
                )
            else:  # Science / Default
                return (
                    f"🎓 **Course Guidance for Science Students:**\n\n"
                    f"Based on {pct_str}{int_str}, here are premier options available across Tamil Nadu:\n\n"
                    f"1. **B.Tech / B.E. (Computer Science, AI & ML, IT):** 4-year engineering degrees leading to software engineering and systems architecture.\n"
                    f"2. **BCA (Bachelor of Computer Applications):** Fast-track 3-year program focusing directly on coding, web applications, and transitioning to **MCA**.\n"
                    f"3. **B.Sc Computer Science / Data Science:** Strong theoretical and mathematical foundation for algorithm development and scientific research.\n"
                    f"4. **B.Sc IT / Electronics:** Practical systems and network infrastructure programs.\n\n"
                    f"💡 *Next Step:* Enter your subject marks in our **Marks Assessment** module to compute your exact **TNEA Cutoff**!"
                )

        # Query 2: TNEA Cutoff
        if any(w in msg_lower for w in ['tnea', 'cutoff', 'cut off', 'formula']):
            tnea = ctx.get('tnea_cutoff')
            val_txt = ""
            if isinstance(tnea, dict):
                val_txt = f"\n\n📊 **Your Calculated Cutoff:**\n- Formula Cutoff: **{tnea.get('formula_cutoff')}**\n- Standard TN 200-Scale: **{tnea.get('standard_200_cutoff')} / 200**"

            return (
                f"📐 **Understanding Tamil Nadu TNEA Engineering Cutoff:**\n\n"
                f"The standardized formula used for admission into Anna University and affiliated engineering colleges is:\n\n"
                f"$$\\text{{TNEA Cutoff}} = \\frac{{\\text{{Mathematics}}}}{{2}} + \\frac{{\\text{{Physics}}}}{{4}} + \\frac{{\\text{{Chemistry}}}}{{4}}$$\n\n"
                f"On the standard **200-mark scale**:\n"
                f"- **Mathematics:** Max 100 marks\n"
                f"- **Physics:** Max 50 marks (Mark / 2)\n"
                f"- **Chemistry:** Max 50 marks (Mark / 2)\n"
                f"- **Total:** 200 marks{val_txt}\n\n"
                f"📌 *Note:* Cutoffs change annually depending on state seat availability and board results. Verify current counseling timelines on `tneaonline.org`."
            )

        # Query 3: Career options after BCA
        if any(w in msg_lower for w in ['after bca', 'bca career', 'bca jobs', 'bca options']):
            return (
                f"💻 **Career Pathways & Higher Studies after BCA:**\n\n"
                f"A Bachelor of Computer Applications provides rich software opportunities:\n\n"
                f"**1. Immediate Job Roles:**\n"
                f"- Full-Stack Web Developer (React, Node.js, Python)\n"
                f"- Software QA Engineer & Automation Tester\n"
                f"- Database Administrator (SQL & NoSQL)\n"
                f"- Technical Support & Cloud Operations Associate\n\n"
                f"**2. Higher Studies & Masters:**\n"
                f"- **MCA (Master of Computer Applications):** 2-year master's equivalent to B.Tech CSE in IT industry recruiting.\n"
                f"- **M.Sc Computer Science / Data Science**\n"
                f"- **MBA in Technology Management**\n\n"
                f"**3. Core Skills to Develop:**\n"
                f"- Git version control, Data Structures, and cloud deployments."
            )

        # Query 4: What colleges can I explore?
        if any(w in msg_lower for w in ['colleges', 'which college', 'best college', 'tamil nadu college', 'find college']):
            return (
                f"🏛️ **Exploring Colleges in EduVerse AI:**\n\n"
                f"Our directory indexes **1,129 higher education institutions across all 38 districts of Tamil Nadu**:\n\n"
                f"- **Government & Autonomous Colleges:** GCT Coimbatore, CEG Guindy, Madras Christian College, Loyola College, GCE Salem, ACGCET Karaikudi, etc.\n"
                f"- **Verified Official Websites:** Click the **'Visit Official Website'** button on any college card to inspect genuine admission bulletins directly.\n"
                f"- **Interactive District Filter:** Browse colleges in Chennai, Coimbatore, Madurai, Tiruchirappalli, Salem, and beyond using our **Explore Colleges** page.\n\n"
                f"🔍 Visit **College Matching** from your assessment results to see institutions tailored to your preferences!"
            )

        # Query 5: Which skills should I learn?
        if any(w in msg_lower for w in ['skill', 'skills', 'learn', 'preparation']):
            return (
                f"🚀 **High-Impact Skills for Students After 12th:**\n\n"
                f"Regardless of your chosen stream, investing in these skills creates a significant advantage:\n\n"
                f"1. **Programming Fundamentals:** Start with Python or JavaScript on free platforms like freeCodeCamp or CS50.\n"
                f"2. **Data & Spreadsheet Fluency:** Advanced Microsoft Excel and basic SQL are prized across both IT and business.\n"
                f"3. **Communication & Presentation:** English proficiency and structured email/report writing.\n"
                f"4. **Problem-Solving & Critical Thinking:** Aptitude puzzles, logical reasoning, and basic algorithmic concepts."
            )

        # Query 6: Higher studies vs direct job
        if any(w in msg_lower for w in ['higher study', 'higher studies', 'masters', 'job vs', 'pg']):
            return (
                f"📚 **Higher Studies vs Immediate Employment:**\n\n"
                f"- **Direct Employment After UG:** 3-year degrees (BCA, B.Sc, B.Com, BBA) allow you to enter junior IT or corporate roles, gain practical experience, and pursue part-time or executive masters later.\n"
                f"- **Pursuing Masters (MCA / MBA / M.Tech / M.Sc):** Provides deeper specialization, opens senior technical architecture roles, and unlocks higher campus placement salary bands.\n\n"
                f"💡 *Recommendation:* Build practical projects during your undergraduate degree; your final-year performance will clearly indicate if immediate work or a Master's program is optimal!"
            )

        # General Personalized Response
        return (
            f"🤝 **Personalized Counseling Insight:**\n\n"
            f"Hello {ctx.get('student_name', 'Student')}! Looking at your 12th profile ({stream} stream, {pct_str}):\n\n"
            f"- **Educational Pathway:** Focus on programs that combine practical skills with accredited university degrees.\n"
            f"- **Explore Options:** Check out our **Course Recommendations** for suitability scores and career roadmaps.\n"
            f"- **Institution Verification:** Use our verified institutional links to examine faculty, amenities, and syllabus.\n\n"
            f"Feel free to ask me questions like: *'What are the career options after BCA?'*, *'How is TNEA cutoff computed?'*, or *'What courses suit my Commerce marks?'*!"
        )

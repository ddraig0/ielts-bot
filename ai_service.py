import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def ask_claude(system_prompt: str, user_message: str, max_tokens: int = 1500) -> str:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text

# ─── READING ───────────────────────────────────────────────────────────────────
def generate_reading_passage(topic: str = None) -> dict:
    topics = ["climate change", "technology", "history", "science", "society", "business", "health"]
    import random
    topic = topic or random.choice(topics)
    
    system = """You are an IELTS Reading expert. Generate a realistic IELTS Academic Reading passage with questions.
Return ONLY valid JSON in this exact format, nothing else:
{
  "topic": "...",
  "passage": "...(400-500 words)...",
  "questions": [
    {"num": 1, "type": "True/False/Not Given", "question": "...", "answer": "TRUE/FALSE/NOT GIVEN", "explanation": "..."},
    {"num": 2, "type": "Multiple Choice", "question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A", "explanation": "..."},
    {"num": 3, "type": "Fill in the blank", "question": "The passage states that ___ is important.", "answer": "...", "explanation": "..."},
    {"num": 4, "type": "True/False/Not Given", "question": "...", "answer": "NOT GIVEN", "explanation": "..."},
    {"num": 5, "type": "Multiple Choice", "question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "B", "explanation": "..."}
  ]
}"""
    
    result = ask_claude(system, f"Generate an IELTS Reading passage about: {topic}")
    import json, re
    # Clean up JSON
    result = re.sub(r'```json|```', '', result).strip()
    return json.loads(result)

def check_reading_answer(question: dict, user_answer: str) -> dict:
    correct = question["answer"].strip().upper()
    user = user_answer.strip().upper()
    
    # Normalize
    if user in ["A", "B", "C", "D"] and correct in ["A", "B", "C", "D"]:
        is_correct = user == correct
    elif any(x in user for x in ["TRUE", "FALSE", "NOT GIVEN", "T", "F", "N"]):
        mapping = {"T": "TRUE", "F": "FALSE", "N": "NOT GIVEN", "NG": "NOT GIVEN"}
        normalized = mapping.get(user, user)
        is_correct = normalized == correct
    else:
        is_correct = user.lower() == correct.lower()
    
    return {
        "is_correct": is_correct,
        "correct_answer": question["answer"],
        "explanation": question.get("explanation", "")
    }

# ─── LISTENING ─────────────────────────────────────────────────────────────────
def generate_listening_exercise() -> dict:
    import random
    scenarios = [
        "a conversation between a student and a university advisor about course registration",
        "a radio broadcast about environmental issues",
        "a lecture excerpt about historical events",
        "a conversation at a hotel reception desk",
        "a discussion between flatmates about household chores"
    ]
    scenario = random.choice(scenarios)
    
    system = """You are an IELTS Listening expert. Since actual audio is not available, create a transcript-based exercise.
Return ONLY valid JSON in this exact format:
{
  "scenario": "...",
  "transcript": "...(realistic dialogue or monologue, 200-300 words)...",
  "note": "📖 Bu tapşırıqda transkrip verilir — real imtahanda siz audio dinləyərdiniz.",
  "questions": [
    {"num": 1, "question": "...", "answer": "...", "hint": "..."},
    {"num": 2, "question": "...", "answer": "...", "hint": "..."},
    {"num": 3, "question": "...", "answer": "...", "hint": "..."},
    {"num": 4, "question": "...", "answer": "...", "hint": "..."}
  ]
}"""
    
    result = ask_claude(system, f"Create IELTS Listening exercise for: {scenario}")
    import json, re
    result = re.sub(r'```json|```', '', result).strip()
    return json.loads(result)

def check_listening_answer(question: dict, user_answer: str) -> dict:
    system = "You are an IELTS examiner. Evaluate if the student's answer is correct or acceptable. Be somewhat flexible with minor spelling/wording variations. Reply ONLY with JSON: {\"is_correct\": true/false, \"feedback\": \"brief explanation\"}"
    prompt = f"Correct answer: {question['answer']}\nStudent answer: {user_answer}"
    result = ask_claude(system, prompt, max_tokens=200)
    import json, re
    result = re.sub(r'```json|```', '', result).strip()
    return json.loads(result)

# ─── WRITING ───────────────────────────────────────────────────────────────────
def generate_writing_task(task_type: str = "task2") -> dict:
    import random
    
    if task_type == "task1":
        charts = [
            "a bar chart showing internet usage by age group from 2010 to 2020",
            "a pie chart illustrating the distribution of household expenses in a typical family",
            "a line graph showing changes in three countries' GDP over 10 years",
            "a table comparing tourism statistics in 5 major cities"
        ]
        topic = random.choice(charts)
        prompt_text = f"The diagram below shows {topic}.\nSummarise the information by selecting and reporting the main features, and make comparisons where relevant."
        word_count = "at least 150 words"
        time_limit = "20 minutes"
    else:
        topics = [
            "Some people believe that technology has made our lives more complicated. To what extent do you agree or disagree?",
            "Many governments believe that economic progress is the most important goal. Others argue that other types of progress are equally important. Discuss both views and give your opinion.",
            "In many countries, the gap between the rich and the poor is widening. What problems does this cause? What measures can be taken to reduce inequality?",
            "Some people think that children should begin their formal education at a very early age. Others believe that they should not go to school until they are older. Discuss both views and give your own opinion."
        ]
        prompt_text = random.choice(topics)
        word_count = "at least 250 words"
        time_limit = "40 minutes"
    
    return {
        "task_type": task_type.upper(),
        "prompt": prompt_text,
        "word_count": word_count,
        "time_limit": time_limit
    }

def evaluate_writing(task_prompt: str, task_type: str, user_essay: str) -> str:
    system = f"""You are a certified IELTS examiner. Evaluate the following IELTS Writing {task_type.upper()} response.
Provide detailed feedback in Azerbaijani language using this structure:

📊 **BAND SCORE: X.X / 9.0**

**Task Achievement/Response: X/9**
[feedback]

**Coherence & Cohesion: X/9**
[feedback]

**Lexical Resource: X/9**
[feedback]

**Grammatical Range & Accuracy: X/9**
[feedback]

**💪 Güclü tərəflər:**
- [point]

**🔧 Zəif tərəflər & Tövsiyələr:**
- [point]

**✏️ Nümunə düzəliş:**
[Show 1-2 specific sentence improvements]

Be honest and constructive. Base scoring on official IELTS band descriptors."""

    prompt = f"Task prompt: {task_prompt}\n\nStudent's response:\n{user_essay}"
    return ask_claude(system, prompt, max_tokens=2000)

# ─── SPEAKING ──────────────────────────────────────────────────────────────────
def generate_speaking_question(part: int) -> dict:
    import random
    
    if part == 1:
        topics = [
            ["Do you work or study?", "What do you enjoy most about your work/studies?", "How do you usually spend your weekends?"],
            ["Do you like cooking?", "What kind of food do you usually eat?", "Have you ever tried food from another country?"],
            ["What hobbies do you have?", "How long have you been interested in this hobby?", "Do you think hobbies are important? Why?"]
        ]
        q_set = random.choice(topics)
        return {"part": 1, "title": "Part 1: Personal Questions", "questions": q_set, "time": "4-5 minutes", "tip": "Answer naturally and expand your answers. Don't give one-word replies!"}
    
    elif part == 2:
        cue_cards = [
            {
                "title": "Describe a memorable trip you have taken",
                "points": ["Where you went", "Who you went with", "What you did there", "Why it was memorable"],
                "follow_up": "Do you think travel broadens the mind?"
            },
            {
                "title": "Describe a person who has influenced you",
                "points": ["Who this person is", "How you know them", "What they did", "How they influenced you"],
                "follow_up": "Do you think famous people have a greater influence than ordinary people?"
            },
            {
                "title": "Describe a skill you would like to learn",
                "points": ["What the skill is", "Why you want to learn it", "How you would learn it", "How useful it would be"],
                "follow_up": "What skills are most important for young people today?"
            }
        ]
        card = random.choice(cue_cards)
        return {"part": 2, "title": "Part 2: Cue Card", "cue_card": card, "prep_time": "1 minute", "speak_time": "1-2 minutes"}
    
    else:
        discussions = [
            {
                "theme": "Education & Technology",
                "questions": [
                    "How has technology changed the way people learn?",
                    "Do you think online education can replace traditional schooling?",
                    "What are the advantages of lifelong learning?"
                ]
            },
            {
                "theme": "Environment & Society",
                "questions": [
                    "Who is more responsible for protecting the environment — individuals or governments?",
                    "How can cities become more environmentally friendly?",
                    "Do you think future generations will face more environmental challenges?"
                ]
            }
        ]
        disc = random.choice(discussions)
        return {"part": 3, "title": f"Part 3: Discussion — {disc['theme']}", "questions": disc["questions"], "time": "4-5 minutes", "tip": "Give detailed answers with reasons and examples. Discuss different perspectives!"}

def evaluate_speaking(part: int, question: str, user_response: str) -> str:
    system = """You are a certified IELTS Speaking examiner. Evaluate the written version of a student's speaking response.
Provide feedback in Azerbaijani using this format:

🎙️ **SPEAKING DEĞERLENDİRMƏ**

**Tahmini Band Score: X.X / 9.0**

**Fluency & Coherence: X/9** — [feedback]
**Lexical Resource: X/9** — [feedback]  
**Grammatical Range: X/9** — [feedback]
**Pronunciation (yazıdan qiymətləndirilir): N/A**

**✅ Yaxşı tərəflər:**
- [point]

**📈 İnkişaf üçün:**
- [point with example correction]

**💡 İpucu:** [one practical speaking tip]"""

    prompt = f"IELTS Speaking Part {part}\nQuestion: {question}\nStudent response: {user_response}"
    return ask_claude(system, prompt, max_tokens=1500)

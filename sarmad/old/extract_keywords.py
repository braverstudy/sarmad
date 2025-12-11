import google.generativeai as genai

# Setup (Use Gemini 1.5 Flash - it's cheaper and faster than GPT-3.5)
model = genai.GenerativeModel('gemini-1.5-flash')

def llm_extract(text):
    prompt = f"""
    Extract the main topics/entities from this Arabic text.
    Rules:
    1. Output ONLY the keywords separated by commas.
    2. Ignore verbs (went, saw) and filler words.
    3. Fix typos (e.g., 'الشارعط' -> 'الشارع').
    4. Ignore laughter.
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return response.text.strip()


Result = "ههههه الناس تتضارب بالشارعط"
print(llm_extract(Result))
# Output: "الناس, الشارع, مضاربة" (It actually fixes the typo and understands context)
from flask import Flask, render_template, request
import re

app = Flask(__name__)
def grammar_ai(text):
    errors = []
    seen_issues = set()
    corrected = text
    rules = [
        (r"\bi\b", "I", "Pronoun 'I' must always be capitalized"),
        (r"(^|\.\s+)([a-z])",
         lambda m: m.group(1) + m.group(2).upper(),
         "Sentence should start with a capital letter"),

        (r"\ba ([aeiouAEIOU]\w*)", r"an \1",
         "Use 'an' before vowel sounds"),
        (r"\ban ([^aeiouAEIOU\s]\w*)", r"a \1",
         "Use 'a' before consonant sounds"),

        (r"\b(I|You|We|They) is\b", r"\1 are",
         "Incorrect subject–verb agreement"),
        (r"\b(He|She|It) are\b", r"\1 is",
         "Singular subject must use 'is'"),

        (r"\bI has\b", "I have",
         "Incorrect tense usage"),
        (r"\bHe have\b", "He has",
         "Incorrect verb form"),
        (r"\bThey has\b", "They have",
         "Plural subject must use 'have'"),

        (r"\s,", ",", "Remove space before comma"),
        (r",(?=\S)", ", ", "Add space after comma"),
        (r"\s\.", ".", "Remove space before period"),
        (r"\.\.+", ".", "Avoid repeated periods"),
        (r"\?\?+", "?", "Avoid repeated question marks"),
        (r"!!+", "!", "Avoid repeated exclamation marks"),

        (r'""+', '"', "Avoid duplicate quotation marks"),
        (r"\b(\w+)\s+\1\b", r"\1", "Avoid repeated words"),

        (r"\bthis side\b", "this is",
         "Incorrect informal phrase usage"),
        (r"\ba lot of\b", "many",
         "Use concise formal expression"),
    ]

    for pattern, replacement, explanation in rules:
        matches = list(re.finditer(pattern, corrected, flags=re.IGNORECASE))

        for m in matches:
            issue = m.group()
            issue_key = issue.lower()

            if issue_key not in seen_issues:
                seen_issues.add(issue_key)
                errors.append({
                    "issue": issue,
                    "correction": replacement if isinstance(replacement, str) else "Correct form",
                    "message": explanation
                })

        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

    # Sentence-ending punctuation check (ONLY ONCE)
    if corrected and corrected[-1] not in ".!?":
        corrected += "."
        if "missing punctuation" not in seen_issues:
            errors.append({
                "issue": "Missing punctuation",
                "correction": ".",
                "message": "Sentence should end with proper punctuation"
            })

    return corrected, errors

def highlight_errors(text, errors):
    highlighted = text
    for e in errors:
        if e["issue"] != "Missing punctuation":
            highlighted = re.sub(
                re.escape(e["issue"]),
                f"<span class='highlight'>{e['issue']}</span>",
                highlighted,
                count=1,
                flags=re.IGNORECASE
            )
    return highlighted

@app.route("/", methods=["GET", "POST"])
def index():
    original_text = ""
    corrected_text = ""
    errors = []
    score = None
    highlighted_text = ""

    if request.method == "POST":
        original_text = request.form.get("text", "").strip()

        if original_text:
            corrected_text, errors = grammar_ai(original_text)
            highlighted_text = highlight_errors(original_text, errors)

            if errors:
                score = max(50, 100 - len(errors) * 15)
            else:
                score = 100

    return render_template(
        "index.html",
        original_text=original_text,
        corrected_text=corrected_text,
        errors=errors,
        score=score,
        highlighted_text=highlighted_text
    )

if __name__ == "__main__":
    app.run(debug=False)

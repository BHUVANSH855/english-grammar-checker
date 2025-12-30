from flask import Flask, render_template, request
import language_tool_python

app = Flask(__name__)

tool = language_tool_python.LanguageTool('en-US')

@app.route("/", methods=["GET", "POST"])
def index():
    corrected_text = ""
    explanation = ""

    if request.method == "POST":
        user_text = request.form.get("text")

        matches = tool.check(user_text)
        corrected_text = language_tool_python.utils.correct(user_text, matches)

        explanation_list = []
        for match in matches:
            explanation_list.append(match.message)

        explanation = "\n".join(explanation_list)

    return render_template(
        "index.html",
        corrected_text=corrected_text,
        explanation=explanation
    )

if __name__ == "__main__":
    app.run(debug=True)

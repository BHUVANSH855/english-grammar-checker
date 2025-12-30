from flask import Flask, render_template, request
import language_tool_python
from language_tool_python.exceptions import RateLimitError

app = Flask(__name__)

tool = None  # lazy initialization


def get_tool():
    global tool
    if tool is None:
        tool = language_tool_python.LanguageToolPublicAPI('en-US')
    return tool


@app.route("/", methods=["GET", "POST"])
def index():
    original_text = ""
    corrected_text = ""
    explanations = []
    error = None

    if request.method == "POST":
        original_text = request.form.get("text", "").strip()

        if not original_text:
            error = "Please enter some text to check."
        else:
            try:
                tool_instance = get_tool()
                matches = tool_instance.check(original_text)

                corrected_text = language_tool_python.utils.correct(
                    original_text, matches
                )

                explanations = [m.message for m in matches]

            except RateLimitError:
                error = (
                    "⚠️ Free LanguageTool API rate limit reached. "
                    "Please wait a few minutes and try again."
                )

            except Exception:
                error = "⚠️ Something went wrong. Please try again later."

    return render_template(
        "index.html",
        original_text=original_text,
        corrected_text=corrected_text,
        explanations=explanations,
        error=error
    )


if __name__ == "__main__":
    # Disable reloader to avoid multiple API hits
    app.run(debug=True, use_reloader=False)

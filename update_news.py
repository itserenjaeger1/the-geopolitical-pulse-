import os
import time
import re
import feedparser
from google import genai

# 1. Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# Add this line to clean the hidden spaces or newlines
api_key = api_key.strip()    

#genai.configure(api_key=api_key)
## Replace with new gen_api key
client = genai.Client(api_key=api_key)
#model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Define High-Quality RSS Feeds below is old block , new one is below for RSS feeds
#FEEDS = {
#    "UN Global News": "https://un.org",
#    "CNBC World Economy": "https://cnbc.com"
#}

FEEDS = {
    "UN Global News": "https://news.un.org/feed/view/en/story/ticker/rss",
    "CNBC World Economy": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362"
}

html_articles = ""

# 3. Fetch and Process Feeds
for source_name, url in FEEDS.items():
    print(f"Fetching feeds from: {source_name}")
    feed = feedparser.parse(url)
    
    for entry in feed.entries[:3]:
        title = entry.get("title", "Global Update")
        link = entry.get("link", "#")
        summary = entry.get("summary", entry.get("description", "No summary provided."))
        
        prompt = (
            f"Analyze the following headline and summary. Provide exactly two short bullet points explaining its macro socioeconomic or geopolitical significance. "
            f"Keep them short. Do not include introductory text.\n\n"
            f"Headline: {title}\n"
            f"Summary: {summary}"
        )
        
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

            # removes bold formatting
            ai_text = response.text.replace("**", "").replace("*", "").strip()

            lines = ai_text.split("\n")
            bullets_html = ""

            for line in lines:
                # strips bullets or numbered-list prefixes
                clean_line = re.sub(
                    r"^[-•+]\s*|^\d+\.\s*",
                    "",
                    line.strip()
                ).strip()

                if clean_line:
                    bullets_html += f"<li>{clean_line}</li>"

            html_articles += f"""
            <div class="card">
                <div class="source">{source_name}</div>
                <h2><a href="{link}" target="_blank">{title}</a></h2>
                <ul>{bullets_html}</ul>
            </div>
            """

        except Exception as e:
            print(f"Error processing '{title}': {e}")

        time.sleep(2)
# 4. Generate the Final Dashboard Template
current_date = time.strftime("%B %d, %Y at %I:%M %p")
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Geopolitical Briefing</title>
    <style>
        :root {{
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --text-color: #c9d1d9;
            --accent-color: #58a6ff;
            --border-color: #30363d;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 800px;
            width: 100%;
        }}
        header {{
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            margin: 0 0 10px 0;
            font-size: 2rem;
            color: #f0f6fc;
        }}
        .date {{
            color: #8b949e;
            font-size: 0.95rem;
        }}
        .grid {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 24px;
        }}
        .source {{
            display: inline-block;
            background-color: rgba(88, 166, 255, 0.15);
            color: var(--accent-color);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        h2 {{
            margin: 0 0 12px 0;
            font-size: 1.35rem;
        }}
        h2 a {{
            color: #f0f6fc;
            text-decoration: none;
        }}
        h2 a:hover {{
            color: var(--accent-color);
            text-decoration: underline;
        }}
        ul {{
            margin: 0;
            padding-left: 20px;
            color: #f0f6fc;
        }}
        li {{
            margin-bottom: 8px;
            line-height: 1.5;
            color: #b1bac4;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Socioeconomic & Geopolitical Brief Updated Test</h1>
            <div class="date">Updated automatically on {current_date}</div>
        </header>
        <div class="grid">
            {html_articles}
        </div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
print("Dashboard updated successfully!")

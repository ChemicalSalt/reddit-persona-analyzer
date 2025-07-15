import asyncio
from playwright.async_api import async_playwright
from collections import Counter, defaultdict
import re
import nltk
from nltk.corpus import stopwords
import spacy

nlp = spacy.load("en_core_web_sm")

def ensure_nltk():
    resources = ["punkt", "stopwords"]
    for res in resources:
        try:
            nltk.data.find(f"corpora/{res}")
        except LookupError:
            nltk.download(res)

ensure_nltk()

EXTRA_STOP_WORDS = {
    "see", "would", "something", "still", "made", "new", "one", "like", "also",
    "guys", "know", "get", "got", "really", "think", "people", "just", "much",
    "good", "well", "want", "need", "time", "day", "years", "year",
    "say", "says", "don", "did", "does", "ok", "okay", "yes", "no", "yeah",
    "lol", "thanks", "thank", "hi", "hello", "hey"
}

STOP_WORDS = set(stopwords.words("english")).union(EXTRA_STOP_WORDS)

def extract_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        lemma = token.lemma_.lower()
        if (
            token.pos_ in {"NOUN", "PROPN", "VERB"} 
            and token.is_alpha
            and lemma not in STOP_WORDS
        ):
            keywords.append(lemma)
    return keywords

# Helper to turn keywords into more natural descriptive phrases
def describe_keyword(keyword, category):
    # Simple heuristic phrases by category
    keyword = keyword.lower()
    if category == "traits":
        phrases = {
            "gaming": "Enjoys gaming and esports culture",
            "ai": "Interested in AI and emerging technologies",
            "nyc": "Engaged with NYC-related topics and lifestyle",
            "make": "Creative and enjoys making or building things",
            "use": "Practical and focused on applying knowledge",
            "thought": "Reflective and thoughtful in discussions",
            "guy": "Shares personal perspectives often",
        }
        return phrases.get(keyword, f"Shows interest in {keyword}")
    elif category == "interests":
        phrases = {
            "post": "Active in posting content",
            "thread": "Participates in discussion threads",
            "seasonal": "Follows seasonal trends or events",
            "ai": "Interested in AI advancements",
            "buying": "Engages in buying or investing topics",
        }
        return phrases.get(keyword, f"Interested in {keyword}")
    elif category == "goals":
        phrases = {
            "character": "Focuses on character development or traits",
            "holder": "Concerned with holding or maintaining assets",
            "exploit": "Looks into exploiting opportunities or systems",
            "investing": "Interested in investment and finance",
            "update": "Keeps information current and updated",
        }
        return phrases.get(keyword, f"Aims to achieve {keyword}")
    return f"Interested in {keyword}"

async def scroll_and_collect(page, selector, max_items=100, max_scrolls=80):
    seen, last_height, scrolls = set(), None, 0
    while len(seen) < max_items and scrolls < max_scrolls:
        nodes = await page.query_selector_all(selector)
        seen.update(nodes)
        await page.mouse.wheel(0, 3000)
        await asyncio.sleep(3)
        height = await page.evaluate("document.body.scrollHeight")
        if height == last_height:
            break
        last_height, scrolls = height, scrolls + 1
    return list(seen)[:max_items]

async def scrape_reddit_user(username, max_posts=100, max_comments=100):
    base = f"https://www.reddit.com/user/{username}/"
    posts_url, comments_url = base + "posts/", base + "comments/"

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Exception as e:    
             print(f"❌ Failed to launch browser: {e}")
             return None
        ctx = await browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        ))
        page = await ctx.new_page()

        async def accept_cookies():
            try:
                await page.locator("button:has-text('Accept')").click(timeout=4000)
            except:
                pass

        # ── POSTS ──
        await page.goto(posts_url, timeout=60000)
        await accept_cookies()
        try:
            await page.wait_for_selector("a[slot='full-post-link'] faceplate-screen-reader-content", timeout=15000)
        except:
            print("⚠️ No post titles detected. User may have no posts or structure changed.")

        post_nodes = await scroll_and_collect(page, "a[slot='full-post-link'] faceplate-screen-reader-content", max_posts)
        posts = [{"title": await n.inner_text(), "body": ""} for n in post_nodes]

        # ── COMMENTS ──
        await page.goto(comments_url, timeout=60000)
        await accept_cookies()
        try:
            await page.wait_for_selector("a[aria-label^='Thread for']", timeout=15000)
        except:
            print("⚠️ No comments detected. User may have no comments or structure changed.")

        comment_nodes = await scroll_and_collect(page, "a[aria-label^='Thread for']", max_comments)
        comments = []
        for node in comment_nodes:
            label = await node.get_attribute("aria-label")
            if label:
                match = re.search(r"comment on (.+)", label)
                if match:
                    comment_text = match.group(1).strip()
                    comments.append({"body": comment_text})
        await browser.close()

        if not posts and not comments:
            print("❌ Nothing scraped. Either the user has no activity or Reddit changed its layout.")
            return None

        return posts, comments

def build_user_persona(posts, comments, username="Unknown"):
    wc, src = Counter(), defaultdict(list)

    def add(kind, text):
        words_added = set()
        keywords = extract_keywords(text)
        for w in keywords:
            if w in words_added:
                continue
            wc[w] += 1
            words_added.add(w)
            if len(src[w]) < 3:
                src[w].append((kind, text))

    for p in posts:
        add("post", p["title"])
    for c in comments:
        add("comment", c["body"])

    if not wc:
        return "Not enough data to generate a persona."

    common = wc.most_common(15)

    traits = [w for w, _ in common[:5]]
    interests = [w for w, _ in common[5:10]]
    goals = [w for w, _ in common[10:15]]

    top_word = common[0][0]
    quote = src[top_word][0][1]

    lines = [
        "USER PERSONA",
        "="*40,
        "",
        f"Name             : Unknown",
        f"Reddit Handle    : u/{username}",
        "Age Group        : Not evident",
        "Location         : Not available",
        "Occupation       : Not evident",
        "",
        "-"*40,
        "Personality Traits:",
        "-"*40,
    ]

    lines += [f"• {describe_keyword(trait, 'traits')}" for trait in traits]

    lines += [
        "",
        "-"*40,
        "Interests:",
        "-"*40,
    ]

    lines += [f"• {describe_keyword(interest, 'interests')}" for interest in interests]

    lines += [
        "",
        "-"*40,
        "Goals:",
        "-"*40,
    ]

    lines += [f"• {describe_keyword(goal, 'goals')}" for goal in goals]

    lines += [
        "",
        "-"*40,
        "Frustrations:",
        "-"*40,
        "• Not clearly stated",
        "",
        "-"*40,
        "Quote:",
        "-"*40,
        f"\"{quote[:197] + ('...' if len(quote) > 200 else '')}\"",
        "",
        "-"*40,
        "Citations:",
        "-"*40,
    ]

    added_snippets = set()
    citations_count = 0
    for w, _ in common:
        for kind, snippet in src[w]:
            snippet_short = snippet[:80] + ("..." if len(snippet) > 80 else "")
            if snippet_short not in added_snippets:
                added_snippets.add(snippet_short)
                lines.append(f"{citations_count+1}. \"{snippet_short}\"")
                lines.append(f"   — Cited from {kind}")

                citations_count += 1
                if citations_count >= 5:
                    break
        if citations_count >= 5:
            break

    lines += [
        "",
        "-"*40,
        "Note:",
        "This persona was auto‑generated from publicly available Reddit activity.",
    ]

    return "\n".join(lines)

if __name__ == "__main__":
    username = input("Enter Reddit username (without /user/): ").strip()
    result = asyncio.run(scrape_reddit_user(username, max_posts=200, max_comments=200))
    if result is None:
        print("❌ No posts or comments scraped. Exiting.")
        exit()

    posts, comments = result

    print(f"Scraped {len(posts)} posts and {len(comments)} comments.")

    persona = build_user_persona(posts, comments, username)
    print("\n=== Generated User Persona ===\n")
    print(persona)

    with open(f"{username}_persona.txt", "w", encoding="utf-8") as fp:
        fp.write(persona)
    print(f"\nPersona saved to {username}_persona.txt")

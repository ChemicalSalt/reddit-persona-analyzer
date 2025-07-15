# Reddit Persona Analyzer

This project scrapes a Reddit user's public posts and comments and generates a detailed user persona based solely on that data, citing original posts/comments. It is part of the BeyondChats AI/LLM Engineer Intern assignment.

## Setup and Usage

1. Clone this repository:
git clone https://github.com/ChemicalSalt/reddit-persona-analyzer.git
cd reddit-persona-analyzer

2. (Optional) Create and activate a Python virtual environment:
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Create a `.env` file in the project root with your API keys:
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_user_agent
OPENAI_API_KEY=your_openai_api_key

5. Run the script with a Reddit profile URL argument:
python reddit_persona.py https://www.reddit.com/user/username/

The output persona text file will be saved in the project folder.

## Requirements

- Python 3.8+
- praw
- openai
- python-dotenv
- tqdm

## Notes

- Only publicly available Reddit data is accessed.
- No private or sensitive user data is collected.
- Code follows PEP-8 style guidelines.
- Persona is generated strictly from scraped data with citations.
- This repo is the submission for the BeyondChats internship assignment.

For any queries, contact BeyondChats on Internshala.

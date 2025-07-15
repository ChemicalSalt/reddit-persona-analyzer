# Reddit Persona Analyzer

 Reddit Persona Analyzer scrapes a Reddit user's public posts and comments and generates a detailed user persona based solely on that data, citing original posts/comments. 

## Setup and Usage

1. Clone this repository:  
git clone https://github.com/ChemicalSalt/reddit-persona-analyzer.git  
cd reddit-persona-analyzer

2. (Optional) Create and activate a Python virtual environment:  
python -m venv venv  
Windows: venv\Scripts\activate  
macOS/Linux: source venv/bin/activate

3. Install dependencies:  
pip install -r requirements.txt

4. Install Playwright browsers:  
playwright install

5. Download SpaCy English model:  
python -m spacy download en_core_web_sm

6. Run the script:  
python reddit_persona.py  
- When prompted, enter the Reddit username (without `/user/` or full URL).  
- The output persona text file (`<username>_persona.txt`) will be saved in the project folder.

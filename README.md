# Restaurant Review Analysis with AutoGen

## Project Overview
This project uses the AutoGen framework to analyze restaurant reviews, extracting and aggregating scores for food quality and customer service based on qualitative review data. (Based on UC Berkeley MOOC LAB1 - [Large Language Model Agents](https://llmagents-learning.org/f24) LAB1)

## Prerequisites
- Python 3.x
- OpenAI API Key
- Virtual environment recommended

## Setup Instructions

1. Clone the repository
```bash
git clone <repository-url>
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set OpenAI API Key
```bash
export OPENAI_API_KEY='your-openai-api-key'  # On Windows, use `set OPENAI_API_KEY=your-openai-api-key`
```

## Running the Project
```bash
python main.py "How good is Subway as a restaurant?"
```

## Features
- Fetch restaurant reviews
- Analyze reviews for food and service scores
- Calculate overall restaurant rating
- Query restaurant performance


## Notes
- Uses GPT-4o-mini model
- Recommended for educational purposes
- Supports queries like "How good is Subway as a restaurant?"



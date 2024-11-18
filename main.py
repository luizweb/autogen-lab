from typing import Dict, List, Tuple
from autogen import ConversableAgent
import math
import sys
import os


from dotenv import load_dotenv
load_dotenv()



def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    """
    Fetches restaurant reviews from a text file based on restaurant name.
    
    Args:
        restaurant_name (str): Name of the restaurant to fetch reviews for
        
    Returns:
        Dict[str, List[str]]: Dictionary with restaurant name as key and list of reviews as value
        
    Example:
        >>> fetch_restaurant_data("Applebee's")
        {"Applebee's": ["The food at Applebee's was average, with nothing particularly standing out.", ...]}
    """
    reviews: List[str] = []
    
    try:
        with open('restaurant-data.txt', 'r', encoding='utf-8') as file:
            for line in file:
                # Split at the first period to separate restaurant name and review
                parts = line.strip().split('. ', 1)
                if len(parts) != 2:
                    continue
                    
                current_restaurant, review = parts
                
                # Check if this review is for our target restaurant
                if current_restaurant.lower() == restaurant_name.lower():
                    reviews.append(review)
    
    except FileNotFoundError:
        raise FileNotFoundError("restaurant-data.txt file not found")
    except Exception as e:
        raise Exception(f"Error processing restaurant data: {str(e)}")
    
    # If no reviews found, return empty list
    return {restaurant_name: reviews}




def extract_restaurant_scores(restaurant_name: str, reviews: List[str]) -> Tuple[str, List[int], List[int]]:
    """
    Extracts food and customer service scores from a list of reviews for a given restaurant.
    
    Args:
        restaurant_name (str): The name of the restaurant
        reviews (List[str]): List of reviews about the restaurant
        
    Returns:
        Tuple[str, List[int], List[int]]: Tuple of restaurant name, list of food scores, and list of customer service scores
    """
    food_scores: List[int] = []
    customer_service_scores: List[int] = []

    # Define keywords for each score
    score_keywords = {
        1: ["awful", "horrible", "disgusting"],
        2: ["bad", "unpleasant", "offensive"],
        3: ["average", "uninspiring", "forgettable"],
        4: ["good", "enjoyable", "satisfying"],
        5: ["awesome", "incredible", "amazing"]
    }
    
    # Function to determine the score from a review segment based on keywords
    def get_score(segment: str) -> int:
        for score, keywords in score_keywords.items():
            if any(keyword in segment.lower() for keyword in keywords):
                return score
        return 3  # Default to 3 if no keywords found (neutral rating)

    # Process each review
    for review in reviews:
        # Split review into food and customer service sections
        segments = review.split('.')
        if len(segments) >= 2:
            food_review = segments[0].strip()
            customer_service_review = segments[1].strip()
            
            # Extract scores for each part
            food_scores.append(get_score(food_review))
            customer_service_scores.append(get_score(customer_service_review))
    
    return restaurant_name, food_scores, customer_service_scores


    


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    """
    Calculates an overall restaurant score based on food and customer service ratings.
    
    Args:
        restaurant_name (str): Name of the restaurant
        food_scores (List[int]): List of food scores (1-5)
        customer_service_scores (List[int]): List of customer service scores (1-5)
        
    Returns:
        Dict[str, float]: Dictionary with restaurant name as key and calculated score as value
        
    Formula:
        score = SUM(sqrt(food_scores[i]**2 * customer_service_scores[i])) * 1/(N * sqrt(125)) * 10
        
    Example:
        >>> calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
        {"Applebee's": 5.048}
    """
    # Validate input lengths match
    if len(food_scores) != len(customer_service_scores):
        raise ValueError("Food scores and customer service scores must have the same length")
    
    # Validate input ranges
    if not all(1 <= score <= 5 for score in food_scores + customer_service_scores):
        raise ValueError("All scores must be between 1 and 5")
    
    N = len(food_scores)
    if N == 0:
        return {restaurant_name: 0.000}
    
    # Calculate sum of geometric means
    sum_scores = sum(
        math.sqrt(food_score ** 2 * service_score)
        for food_score, service_score in zip(food_scores, customer_service_scores)
    )
    
    # Calculate final score using the formula
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i])) * 1/(N * sqrt(125)) * 10
    score = sum_scores * (1 / (N * math.sqrt(125))) * 10
    
    # Format score to ensure at least 3 decimal places
    formatted_score = f"{score:.3f}"
    

    return {restaurant_name: formatted_score}


def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    """
    Corrects restaurant names in a given query string by replacing common misspellings
    or informal variations with their proper names.

    Args:
        restaurant_query (str): A string containing a question or query about a restaurant.
            Examples:
            - "How good is mcdonalds?"
            - "What would you rate In n out?"
            - "Tell me about Chick fil a"

    Returns:
        str: The original query with the restaurant name corrected if a match is found.
            If no restaurant name needs correction, returns the original query unchanged.
            
    Examples:
        >>> get_data_fetch_agent_prompt("How good is mcdonalds?")
        "How good is McDonald's?"
        >>> get_data_fetch_agent_prompt("What would you rate In n out?")
        "What would you rate In-N-Out?"
        >>> get_data_fetch_agent_prompt("Tell me about some random restaurant")
        "Tell me about some random restaurant"
    """
    restaurant_mappings = {
        'mcdonalds': "McDonald's",
        'mcdonald': "McDonald's",
        'mc donalds': "McDonald's",
        'subway': 'Subway',
        'in n out': 'In-N-Out',
        'innout': 'In-N-Out',
        'burger king': 'Burger King',
        'burgerking': 'Burger King',
        'kfc': 'KFC',
        'kentucky fried chicken': 'KFC',
        'wendys': "Wendy's",
        'taco bell': 'Taco Bell',
        'tacobell': 'Taco Bell',
        'chipotle': 'Chipotle',
        'five guys': 'Five Guys',
        'fiveguys': 'Five Guys',
        'popeyes': "Popeyes",
        'chick fil a': 'Chick-fil-A',
        'chickfila': 'Chick-fil-A',
    }
    
    
    query_lower = restaurant_query.lower()
    
    for incorrect, correct in restaurant_mappings.items():
        if incorrect in query_lower:
            return restaurant_query.lower().replace(incorrect, correct)
    
    return restaurant_query




# Do not modify the signature of the "main" function.
def main(user_query: str):
    entrypoint_agent_system_message = """
        You are a helpful assistant for a restaurant review analysis system.         
        """ 
    
    # example LLM config for the entrypoint agent
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    

    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent(
        "entrypoint_agent", 
        system_message=entrypoint_agent_system_message, 
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    

    data_fetch_agent = ConversableAgent(
        "data_fetch_agent", 
        system_message="""
            Your job is to fetch the reviews for the restaurant. 
            
            Write the result as below:
            
            Restaurant name: `the name of the restaurant`
            Reviews: `a list of reviews for the restaurant`

            """, 
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    review_analysis_agent = ConversableAgent(
        "review_analysis_agent", 
        system_message="""
            Your job is to extract scores (food_score and customer_service_score) of restaurant reviews.

            You should extract these two scores by looking for keywords in the review. 
            Each review has keyword adjectives that correspond to the score that the restaurant should get for its food_score and customer_service_score. 
            Here are the keywords the agent should look out for:

            Score 1/5 has one of these adjectives: awful, horrible, or disgusting.
            Score 2/5 has one of these adjectives: bad, unpleasant, or offensive.
            Score 3/5 has one of these adjectives: average, uninspiring, or forgettable.
            Score 4/5 has one of these adjectives: good, enjoyable, or satisfying.
            Score 5/5 has one of these adjectives: awesome, incredible, or amazing.
            

            Write the result as below:

            Restaurant name: `the name of the restaurant`
            Food scores: `a list of integer food scores`
            Customer service scores: `a list of integer customer service scores`
            """, 
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    scoring_agent = ConversableAgent(
        "scoring_agent", 
        system_message="""
            Your job is to calculate the overall score.

            Write the result as below:

            'The `name of the restaurant` restaurant overall score is: `the overall score`'
            """,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )                   


    # TOOLS 
    data_fetch_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    #review_analysis_agent.register_for_llm(name="extract_restaurant_scores", description="Extract scores from a restaurant reviews.")(extract_restaurant_scores)
    scoring_agent.register_for_llm(name="calculate_overall_score", description="Calculates the overall score for the restaurant.")(calculate_overall_score)
    
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)    
    #entrypoint_agent.register_for_execution(name="extract_restaurant_scores")(extract_restaurant_scores)
    entrypoint_agent.register_for_execution(name="calculate_overall_score")(calculate_overall_score)

  
    
    result = entrypoint_agent.initiate_chats(
        [
            {
            "recipient": data_fetch_agent,
            "message": get_data_fetch_agent_prompt(user_query), # Initial message
            "max_turns": 2,
            "summary_method": "last_msg",
            },
            {
            "recipient": review_analysis_agent,
            "message": "Extract the scores for the restaurant reviews.",  
            "max_turns": 1,
            "summary_method": "last_msg",
            },
            {
            "recipient": scoring_agent,
            "message": "Calculate the overall score.", 
            "max_turns": 2,
            "summary_method": "last_msg",
            },
        ]
    )
    

# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
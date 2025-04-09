import os
import json
import logging
from typing import Union
import httpx
import inspect
from openai import OpenAI, APIError, RateLimitError
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Debug OpenAI module
logging.info(f"OpenAI module version: {OpenAI.__module__}")
logging.info(f"OpenAI class signature: {inspect.signature(OpenAI.__init__)}")

def analyze_psychographics(post_text: str) -> Union[str, None]:
    """
    Analyzes a given text (e.g., Reddit post) to extract psychographic insights using OpenAI.

    Args:
        post_text: The text content to analyze.

    Returns:
        A JSON string containing the analysis results (emotion, core_belief, etc.),
        or None if the analysis fails or the client is not initialized.
    """
    if not post_text or not isinstance(post_text, str) or len(post_text.strip()) == 0:
        logging.warning("Input text is empty or invalid. Skipping analysis.")
        return None

    # Try to get API key from environment or secrets
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.openai.api_key
            except (AttributeError, KeyError):
                logging.error("OpenAI API key not found in environment or secrets")
                return None
        
        # Using a custom httpx client without proxies
        http_client = httpx.Client(
            base_url="https://api.openai.com",
            follow_redirects=True,
            timeout=60.0
        )
        
        # Create a new client with our custom http_client
        client = OpenAI(
            api_key=api_key,
            http_client=http_client
        )
        
        logging.info("Created custom OpenAI client without proxies")
    except Exception as e:
        logging.error(f"Failed to create OpenAI client: {e}")
        return None

    system_prompt = "You are a market behavior analyst."
    user_prompt = f"""
Read the following Reddit post and return ONLY a valid JSON object with the following keys:
- "emotion": Primary emotion (e.g. frustration, anger, hope)
- "core_belief": Core belief about the problem or life
- "attempted_solution": What solutions has this person tried (tools, habits, products)? List them comma-separated or as 'None'.
- "perceived_blocker": What do they think is blocking them? List them comma-separated or as 'None'.
- "external_forces": Do they mention any external forces (companies, government, etc.)? List them comma-separated or as 'None'.
- "quote": What's a direct quote that captures the feeling? If no suitable quote, use 'None'.

Reddit Post:
---
{post_text}
---

Ensure the output is ONLY the JSON object, without any introductory text or explanation. Example: {{"emotion": "frustration", "core_belief": "...", ...}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or consider gpt-4-turbo for potentially better results
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5, # Adjust temperature for creativity vs. consistency
            max_tokens=300, # Adjust based on expected output length
            response_format={ "type": "json_object" } # Request JSON output directly if using compatible models
        )

        analysis_content = response.choices[0].message.content
        logging.info(f"Successfully received psychographic analysis for post snippet: {post_text[:50]}...")

        # Validate if the response is valid JSON
        try:
            json.loads(analysis_content)
            return analysis_content
        except json.JSONDecodeError:
            logging.error(f"OpenAI response is not valid JSON: {analysis_content}")
            # Attempt to extract JSON if wrapped in ```json ... ```
            if "```json" in analysis_content:
                try:
                    extracted_json = analysis_content.split("```json")[1].split("```")[0].strip()
                    json.loads(extracted_json) # Test if valid
                    logging.info("Successfully extracted JSON from formatted response.")
                    return extracted_json
                except (IndexError, json.JSONDecodeError):
                     logging.error("Failed to extract valid JSON from formatted response.")
                     return None # Fallback if extraction fails
            return None # Return None if not valid JSON and extraction failed


    except RateLimitError:
        logging.error("OpenAI API rate limit exceeded. Please check your plan and usage.")
        return None
    except APIError as e:
        logging.error(f"An API error occurred: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during psychographic analysis: {e}")
        return None

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # Ensure OPENAI_API_KEY is set as an environment variable for this test
    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set the OPENAI_API_KEY environment variable to run this test.")
    else:
        test_post = """
        I've been freelancing for 5 years now and I'm completely burnt out.
        I feel like I'm on a hamster wheel, constantly chasing clients and deadlines.
        I've tried time management techniques, meditation, even took a vacation last month, but nothing helps.
        It feels like the only way to succeed is to work 12 hours a day, which is just not sustainable.
        My friends in regular jobs don't get it. They think I have all the freedom, but I feel trapped.
        I blame the 'hustle culture' everyone seems to glorify. Is there any way out?
        I feel like I'm constantly failing even though I'm doing everything I can.
        """
        analysis_result = analyze_psychographics(test_post)
        if analysis_result:
            print("Analysis Result:")
            # Pretty print the JSON
            parsed_json = json.loads(analysis_result)
            print(json.dumps(parsed_json, indent=2))
        else:
            print("Failed to get analysis result.") 
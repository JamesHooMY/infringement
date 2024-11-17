from pyexpat import model
from turtle import st
import openai
import json
import uuid
import logging
import re
from datetime import datetime
from app.core.config import settings  # Import your settings
from app.models import Company, Patent, InfringementAnalysis

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PatentInfringementAnalyzer:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key

        base_url = str(settings.OPENAI_BASE_URL)
        if base_url:
            openai.base_url = base_url

        # Set default headers if specified in settings
        openai.default_headers = {
            "x-foo": "true" if settings.OPENAI_DEFAULT_HEADER_X_FOO else "false"
        }

    def analyze_infringement(
        self, company: Company, patent: Patent
    ) -> InfringementAnalysis:
        # Create a unique analysis ID and current analysis date
        analysis_id = str(uuid.uuid4())
        analysis_date = datetime.now().isoformat()

        # Format the input message for OpenAI
        input_message = f"""
            You are an expert in patent analysis. Your task is to analyze the following patent and company product details and provide a response in the JSON format specified below:

            Expected JSON format:
            {{
            "analysis_id": "{analysis_id}",
            "patent_id": "{patent.publication_number}",
            "company_name": "{company.name}",
            "analysis_date": "{analysis_date}",
            "top_infringing_products": [
                {{
                    "product_name": "<product_name>",
                    "infringement_likelihood": "<High/Moderate/Low>",
                    "relevant_claims": ["<claim_number_1>", "<claim_number_2>"],
                    "explanation": "<detailed explanation>",
                    "specific_features": [
                        "<feature_1>",
                        "<feature_2>",
                        "<feature_3>"
                    ]
                }}
                // Repeat for each product if applicable
            ],
            "overall_risk_assessment": "<summary_of_overall_risk>"
            }}

            Details for analysis:

            Patent Information:
            - Title: "{patent.title}"
            - Abstract: "{patent.abstract}"
            - Claims:
            {json.dumps(patent.claims, indent=4)}

            Company Information:
            Company "{company.name}" has the following products:
            {json.dumps(company.products, indent=4)}

            Please analyze and identify which of these products potentially infringe on the patent claims. Include detailed explanations and ensure the response follows the JSON format specified above.
        """

        try:
            # logger.debug("Calling OpenAI API with input message: %s", input_message)
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                # model="gpt-4o-mini",
                messages=[
                    # {
                    #     "role": "system",
                    #     "content": "You are an expert patent analyst specializing in evaluating and assessing patent infringement scenarios. Your responses must be in a structured JSON format for machine parsing and use.",
                    # },
                    {
                        "role": "system",
                        "content": "You are a professional patent genius with expertise in analyzing and evaluating patent infringement scenarios.",
                    },
                    {
                        "role": "user",
                        "content": input_message,
                    },
                ],
            )

            # complete_response = ""
            # for chunk in response:
            #     complete_response += chunk["choices"][0]["delta"].get("content", "")
            # logger.debug("Complete response from OpenAI: %s", complete_response)

            # Extract the response from OpenAI
            if response.choices and response.choices[0].message:
                response_messages = response.choices[0].message.content
                if isinstance(response_messages, str):
                    response_messages = response_messages.strip()
                else:
                    logger.error(
                        "Received an unexpected response structure from OpenAI. Response content: %s",
                        response_messages,
                    )
                    raise ValueError("OpenAI returned an unexpected response format.")

                logger.debug("Response from OpenAI: %s", response_messages)

                # Extract the JSON content from the response by slicing the string twice, not recommended
                # response_messages = response_messages[response_messages.find("{") :]
                # response_messages = response_messages[: response_messages.rfind("}") + 1]

                # Optimize
                response_messages = response_messages[
                    response_messages.find("{") : response_messages.rfind("}") + 1
                ]

                # Extract the JSON content using a regular expression
                match = re.search(r"\{.*\}", response_messages, re.DOTALL)
                if match:
                    response_messages = match.group()
                else:
                    raise ValueError("No JSON content found in response_messages.")

                try:
                    # logger.debug("Parsing response as JSON: %s", response_messages)
                    response_dict = json.loads(response_messages)
                    # logger.debug("Parsed JSON response: %s", response_dict)
                except json.JSONDecodeError:
                    logger.error(
                        "Failed to parse response as JSON. Response content: %s",
                        response_messages,
                    )
                    raise ValueError("Invalid JSON response from OpenAI.")
            else:
                logger.error("Received an unexpected response structure from OpenAI.")
                raise ValueError("OpenAI returned an unexpected response format.")

            # Create InfringementAnalysis object
            analysis_response = InfringementAnalysis(
                id=uuid.UUID(analysis_id),
                patent_id=patent.publication_number,
                company_name=company.name,
                analysis_date=datetime.fromisoformat(analysis_date),
                top_infringing_products=response_dict.get(
                    "top_infringing_products", []
                ),
                overall_risk_assessment=response_dict.get(
                    "overall_risk_assessment", ""
                ),
            )

            return analysis_response

        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)
            # return default response
            response_raise = InfringementAnalysis(
                id=uuid.UUID(analysis_id),
                patent_id=patent.publication_number,
                company_name=company.name,
                analysis_date=datetime.fromisoformat(analysis_date),
                top_infringing_products=[],
                overall_risk_assessment="An error occurred during the analysis.",
            )
            return response_raise


# Example usage (for testing purposes):
if __name__ == "__main__":
    analyzer = PatentInfringementAnalyzer()

    # Example company and patent information (these would normally come from your database or another source)
    company_info = {
        "name": "Walmart Inc.",
        "products": [
            {
                "name": "Walmart Shopping App",
                "description": "Mobile application with integrated shopping list and advertisement features",
            },
            {
                "name": "Walmart+",
                "description": "Membership program with smart shopping list synchronization",
            },
        ],
    }

    patent_info = {
        "publication_number": "US-RE49889-E1",
        "title": "Systems and methods for generating and/or modifying electronic shopping lists from digital advertisements",
        "abstract": "Systems and methods are provided for generating and/or modifying a shopping list from a mobile advertisement...",
        "claims": [
            {
                "num": "00001",
                "text": "1. An improved computer-implemented method for generating a digital shopping list, ...",
            },
            {
                "num": "00002",
                "text": "2. The method according to claim 1 further comprising the mobile device transmitting ...",
            },
        ],
    }

    result = analyzer.analyze_infringement(
        company=Company(**company_info), patent=Patent(**patent_info)
    )
    print(result)

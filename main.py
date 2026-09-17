import os
import random
import uuid

from dotenv import load_dotenv
from langfuse import get_client, propagate_attributes
from langfuse.openai import OpenAI

from output import print_recommendation


ALL_FLAVOURS = [
    "Vanilla Bean",
    "Dark Chocolate",
    "Strawberry",
    "Salted Caramel",
    "Mint Chocolate Chip",
    "Cookies and Cream",
    "Pistachio",
    "Mango Sorbet",
    "Coffee",
    "Cookie Dough",
]

DEFAULT_FLAVOUR_PROMPT = """You are an ice-cream expert.
Recommend exactly one flavour from this list: {{flavours}}.
Briefly explain why it suits the customer's request.
Never recommend a flavour that is not in the list."""


def generate_customer_request(client: OpenAI) -> str:
    """Generate a realistic request from an ice-cream customer."""
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=(
            "Generate one realistic ice-cream request written by a customer. "
            "Vary the mood, cravings, preferences, and phrasing. Return only "
            "the request, with no extra commentary."
        ),
        input="Generate one random ice-cream request.",
    )
    return response.output_text.strip()


def main() -> None:
    load_dotenv()

    required_variables = (
        "OPENAI_API_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_PUBLIC_KEY",
    )
    missing_variables = [name for name in required_variables if not os.getenv(name)]
    if missing_variables:
        raise SystemExit(
            "Configuration error: missing "
            f"{', '.join(missing_variables)}. Add them to the project's .env file."
        )

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    langfuse = get_client()
    available_flavours = random.sample(ALL_FLAVOURS, 5)

    # Group the two model calls into one trace and make the run filterable by
    # session and user in Langfuse.
    with propagate_attributes(session_id=str(uuid.uuid4()), user_id="demo-user"):
        with langfuse.start_as_current_observation(
            name="ice-cream-recommendation"
        ):
            customer_request = generate_customer_request(client)

            # Prefer the production prompt managed in Langfuse. The local
            # fallback keeps the demo usable before that prompt is created.
            flavour_prompt = langfuse.get_prompt(
                "ice-cream-flavour-prompt",
                fallback=DEFAULT_FLAVOUR_PROMPT,
            )
            instructions = flavour_prompt.compile(
                flavours=", ".join(available_flavours)
            )

            response = client.responses.create(  # type: ignore[call-overload]
                model="gpt-4o-mini",
                instructions=instructions,
                input=customer_request,
                langfuse_prompt=flavour_prompt,
            )

    print_recommendation(
        customer_request,
        available_flavours,
        response.output_text,
    )


if __name__ == "__main__":
    main()

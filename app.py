#working well

import streamlit as st
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
import cohere  # Cohere SDK for text generation

# Pydantic models for input validation
class SMEProfile(BaseModel):
    name: str = Field(..., description="Name of the SME or content creator.")
    industry: str = Field(..., description="Industry or niche of the SME.")
    tone: str = Field(..., description="Tone of the content (e.g., professional, casual, inspiring).")
    target_audience: str = Field(..., description="Description of the target audience.")

class ContentRequest(BaseModel):
    prompt: str = Field(..., description="User-defined content prompt.")
    trending_topic: Optional[str] = Field(None, description="Optional trending topic to incorporate into content.")
    profile: SMEProfile

# Helper function to call Cohere API for LinkedIn content generation
def generate_content_with_cohere(prompt: str, tone: str, audience: str, trending_topic: Optional[str] = None):
    cohere_api_key = "Xqg33zlVwRzYirWPb2jZiakjuLsY98tNQGrOgKHV"  # Updated API key

    # Initialize the Cohere client
    cohere_client = cohere.Client(cohere_api_key)

    # Prepare the prompt
    full_prompt = f"Generate a LinkedIn post with the following details:\n\n" \
                  f"Prompt: {prompt}\n" \
                  f"Tone: {tone}\n" \
                  f"Audience: {audience}\n" \
                  f"Include **bold text** only for headers (e.g., **Product Launch**), relevant emojis (like 🎯, 🚀), and symbols where appropriate.\n" \
                  f"Make it concise, engaging, and provide a clear call to action (CTA)."

    if trending_topic:
        full_prompt += f"\nTrending Topic: {trending_topic}"

    # Request content generation from Cohere with the correct model ID
    response = cohere_client.generate(
        model="command-xlarge",  # Model name for content generation
        prompt=full_prompt,
        max_tokens=150,  # Limit the number of tokens
        temperature=0.7  # Controls creativity
    )

    return response.generations[0].text.strip()


# Function to format headers as bold and keep content regular
def format_bold_headers(content):
    # Split content by lines
    lines = content.split('\n')

    formatted_content = []

    for line in lines:
        # Apply bold formatting for lines that appear as headers (you can customize the condition)
        if line.strip().endswith(":") or line.isupper():
            formatted_content.append(f"<b>{line}</b>")  # Bold the header
        else:
            formatted_content.append(line)  # Keep regular text

    return "\n".join(formatted_content)


# Function to add hashtags at the end of the post
def add_hashtags(content):
    hashtags = "#Innovation #Growth #BusinessSuccess #Marketing #BrandAwareness #ContentCreation"
    return f"{content}\n\n{hashtags}"


# Streamlit UI for generating content
def main():
    st.title("LinkedIn Content Generator")

    with st.form("content_form"):
        # SME Profile Inputs
        st.header("Input SME Profile")
        name = st.text_input("Name of SME or Content Creator")
        industry = st.text_input("Industry or Niche")
        tone = st.selectbox("Tone of Content", ["Professional", "Casual", "Inspiring", "Empathetic", "Supportive"])
        target_audience = st.text_input("Target Audience Description")

        # Content Details
        st.header("Content Details")
        prompt = st.text_area("Content Prompt", "Generate content for a new business idea or product.")
        trending_topic = st.text_input("Trending Topic (Optional)", "#BusinessGrowth")

        submit_button = st.form_submit_button("Generate Content")

        if submit_button:
            try:
                # Validate input with Pydantic
                profile = SMEProfile(
                    name=name,
                    industry=industry,
                    tone=tone,
                    target_audience=target_audience
                )
                request = ContentRequest(
                    prompt=prompt,
                    trending_topic=trending_topic,
                    profile=profile
                )

                # Generate content using Cohere API
                content = generate_content_with_cohere(
                    prompt=request.prompt,
                    tone=request.profile.tone,
                    audience=request.profile.target_audience,
                    trending_topic=request.trending_topic
                )

                # Format headers as bold, keeping other content regular
                content_with_bold_headers = format_bold_headers(content)

                # Add hashtags to the content
                content_with_hashtags = add_hashtags(content_with_bold_headers)

                # Display content with bold headers and hashtags in HTML format
                st.markdown(content_with_hashtags, unsafe_allow_html=True)

            except ValidationError as e:
                st.error("Input validation failed. Please correct the errors below.")
                st.json(e.json())

if __name__ == "__main__":
    main()

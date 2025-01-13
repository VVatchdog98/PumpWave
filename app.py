import streamlit as st
import openai
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# OpenAI API Key
openai.api_key = "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"

# Helper function to calculate growth potential
def calculate_growth_potential(mc, fdv, locked, unlocked):
    try:
        locked_percentage = (locked / (locked + unlocked)) * 100
        if mc < 10_000_000 and locked_percentage > 50:
            return "Bullish - Low market cap and high locked supply may indicate future growth potential."
        elif fdv > mc * 3 and locked_percentage < 30:
            return "Bearish - High FDV compared to market cap and low locked supply could mean overvaluation."
        else:
            return "Neutral - The metrics do not strongly indicate bullish or bearish potential."
    except ZeroDivisionError:
        return "Insufficient data to estimate growth potential."

# AI Function for User Interaction
def analyze_with_ai(user_question, context_data):
    prompt = f"""
    You are a crypto analysis assistant. The user has asked: {user_question}.
    Here is the token data:
    {context_data}

    Respond in simple terms with insights about growth potential, risks, and whether it's a good buy.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# App title
st.title("AI-Powered Solana Coin Analyzer")

# Input field for the user to enter the token pair address or coin ID
token_pair_address = st.text_input("Enter Token Pair Address (Solana):", placeholder="e.g., Token_Pair_Address")
coin_id = st.text_input("Enter Coin ID (CoinGecko):", placeholder="e.g., solana")
user_question = st.text_input("Ask your question about the token:", placeholder="e.g., Is this a good buy?")

# Button to fetch and analyze data
if st.button("Analyze Token"):
    if token_pair_address and coin_id:
        # Fetch data from DEXscreener API
        url = f"https://api.dexscreener.io/latest/dex/pairs/solana/{token_pair_address}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            pair_data = data.get("pair", {})
            if pair_data:
                st.subheader("Token Metrics")
                st.write(f"**Symbol:** {pair_data['baseToken']['symbol']}")
                st.write(f"**Price (USD):** ${pair_data['priceUsd']}")
                st.write(f"**Market Cap (Liquidity USD):** ${pair_data['liquidity']['usd']:,}")
                st.write(f"**Fully Diluted Valuation (FDV):** ${pair_data['fdv']:,}")

                # Example locked and unlocked supply data
                locked_coins = 40_000_000  # Replace with actual API data
                unlocked_coins = 60_000_000  # Replace with actual API data

                # Calculate growth potential
                growth_potential = calculate_growth_potential(
                    mc=pair_data['liquidity']['usd'],
                    fdv=pair_data['fdv'],
                    locked=locked_coins,
                    unlocked=unlocked_coins
                )
                st.subheader("Growth Potential Estimation")
                st.write(growth_potential)

                # AI-Powered Question Analysis
                if user_question:
                    context_data = f"""
                    - Market Cap: {pair_data['liquidity']['usd']}
                    - FDV: {pair_data['fdv']}
                    - Locked Supply: {locked_coins}
                    - Unlocked Supply: {unlocked_coins}
                    - Growth Potential: {growth_potential}
                    """
                    ai_response = analyze_with_ai(user_question, context_data)
                    st.subheader("AI Response")
                    st.write(ai_response)
            else:
                st.error("No data found for this token pair.")
        else:
            st.error(f"Failed to fetch data. Status code: {response.status_code}")
    else:
        st.error("Please enter a valid token pair address or coin ID.")

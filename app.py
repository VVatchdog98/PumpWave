import streamlit as st
import requests


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


# Helper function to explain tokenomics
def explain_tokenomics(locked, unlocked):
    locked_percentage = (locked / (locked + unlocked)) * 100 if (locked + unlocked) > 0 else 0
    explanation = f"""
    - Total Supply: {locked + unlocked}
    - Circulating Supply: {unlocked}
    - Locked Supply: {locked} ({locked_percentage:.2f}% of total)
    """
    if locked_percentage > 50:
        explanation += "\n**Bullish**: A high percentage of locked supply can reduce immediate sell pressure."
    elif locked_percentage < 30:
        explanation += "\n**Bearish**: A low locked supply might indicate potential sell-offs as most tokens are unlocked."
    else:
        explanation += "\n**Neutral**: Locked and unlocked supply are balanced, suggesting steady market conditions."
    return explanation


# App title
st.title("Solana Coin Growth Potential Analyzer")

# Input field for the user to enter the token pair address
token_pair_address = st.text_input("Enter Token Pair Address (Solana):", placeholder="e.g., Token_Pair_Address")

# Button to fetch and analyze data
if st.button("Analyze Token"):
    if token_pair_address:
        # Fetch data from DEXscreener API
        url = f"https://api.dexscreener.io/latest/dex/pairs/solana/{token_pair_address}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Extract relevant metrics
            pair_data = data.get("pair", {})
            if pair_data:
                st.subheader("Token Metrics")
                st.write(f"**Symbol:** {pair_data['baseToken']['symbol']}")
                st.write(f"**Name:** {pair_data['baseToken']['name']}")
                st.write(f"**Price (USD):** ${pair_data['priceUsd']}")
                st.write(f"**Market Cap (Liquidity USD):** ${pair_data['liquidity']['usd']:,}")
                st.write(f"**Fully Diluted Valuation (FDV):** ${pair_data['fdv']:,}")

                # Example data for locked and unlocked coins (replace with API call or additional logic)
                locked_coins = 40_000_000  # Replace with actual API data
                unlocked_coins = 60_000_000  # Replace with actual API data

                # Display tokenomics 101
                st.subheader("Tokenomics 101")
                tokenomics_explanation = explain_tokenomics(locked_coins, unlocked_coins)
                st.write(tokenomics_explanation)

                # Calculate growth potential
                growth_potential = calculate_growth_potential(
                    mc=pair_data['liquidity']['usd'],
                    fdv=pair_data['fdv'],
                    locked=locked_coins,
                    unlocked=unlocked_coins
                )
                st.subheader("Growth Potential Estimation")
                st.write(growth_potential)
            else:
                st.error("No data found for this token pair.")
        else:
            st.error(f"Failed to fetch data. Status code: {response.status_code}")
    else:
        st.error("Please enter a valid token pair address.")

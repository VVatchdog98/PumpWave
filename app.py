from flask import Flask, request, render_template, jsonify
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

app = Flask(__name__)

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
        explanation += "\n**Bullish**: High locked supply reduces immediate sell pressure."
    elif locked_percentage < 30:
        explanation += "\n**Bearish**: Low locked supply increases sell-off risk."
    else:
        explanation += "\n**Neutral**: Balanced supply suggests steady conditions."
    return explanation

# API Route for Analyzing Token
@app.route('/analyze', methods=['POST'])
def analyze_token():
    data = request.json
    token_address = data.get("token_address")
    coin_id = data.get("coin_id")

    # Fetch data from DEXscreener API
    url = f"https://api.dexscreener.io/latest/dex/pairs/solana/{token_address}"
    response = requests.get(url)

    if response.status_code == 200:
        pair_data = response.json().get("pair", {})
        if not pair_data:
            return jsonify({"error": "No data found for the token pair"}), 404

        # Example locked/unlocked coins (replace with actual API logic)
        locked_coins = 40_000_000
        unlocked_coins = 60_000_000

        # Metrics
        growth_potential = calculate_growth_potential(
            mc=pair_data['liquidity']['usd'],
            fdv=pair_data['fdv'],
            locked=locked_coins,
            unlocked=unlocked_coins
        )
        tokenomics = explain_tokenomics(locked_coins, unlocked_coins)

        # Sentiment Analysis
        sentiment_text = "The Solana community is optimistic."  # Replace with actual data
        analyzer = SentimentIntensityAnalyzer()
        sentiment_score = analyzer.polarity_scores(sentiment_text)

        return jsonify({
            "symbol": pair_data['baseToken']['symbol'],
            "name": pair_data['baseToken']['name'],
            "price_usd": pair_data['priceUsd'],
            "liquidity_usd": pair_data['liquidity']['usd'],
            "fdv": pair_data['fdv'],
            "growth_potential": growth_potential,
            "tokenomics": tokenomics,
            "sentiment": sentiment_score
        })
    else:
        return jsonify({"error": "Failed to fetch data from DEXscreener"}), 500

# Home route for UI
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

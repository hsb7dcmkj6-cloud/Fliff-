# Fliff $1 → $50 scanner website

This is a **starter Streamlit website**, not a deployed live site. It calls PropLine on the server and filters single Fliff outcomes for $50+ total payout on a $1 stake. It never places bets.

## Deploy from an iPhone

1. Create a private GitHub repository and upload `app.py` and `requirements.txt` (do **not** upload any API key).
2. Go to https://share.streamlit.io/ and deploy the repo with `app.py` as the entry point.
3. In the app's settings, open **Secrets** and enter `PROPLINE_API_KEY = "YOUR_NEW_KEY"` (replace placeholder locally). Save/reboot.
4. Open the resulting Streamlit URL in Safari. Use **Scan live odds**.

Because a key was posted in chat, rotate/revoke it before use. Never add secrets to repository files or a URL.

## Important limitations

- PropLine's current published bookmaker listing does **not** establish Fliff coverage. The app checks actual response bookmaker keys and explicitly warns if `fliff` is absent.
- This version scans a limited number of events per sport to conserve the free daily API quota. Events and odds responses may be incomplete or require explicit market keys; see https://prop-line.com/docs.
- This only filters **single selections** by payout, not correlated parlays.
- It does **not** assign positive expected value: doing so requires independent probability estimates, properly matched markets, and validation.
- Live prices can move, and a quoted payout is not guaranteed to be available on Fliff.

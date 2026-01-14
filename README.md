# DOIMiner 🔬

by **Raj Singh** (GR-MMG Lab, IIT Bombay)

DOIMiner is a tool designed to easily fetch DOIs and metadata for scientific papers using the Crossref API, filtering by specific keywords relevant to your research.

## Features
- **Smart Keyword Matching**: Handles plurals and case sensitivity automatically.
- **Web GUI**: User-friendly interface built with [Streamlit](https://streamlit.io).
- **Excel Export**: Download your results directly as an `.xlsx` file.

## How to Run Locally

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deploying to Streamlit Community Cloud (Free)
1. Fork this repository or push it to your own GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Click "New App".
4. Select your repository (`github_doiminer`).
5. Set "Main file path" to `app.py`.
6. Click **Deploy!**

## License
© 2026 GR-MMG Lab, Department of Chemistry, IIT Bombay

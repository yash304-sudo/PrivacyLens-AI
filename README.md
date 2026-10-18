# PrivacyLens AI

A small Streamlit prototype that detects selected sensitive patterns in text, masks them, and displays a transparent heuristic privacy-risk score.

## Features
- Detects email addresses, phone-like number strings, and reference IDs such as `CUST-482913`
- Replaces detected values with placeholders
- Shows detection counts, a demo risk score, and a breakdown table
- Allows downloading masked text
- Includes a sample input for demonstrations

## Requirements
- Python 3.10+
- Streamlit
- Pandas

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Important limitations
- This is a prototype using regular expressions, not a trained AI model.
- It may miss sensitive data or produce false positives.
- The risk score is a demo heuristic, not a probability or formal security assessment.
- Do not paste real confidential or highly sensitive information into a demo.
- The app does not claim IBM Z/LinuxONE deployment; that requires a separate test on an authorized environment.

## Suggested architecture
Text input -> pattern-based detector -> masking layer -> risk-score heuristic -> review and download.

## Demo script
1. Launch the app and use the sample text.
2. Click **Scan and mask sensitive data**.
3. Show the number of detections and risk score.
4. Compare the original and masked text.
5. Download the masked result.
6. Explain limitations and how enterprise policy / IBM LinuxONE deployment could be explored next.

## Responsible use
Use synthetic demonstration data only. Review the masked output before sharing it with another system.

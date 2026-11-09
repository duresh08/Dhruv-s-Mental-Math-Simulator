# Dhruv's MathBot

**Live:** https://duresh08.github.io/Dhruv-s-Mental-Math-Simulator/

Mental math practice for trading and quant interviews. Questions are read aloud, you type the answer, and you get +1 for a correct answer and −1 for a wrong one.

- Addition, subtraction and multiplication, in any combination
- Adjustable ranges (defaults: 2–100 for addition and subtraction, (2–12) × (2–100) for multiplication)
- Audio mode (questions spoken by your browser) or visual mode
- Keyboard first: Enter to submit, R to replay, S to skip

## Run it

It's a static page with no build step and no dependencies. Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
```

Then go to http://localhost:8000.

It's hosted on GitHub Pages from the `main` branch, so pushing to `main` updates the live site.

The original 2022 Streamlit version is still in `mathbot.py`.

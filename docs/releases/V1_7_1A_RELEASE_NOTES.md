# TEAD AI V1.7.1a — Guided Demo Header Clearance

**Hotfix scope:** Guided Operations Demo's first eyebrow label was partially cropped at the top in a live desktop screenshot after Streamlit reboot.

- Add 12px of internal top clearance and an explicit line height to the first Guided Demo eyebrow text.
- Target only the Guided Operations Demo via the existing `.tread-guided-marker` page selector. No other page's spacing is modified.
- Keep the 1.7.1 orchestration, progress timers, four RCA cards, replay controls and offline recorded evidence untouched.
- This is a CSS-only layout correction; live Streamlit acceptance must be repeated after deployment.

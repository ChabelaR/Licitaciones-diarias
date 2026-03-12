# Neix · Generador de Licitaciones

## Estructura del proyecto

```
neix-licitacion-app/
├── app.py              # App principal Streamlit
├── requirements.txt    # Dependencias Python
├── packages.txt        # Dependencias del sistema Linux
├── setup.sh            # Instala Chromium para Playwright
├── .streamlit/
│   └── config.toml     # Config headless
└── README.md
```

## Deploy en Streamlit Cloud

1. Subí esta carpeta a un repo de GitHub
2. En [share.streamlit.io](https://share.streamlit.io) → New app → seleccioná `app.py`
3. En **Advanced settings** → **Custom install command**:
   ```
   pip install -r requirements.txt && playwright install chromium
   ```
4. En **Settings → Secrets**:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Deploy ✅

## Uso local

```bash
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

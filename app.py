import streamlit as st
import anthropic
import base64
import json
import re
import os
import io

st.set_page_config(page_title="Neix · Generador de Licitaciones", page_icon="🔴", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main, .stApp { background-color: #f7f5f3; }
    .neix-header { background:#3d3d3d; padding:28px 36px; border-radius:4px 4px 0 0; display:flex; align-items:center; gap:20px; }
    .neix-title { color:#f7f5f3; font-family:'Playfair Display',serif; font-size:24px; font-weight:700; margin:0; }
    .neix-subtitle { color:#e4e4e4; font-size:11px; letter-spacing:0.12em; text-transform:uppercase; margin:0; }
    .red-bar { height:4px; background:#ab1930; margin-bottom:32px; }
    .step-label { font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.14em; color:#ab1930; margin-bottom:6px; }
    .stButton > button { background-color:#ab1930 !important; color:white !important; border:none !important; font-weight:600 !important; padding:12px 32px !important; border-radius:2px !important; width:100% !important; font-size:13px !important; text-transform:uppercase !important; }
    .status-box { background:#fff; border-left:3px solid #ab1930; padding:12px 16px; font-size:13px; color:#3d3d3d; margin:12px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="neix-header">
    <svg width="44" height="45" viewBox="0 0 405 412" xmlns="http://www.w3.org/2000/svg">
        <path fill="#f7f5f3" d="M133.3,322.71c0,21.7-17.59,39.29-39.29,39.29s-39.29-17.59-39.29-39.29,17.59-39.29,39.29-39.29,39.29,17.59,39.29,39.29"/>
        <polygon fill="#ab1930" points="209.89 130.47 264.37 48.45 329.59 48.45 275.11 130.47 209.89 130.47"/>
        <polygon fill="#f7f5f3" points="274.91 361.83 66.33 48.45 131.55 48.45 340.13 361.83 274.91 361.83"/>
    </svg>
    <p class="neix-title">Generador de Licitaciones</p>
</div>
<div class="red-bar"></div>
""", unsafe_allow_html=True)

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    api_key = st.text_input("API Key de Anthropic", type="password", placeholder="sk-ant-...",
        help="Configurala como secreto ANTHROPIC_API_KEY en Streamlit Cloud.")

st.markdown('<p class="step-label">Subí la imagen</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Imagen", type=["png","jpg","jpeg"], label_visibility="collapsed")
if uploaded_file:
    st.image(uploaded_file, caption="Imagen cargada", width='stretch')

def build_html(data):
    def badge_class(tipo):
        t = tipo.lower()
        if "lecap" in t: return "lecap"
        if "lecer" in t: return "lecer"
        if "boncer" in t: return "boncer"
        if "bonar" in t: return "bonar"
        return ""
    def tasa_html(tasa):
        t = str(tasa).strip()
        if t.upper() in ["N/A",""]: return t
        return f'<span class="tasa-highlight">{t}</span>'
    rows = ""
    for inst in data.get("instrumentos", []):
        emision = inst.get("emision","")
        emision_html = '<span class="tag-nuevo">Nuevo</span>' if emision.lower()=="nuevo" else '<span class="tag-reapertura">Reapertura</span>'
        tipo = inst.get("tipo","")
        rows += f"""<tr>
          <td>{inst.get('especie','')}</td>
          <td><span class="tipo-badge {badge_class(tipo)}">{tipo}</span></td>
          <td>{emision_html}</td>
          <td>{inst.get('precio','')}</td>
          <td>{inst.get('pago_intereses','')}</td>
          <td>{tasa_html(inst.get('tasa',''))}</td>
          <td>{inst.get('vencimiento','')}</td>
        </tr>"""
    fecha_lic = data.get("fecha_licitacion","")
    horario = data.get("horario","")
    fecha_liq = data.get("fecha_liquidacion","")
    fecha_lic_display = f"{fecha_lic} · {horario}" if horario else fecha_lic
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<style>
  @page {{ margin: 0; size: 1100px 10000px; }}
  * {{margin:0;padding:0;box-sizing:border-box;}}
  body {{background:#f7f5f3;font-family:Helvetica,Arial,sans-serif;width:1100px;}}
  .card {{width:1100px;background:#f7f5f3;overflow:hidden;}}
  .header {{background:#3d3d3d;padding:32px 48px;display:flex;justify-content:space-between;align-items:center;}}
  .logo-svg {{width:56px;height:57px;}}
  .header-right {{text-align:right;}}
  .header-title {{font-family:Georgia,serif;font-weight:700;font-size:22px;color:#f7f5f3;letter-spacing:0.02em;}}
  .header-subtitle {{font-size:11px;font-weight:300;color:#e4e4e4;letter-spacing:0.12em;text-transform:uppercase;margin-top:4px;}}
  .accent-bar {{height:4px;background:#ab1930;}}
  .date-section {{background:#fff;padding:24px 48px;display:flex;justify-content:space-between;border-bottom:1px solid #e4e4e4;align-items:center;}}
  .date-item {{display:flex;flex-direction:column;gap:4px;}}
  .date-item.right {{text-align:left;margin-right:120px;}}
  .date-label {{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.14em;color:#ab1930;}}
  .date-value {{font-size:15px;font-weight:400;color:#3d3d3d;}}
  .table-wrapper {{padding:0 0 32px 0;}}
  table {{width:100%;border-collapse:collapse;}}
  thead tr {{background:#3d3d3d;}}
  thead th {{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#f7f5f3;padding:14px 16px;text-align:left;white-space:nowrap;}}
  thead th:first-child {{padding-left:48px;}} thead th:last-child {{padding-right:48px;}}
  tbody tr:nth-child(even) {{background:#fff;}} tbody tr:nth-child(odd) {{background:#f7f5f3;}}
  tbody td {{font-size:11.5px;font-weight:400;color:#3d3d3d;padding:14px 16px;border-bottom:1px solid #e4e4e4;}}
  tbody td:first-child {{padding-left:48px;font-weight:700;color:#ab1930;font-size:12px;letter-spacing:0.04em;}}
  tbody td:last-child {{padding-right:48px;}}
  .tipo-badge {{display:inline-block;background:#3d3d3d;color:#f7f5f3;font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:3px 8px;border-radius:2px;}}
  .tipo-badge.lecap {{background:#ab1930;}} .tipo-badge.lecer {{background:#5a5a5a;}}
  .tipo-badge.boncer {{background:#2c2c2c;}} .tipo-badge.bonar {{background:#7a0e1f;}}
  .tag-nuevo {{display:inline-block;font-size:9px;font-weight:700;color:#ab1930;text-transform:uppercase;letter-spacing:0.1em;border:1.5px solid #ab1930;padding:2px 7px;border-radius:2px;}}
  .tag-reapertura {{display:inline-block;font-size:9px;font-weight:600;color:#3d3d3d;text-transform:uppercase;letter-spacing:0.1em;border:1.5px solid #3d3d3d;padding:2px 7px;border-radius:2px;}}
  .tasa-highlight {{font-weight:700;color:#ab1930;}}
</style></head><body>
<div class="card">
  <div class="header">
    <svg class="logo-svg" viewBox="0 0 405 412" xmlns="http://www.w3.org/2000/svg">
      <path fill="#f7f5f3" d="M133.3,322.71c0,21.7-17.59,39.29-39.29,39.29s-39.29-17.59-39.29-39.29,17.59-39.29,39.29-39.29,39.29,17.59,39.29,39.29"/>
      <polygon fill="#ab1930" points="209.89 130.47 264.37 48.45 329.59 48.45 275.11 130.47 209.89 130.47"/>
      <polygon fill="#f7f5f3" points="274.91 361.83 66.33 48.45 131.55 48.45 340.13 361.83 274.91 361.83"/>
    </svg>
    <div class="header-right">
      <div class="header-title">Licitación del Tesoro</div>
      <div class="header-subtitle">Ministerio de Economía · República Argentina</div>
    </div>
  </div>
  <div class="accent-bar"></div>
  <div class="date-section">
    <div class="date-item"><span class="date-label">Licitación</span><span class="date-value">{fecha_lic_display}</span></div>
    <div class="date-item right"><span class="date-label">Liquidación</span><span class="date-value">{fecha_liq}</span></div>
  </div>
  <div class="table-wrapper">
    <table>
      <thead><tr><th>Especie</th><th>Tipo</th><th>Emisión</th><th>Precio VNO 1.000</th><th>Pago de Intereses</th><th>TEM / Tasa / Margen</th><th>Vencimiento</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</div></body></html>"""

def html_to_png(html_str):
    from weasyprint import HTML
    from pdf2image import convert_from_bytes
    pdf_bytes = HTML(string=html_str).write_pdf()
    images = convert_from_bytes(pdf_bytes, dpi=150)
    buf = io.BytesIO()
    images[0].save(buf, format='PNG')
    return buf.getvalue()

st.markdown('<p class="step-label" style="margin-top:24px">Paso 2 · Generá la imagen con formato Neix</p>', unsafe_allow_html=True)
generate_btn = st.button("⚡ Extraer datos y generar imagen")

if generate_btn:
    if not api_key:
        st.error("Necesitás ingresar una API Key de Anthropic.")
        st.stop()
    if not uploaded_file:
        st.error("Primero subí una imagen.")
        st.stop()

    with st.spinner("🔍 Claude está leyendo la licitación..."):
        img_bytes = uploaded_file.read()
        img_b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
        ext = uploaded_file.name.split(".")[-1].lower()
        media_type = "image/jpeg" if ext in ["jpg","jpeg"] else "image/png"
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            messages=[{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":media_type,"data":img_b64}},
                {"type":"text","text":"""Analizá esta imagen del Ministerio de Economía de Argentina con datos de una licitación del Tesoro.
Devolvé ÚNICAMENTE un JSON válido, sin texto adicional ni markdown:
{
  "fecha_licitacion": "texto completo",
  "horario": "horario o cadena vacía",
  "fecha_liquidacion": "texto completo",
  "instrumentos": [
    {"especie":"","tipo":"","emision":"Nuevo o Reapertura","precio":"","pago_intereses":"","tasa":"","vencimiento":""}
  ]
}"""}
            ]}]
        )
        raw = re.sub(r"```json|```","",response.content[0].text.strip()).strip()

    try:
        data = json.loads(raw)
    except:
        st.error("No se pudo parsear la respuesta. Intentá con otra imagen.")
        with st.expander("Ver respuesta raw"): st.code(raw)
        st.stop()

    st.markdown('<div class="status-box">✅ Datos extraídos correctamente</div>', unsafe_allow_html=True)

    with st.spinner("🎨 Generando imagen con formato Neix..."):
        html_str = build_html(data)
        try:
            png_bytes = html_to_png(html_str)
        except Exception as e:
            st.error(f"Error al renderizar: {e}")
            st.stop()

    st.markdown('<div class="status-box">✅ Imagen generada exitosamente</div>', unsafe_allow_html=True)
    st.image(png_bytes, caption="Vista previa", width='stretch')
    st.download_button("⬇️ Descargar PNG", data=png_bytes, file_name="licitacion_neix.png", mime="image/png")
    with st.expander("Ver datos extraídos por Claude"): st.json(data)

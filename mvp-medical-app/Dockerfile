# ========================================
# Stage 1: Builder
# ========================================
FROM python:3.11-slim as builder

RUN pip install uv
WORKDIR /app
COPY requirements.txt .
RUN uv pip install --no-cache -r requirements.txt

RUN echo "import antspynet; antspynet.utilities.get_pretrained_network('brainExtraction')" > preload_models.py
RUN python preload_models.py

# ========================================
# Stage 2: Final
# ========================================
FROM python:3.11-slim
WORKDIR /app
RUN addgroup --system appuser && adduser --system --no-create-home appuser
USER appuser
COPY --from=builder /app /app
COPY --from=builder /root/.antspynet /home/appuser/.antspynet
COPY --chown=appuser:appuser modules/ ./modules/
COPY --chown=appuser:appuser pages/ ./pages/
COPY --chown=appuser:appuser app.py .
EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV ANTSPYNET_CACHE_DIRECTORY=/home/appuser/.antspynet
CMD ["streamlit", "run", "app.py"]

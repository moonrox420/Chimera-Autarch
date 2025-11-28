FROM python:3.12-slim-bookworm
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
RUN useradd -m chimera && mkdir -p /chimera/data /chimera/tmp && chown chimera:chimera /chimera/tmp
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
USER chimera
EXPOSE 3000 3000
ENTRYPOINT ["python", "DroxAILauncher.py"]


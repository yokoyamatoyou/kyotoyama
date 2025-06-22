# Codex Instructions

This repository implements the medical image analysis MVP described in `Kyotoyama_Medical_Image_Analyzer最新版MVP設計・進捗管理.md`.

## Guidelines for Codex

1. **Follow the plan.** Implement features according to the development plan document. Start with the project skeleton under `mvp-medical-app/` as shown in section 2.1.
2. **Progress log.** Maintain a file named `PROGRESS.md` at the repository root. Update it with a short description of work done each commit.
3. **Testing.** When Python tests are present, run `pytest` before committing. If dependencies are missing or network access prevents installation, document it in the PR message.
4. **Commit messages.** Write concise English commit messages summarizing the change.
5. **Docker and requirements.** Include a multi-stage Dockerfile and `.dockerignore` as described in section 2.2 of the plan. Dependencies must be listed in `requirements.txt`.
6. **Use Python 3.11** for development and container base image.
7. **Local focus.** All instructions should assume local execution. Avoid cloud-only steps unless the plan explicitly requires them.
8. **Model selection.** When the plan references Gemini, substitute **GPT-4.1mini** as the AI model.
9. **Environment variables.** The MVP must read configuration data (e.g. API keys, file paths) from environment variables rather than hard coded values.

Adhere to these instructions for all future work in this repository.

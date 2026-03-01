name: Hourly Retraining Pipeline

on:
  schedule:
    - cron: "0 * * * *"   # Every hour (UTC)
  workflow_dispatch:
  push:
    paths-ignore:
      - "models/**"
      - "logs/**"

jobs:
  retrain:
    runs-on: ubuntu-latest

    permissions:
      contents: write

    steps:
      # -----------------------------------
      # Checkout Repository
      # -----------------------------------
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          persist-credentials: true
          fetch-depth: 0

      # -----------------------------------
      # Setup Python
      # -----------------------------------
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      # -----------------------------------
      # Install Dependencies
      # -----------------------------------
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # -----------------------------------
      # Run Retraining Pipeline
      # -----------------------------------
      - name: Run retraining pipeline
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          python -m src.orchestration.retrain_pipeline

      # -----------------------------------
      # Commit Experiments + Logs + Promotion
      # -----------------------------------
      - name: Commit artifacts safely
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "actions@github.com"

          # Stage experiment runs
          git add models/experiments || true

          # Stage promoted models
          git add models/promoted || true
          git add models/current_model.txt || true

          # Stage logs
          git add logs || true

          # Exit if nothing changed
          if git diff --cached --quiet; then
            echo "No changes to commit."
            exit 0
          fi

          git commit -m "Automated retraining: logged experiment + promotion"
          git push origin main

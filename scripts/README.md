# scripts/

Headless alternatives to the notebook, for when a Colab Enterprise runtime is slow or
unavailable.

`load.sh` reaches the same end state as `notebooks/c1_01_load_explore.ipynb`—the same tables, in
the same dataset, in your project. Use the notebook if you can: it explains what it's doing and
why, and the explanations matter. Use this if you can't.

## Running it

From the **root of the repo**, in Cloud Shell:

```bash
bash scripts/load.sh              # loads the default city
bash scripts/load.sh --list       # show every available city
bash scripts/load.sh --help       # usage
```

Invoke it with `bash` rather than `./scripts/load.sh`. That way it works whether or not the
file's executable bit survived however your copy of this repo was created.

---

# `deploy.sh` (1-Click Cloud Run Deployment)

Automated script to build and deploy the complete dashboard and ADK agent to Google Cloud Run. Anyone on the team can deploy with a single command.

## Running it

From the **root of the repo** in Cloud Shell:

```bash
# Standard 1-click deploy to Cloud Run:
bash scripts/deploy.sh

# Deploy with a custom service name (e.g. personal test deployment):
bash scripts/deploy.sh --service heatshieldai-track1

# Deploy with an AI Studio Gemini API key:
bash scripts/deploy.sh --api-key AIzaSy...

# Show all options and flags:
bash scripts/deploy.sh --help
```

### What it does automatically:
1. Detects your current Google Cloud project ID and region.
2. Enables necessary Google Cloud APIs (`run`, `cloudbuild`, `artifactregistry`, `aiplatform`, `bigquery`).
3. Automatically binds the necessary IAM roles (`roles/aiplatform.user`, `roles/bigquery.user`) to the Cloud Run service account so predictions never fail with 403 errors.
4. Builds the container via Cloud Build and deploys to Cloud Run with public HTTPS access.
5. Prints the permanent live Service URL upon completion.

---

## Safe to run more than once

Every table is fully replaced, never appended to. So if you cancel it halfway through, or you
aren't sure whether it finished, just run it again—the end state is the same either way.

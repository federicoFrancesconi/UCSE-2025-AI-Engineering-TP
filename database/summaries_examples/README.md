# Example PDF Summaries

This directory contains 30 example PDF files with content descriptions for testing the RAG (Retrieval Augmented Generation) functionality of the AI Agent.

## Contents

These PDFs correspond to the content inserted by `insert_sample_data.sql` and include:
- **10 Movies** (Películas): Action, romance, sci-fi, mystery, drama
- **10 TV Series** (Series): Comedy, drama, crime, spy thrillers
- **6 Documentaries** (Documentales): Nature, history, science, culture
- **4 Specials** (Especiales): Concerts, award shows, comedy specials, animation festivals

## Usage

Copy these PDFs to the `summaries/` directory at the project root to enable RAG queries:

```bash
# From project root
mkdir -p summaries
cp database/summaries_examples/*.pdf summaries/
```

Or configure a custom path in `agent/.env`:

```bash
SUMMARIES_DIR=/path/to/your/summaries
```

## PDF Format

Each PDF contains:
- **Title**: Name of the content
- **Synopsis**: 2-3 sentence description
- **Metadata**: Year, Genre, Duration, Country

## RAG Query Examples

Once the PDFs are copied, you can ask:
- "What is Aventuras Galácticas about?"
- "Describe Terror Nocturno"
- "What is the most viewed movie about?" (HYBRID query)

## Generating More PDFs

You can generate additional PDFs using the data generator script:

```bash
python generate_fake_data.py --content 100 --generate-pdfs
```

This will create new PDF summaries matching the content inserted in the database.

# NCMS Fetch Script

This script is responsible for fetching content from a Notion database, transforming it, and generating the necessary files for the "Cutie" PHP framework.

## Role

This script acts as the bridge between Notion (as a headless CMS) and the static site generator. It automates the content pipeline, ensuring that changes made in Notion are reflected on the website.

## Setup

1.  **Install Dependencies:**
    This project uses Python. Install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in this directory by copying the `.env.template`. Fill in the following values:

    *   `NOTION_API_KEY`: Your Notion API integration key.
    *   `NOTION_DATABASE_ID`: The ID of the Notion database you are fetching content from.
    *   `OUTPUT_DIR`: The absolute path to the directory where the generated PHP component files will be saved. This typically corresponds to the `HTML/Component` directory in your "Cutie" framework project.
    *   `PROJECT_DIR`: The absolute path to the root of the website project. This is used for placing project-level files like `firebase.json` and `sitemap.xml` and for running git commands.

## Operation

To run the script and fetch the latest content from Notion, execute the following command:

```bash
python ncms_fetch.py
```

The script will perform the following actions:
1.  Connect to the Notion API using your key.
2.  Query the specified database for pages with a "Status" of "publish".
3.  Process the content of each page, transforming Notion blocks into PHP/HTML.
4.  Generate and place the PHP files into the `OUTPUT_DIR`.
5.  Generate/update configuration files (`ID.tsv`, `Url.tsv`, `firebase.json`, `sitemap.xml`) and place them in the appropriate locations within the `PROJECT_DIR` and `OUTPUT_DIR`.
6.  Commit the changes to the git repository located at `PROJECT_DIR` and push them to the `publish` branch.
7.  If the git push is successful, the script will update the status of the fetched Notion pages to "published".

## Directory Roles

*   **`output/` (defined by `OUTPUT_DIR`):** This is the destination for the dynamically generated PHP files that represent the content from Notion (e.g., individual articles, pages). It also contains generated configuration files like `ID.tsv`, `Url.tsv`, and `sitemap.xml`.
*   **`project/` (defined by `PROJECT_DIR`):** This path points to the root of the target website project. The script places high-level configuration files like `firebase.json` here. It is also the working directory for `git` operations.
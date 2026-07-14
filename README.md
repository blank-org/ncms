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

## Notion Database Properties

Each page in the Notion database requires these properties:

| Property | Type | Description |
|----------|------|-------------|
| `Id` | Title | The URL slug/path (e.g. `world/philosophy/life`) |
| `Status` | Select | Set to `publish` to trigger generation, becomes `published` after |
| `Label` | Rich text | Navigation label text |
| `Title` | Rich text | Page title |
| `JS` | Select | `0` or `1` — loads `page.js` if `1` |
| `Description` | Rich text | Page description for meta tags |

## Block Type Mapping

### Standard Notion Blocks

These Notion blocks map directly to HTML output:

| Notion Block | HTML Output |
|---|---|
| Paragraph | `<p>...</p>` |
| Heading 1 | `<h3>...</h3>` |
| Heading 2 | `<h2>...</h2>` |
| Heading 3 | `<h4>...</h4>` |
| Bulleted list | `<ul class="list-bullet content-list"><li><div>...</div></li></ul>` |
| Numbered list | `<ol class="list-bullet content-list"><li><div>...</div></li></ol>` |
| Table | `<table><tr><td>...</td></tr></table>` |
| Quote | `<blockquote>...</blockquote>` |
| Code | `<pre class='indent-c'><code class='block'>...</code></pre>` |
| Divider | `<div id='content-body-separator' class='center'></div>` |

Consecutive list items of the same type are automatically wrapped in `<ul>` or `<ol>` tags.

### Rich Text Formatting

Inline formatting from Notion is preserved in all text blocks:

| Notion Format | HTML Output |
|---|---|
| **Bold** | `<strong>...</strong>` |
| *Italic* | `<em>...</em>` |
| `Code` | `<code class='inline'>...</code>` |
| ~~Strikethrough~~ | `<s>...</s>` |
| Underline | `<u>...</u>` |
| Link (internal, ujnotes.com) | `<a class="content-link XURL" href='...' data-target='...' data-title='...'>` |
| Link (external) | `<a class="content-link" href="..." target="_blank">` |

### Callout Blocks (Emoji-tagged PHP Components)

Callout blocks with specific emoji icons generate PHP component includes. The callout's text content provides parameters.

#### First-letter high / drop cap — `🔠`

Use this callout only when the author explicitly wants the paragraph's first letter enlarged. Rich-text formatting and links inside the callout are preserved.

**Notion:** Callout with 🔠 icon containing the paragraph text
**Output:**
```html
<p class='first-letter-high'>Author-selected paragraph...</p>
```

Ordinary Notion paragraphs generate plain `<p>` elements without this class. During website-to-Notion upload, only paragraphs already carrying `class='first-letter-high'` become 🔠 callouts.

#### Cover Image — `🖼️`

Generates the cover image component. The callout text is the image alt text.

**Notion:** Callout with 🖼️ icon, text: `A sculpture of a man thinking deeply`
**Output:**
```php
<?php $alt='A sculpture of a man thinking deeply'; require('../HTML/Fragment/Component_cover.php') ?>
<h2 class='center'><?php echo $desc; ?></h2>
```

#### Content Image — `🏞️`

Generates an inline content image. Text format: `img_title|ext|alt|center`

**Notion:** Callout with 🏞️ icon, text: `paths|svg||true`
**Output:**
```php
<?php $img_title='paths'; $ext='svg'; $alt=''; $center='true'; require('Fragment/Component_image.php') ?>
```

#### Link XURL — `🔗`

Generates PHP `link_xurl()` calls. One link per line, format: `path|label`

**Notion:** Callout with 🔗 icon, text:
```
world/philosophy/life|Life
world/philosophy/death|Death
```
**Output:**
```php
<?php link_xurl('world/philosophy/life', 'Life') ?>
<?php link_xurl('world/philosophy/death', 'Death') ?>
```

#### Raw PHP/HTML — `🔧`

Outputs the callout text verbatim with no transformation. Use this for any complex PHP/HTML that doesn't fit other patterns (e.g. `group_image()` calls, Facebook components, custom includes).

Treat this callout as trusted code. Normal Notion text, links, code blocks, and PHP string parameters are escaped; only the 🔧 callout intentionally bypasses escaping.

**Notion:** Callout with 🔧 icon, text: `<?php group_image('paths', 3, 'svg') ?>`
**Output:**
```php
<?php group_image('paths', 3, 'svg') ?>
```

## Verification

Run the offline parser and configuration checks:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
```

Run the isolated live verification against the Notion page whose Id is `test/ncms-blocks` and whose Status is `test`:

```powershell
.\.venv\Scripts\python.exe test_e2e.py
```

The live verifier writes to a new temporary directory. It forcibly disables git push and Notion status updates, checks all expected generated artifacts, and confirms that the PHP example inside the Notion code block is emitted as display text rather than executable PHP.

"""
Script to create or update the canonical 'technology/computer/artificial_intelligence/machine_learning/models/llm/pricing'
article in the Notion Website database.
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

# Ensure stdout handles UTF-8
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('D:/Ujnotes/Website/ncms/.env')
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')

ARTICLE = {
    "slug": "technology/computer/artificial_intelligence/machine_learning/models/llm/pricing",
    "label": "LLM Pricing",
    "title": "LLM Pricing Reference",
    "description": "Official pricing hubs, model card registries, and token cost structures for Gemini, OpenAI, Claude, Grok, DeepSeek, and leading frontier AI providers.",
    "cover_alt": "Comparing token costs, prompt caching rates, and model cards across frontier AI providers.",
    "sections": [
        ("heading_1", "What is LLM pricing?"),
        ("paragraph", [
            {"text": "Language model pricing is the metered cost of running inference on large neural networks. Unlike traditional software that sells perpetual licenses or flat monthly seats, large language model APIs charge strictly for compute consumed, measured in "},
            {"text": "tokens", "bold": True},
            {"text": "—chunks of characters representing roughly three-quarters of an English word."}
        ]),
        ("paragraph", [
            {"text": "Every prompt sent to an API consumes input tokens during context processing, and every word, character, or punctuation mark produced by the model consumes output tokens. Because generating new text requires sequential autoregressive decoding steps on GPU tensor cores, output tokens typically cost between two and four times more than input tokens."}
        ]),
        ("paragraph", [
            {"text": "Modern provider economics also differentiate between standard real-time calls, cached prompt prefixes, asynchronous batch queues, and hidden reasoning tokens generated during internal chain-of-thought evaluation."}
        ]),

        ("heading_1", "How do pricing structures differ?"),
        ("paragraph", [
            {"text": "Evaluating model costs across different vendors requires understanding five core billing dimensions:"}
        ]),
        ("bulleted_list_item", [
            {"text": "Input versus output tokens", "bold": True},
            {"text": ": input tokens cover prompt ingestion, system instructions, few-shot examples, and retrieved context. Output tokens cover generated responses, tool arguments, and structured schema outputs."}
        ]),
        ("bulleted_list_item", [
            {"text": "Reasoning tokens", "bold": True},
            {"text": ": frontier reasoning architectures (such as OpenAI's o-series and DeepSeek-R1) generate extensive internal thinking tokens before producing a visible response. These internal tokens are billed at full output token rates, which significantly increases total query cost even when the final answer is short."}
        ]),
        ("bulleted_list_item", [
            {"text": "Prompt and context caching", "bold": True},
            {"text": ": when multiple requests share identical prompt prefixes—such as static documentation, system instructions, or code repositories—serving engines store precomputed Key-Value (KV) attention states. Reusing cached tokens reduces input costs by 50% to 90% and slashes time-to-first-token latency."}
        ]),
        ("bulleted_list_item", [
            {"text": "Context tiering", "bold": True},
            {"text": ": several frontier models apply higher token rates when context windows exceed standard thresholds (such as 128,000 or 200,000 tokens), reflecting the increased GPU memory bandwidth required to maintain large attention matrices."}
        ]),
        ("bulleted_list_item", [
            {"text": "Batch processing discounts", "bold": True},
            {"text": ": non-urgent workloads submitted to asynchronous batch endpoints (typically with a 24-hour completion window) receive an automatic 50% discount compared to real-time synchronous inference."}
        ]),

        ("heading_1", "Frontier provider pricing and model directories"),
        ("paragraph", [
            {"text": "Frontier AI laboratories maintain dedicated pricing hubs, developer consoles, and model card registries where specifications, benchmarks, and current token rates are published:"}
        ]),
        ("bulleted_list_item", [
            {"text": "Google DeepMind & Gemini", "bold": True},
            {"text": ": explore official "},
            {"text": "DeepMind Model Cards", "bold": True, "url": "https://deepmind.google/models/model-cards"},
            {"text": " for architecture specifications and benchmark evaluations across the Gemini family. Developer rates and context thresholds are detailed on the "},
            {"text": "Google AI Studio Pricing Hub", "bold": True, "url": "https://ai.google.dev/pricing"},
            {"text": ", while enterprise SLAs and provisioned throughput are managed on "},
            {"text": "Google Cloud Vertex AI Pricing", "bold": True, "url": "https://cloud.google.com/vertex-ai/generative-ai/pricing"},
            {"text": ". Full model capabilities and context windows are catalogued in the "},
            {"text": "Gemini API Models Documentation", "bold": True, "url": "https://ai.google.dev/gemini-api/docs/models/gemini"},
            {"text": "."}
        ]),
        ("bulleted_list_item", [
            {"text": "OpenAI", "bold": True},
            {"text": ": token rates for GPT-4o, GPT-4o mini, o1, o1-mini, and o3-mini are published on the official "},
            {"text": "OpenAI API Pricing Page", "bold": True, "url": "https://openai.com/api/pricing/"},
            {"text": ". Context limits, maximum completion tokens, and training snapshot dates are documented in the "},
            {"text": "OpenAI Platform Models Overview", "bold": True, "url": "https://platform.openai.com/docs/models"},
            {"text": ". OpenAI provides automatic prompt caching discounts and a 50% discount on Batch API requests."}
        ]),
        ("bulleted_list_item", [
            {"text": "Anthropic Claude", "bold": True},
            {"text": ": rates for Claude 3.5 Sonnet, Claude 3.5 Haiku, and Claude 3 Opus are available on the "},
            {"text": "Anthropic Pricing Hub", "bold": True, "url": "https://www.anthropic.com/pricing"},
            {"text": ". Detailed token limits (200k context), 5-minute prompt cache read/write pricing, and Message Batches discounts are outlined in the "},
            {"text": "Claude Models Overview & Rates", "bold": True, "url": "https://docs.anthropic.com/en/docs/about-claude/models"},
            {"text": "."}
        ]),
        ("bulleted_list_item", [
            {"text": "xAI Grok", "bold": True},
            {"text": ": developer rates and context specifications for Grok 2 and Grok Vision are indexed on the "},
            {"text": "xAI API Documentation & Pricing", "bold": True, "url": "https://docs.x.ai/docs/overview#pricing"},
            {"text": ". Account billing, team seats, and key limits are managed within the "},
            {"text": "xAI Developer Console", "bold": True, "url": "https://console.x.ai/"},
            {"text": "."}
        ]),
        ("bulleted_list_item", [
            {"text": "DeepSeek", "bold": True},
            {"text": ": transparent token costs for DeepSeek-V3 and DeepSeek-R1 are published on the "},
            {"text": "DeepSeek API Pricing Page", "bold": True, "url": "https://platform.deepseek.com/api-docs/pricing/"},
            {"text": ", featuring industry-disrupting base input rates, deep automatic cache hit discounts, and competitive output rates. Architecture details and context configurations are maintained in the "},
            {"text": "DeepSeek API Documentation", "bold": True, "url": "https://api-docs.deepseek.com/"},
            {"text": "."}
        ]),

        ("heading_1", "Open-weights and enterprise platforms"),
        ("paragraph", [
            {"text": "Commercial open-weights creators and hyperscale cloud providers offer dedicated managed hosting and model catalogs:"}
        ]),
        ("bulleted_list_item", [
            {"text": "Mistral AI", "bold": True},
            {"text": ": commercial API rates for Mistral Large, Mistral Small, Codestral, and Pixtral are available on the "},
            {"text": "Mistral AI Pricing Directory", "bold": True, "url": "https://mistral.ai/technology/#pricing"},
            {"text": ", with technical parameters documented in the "},
            {"text": "Mistral Models Platform Guide", "bold": True, "url": "https://docs.mistral.ai/getting-started/models/"},
            {"text": "."}
        ]),
        ("bulleted_list_item", [
            {"text": "Cohere", "bold": True},
            {"text": ": token pricing for Command R+, Command R, Embed 3, and Rerank 3.5 is listed on "},
            {"text": "Cohere Pricing", "bold": True, "url": "https://cohere.com/pricing"},
            {"text": ", with enterprise retrieval and connector guides in the "},
            {"text": "Cohere Models Documentation", "bold": True, "url": "https://docs.cohere.com/docs/models"},
            {"text": "."}
        ]),
        ("bulleted_list_item", [
            {"text": "Meta Llama", "bold": True},
            {"text": ": open-weight downloads for Llama 3.3 and Llama 3.1 are hosted on the "},
            {"text": "Meta Llama Official Hub", "bold": True, "url": "https://llama.meta.com/"},
            {"text": ". Technical documentation and evaluation benchmarks are detailed in the "},
            {"text": "Meta Model Cards & Prompt Formats", "bold": True, "url": "https://www.llama.com/docs/model-cards-and-prompt-formats/"},
            {"text": ". Note that while weights are free to self-host, cloud providers bill per-token fees for managed hosting."}
        ]),
        ("bulleted_list_item", [
            {"text": "Amazon Bedrock", "bold": True},
            {"text": ": unified serverless and provisioned throughput rates for hosting Anthropic, Meta, Mistral, AI21, and Cohere models inside AWS are listed on "},
            {"text": "Amazon Bedrock Pricing", "bold": True, "url": "https://aws.amazon.com/bedrock/pricing/"},
            {"text": "."}
        ]),
        ("bulleted_list_item", [
            {"text": "Microsoft Azure AI Foundry", "bold": True},
            {"text": ": enterprise pricing and regional deployment rates for Azure OpenAI and serverless open models are published on "},
            {"text": "Azure AI Services Pricing", "bold": True, "url": "https://azure.microsoft.com/en-us/pricing/details/cognitive-services/"},
            {"text": "."}
        ]),

        ("heading_1", "Dynamic price routers and specialized inference engines"),
        ("paragraph", [
            {"text": "When building multi-model routing architectures or optimizing for latency, third-party inference providers and aggregators offer dynamic comparative pricing:"}
        ]),
        ("bulleted_list_item", [
            {"text": "OpenRouter", "bold": True},
            {"text": ": maintains a live, normalized comparative index across 300+ models on the "},
            {"text": "OpenRouter Models Directory", "bold": True, "url": "https://openrouter.ai/models"},
            {"text": ", tracking real-time token pricing, prompt caching availability, and automated failover routing across providers."}
        ]),
        ("bulleted_list_item", [
            {"text": "Groq", "bold": True},
            {"text": ": provides ultra-fast token inference on custom Language Processing Units (LPUs). Current per-token pricing for Llama 3, Mixtral, and Whisper is published on "},
            {"text": "Groq Pricing", "bold": True, "url": "https://groq.com/pricing/"},
            {"text": "."}
        ]),
        ("bulleted_list_item", [
            {"text": "Together AI", "bold": True},
            {"text": ": serverless per-token inference rates and dedicated GPU cluster pricing for open-weights models are indexed on "},
            {"text": "Together AI Pricing", "bold": True, "url": "https://www.together.ai/pricing"},
            {"text": "."}
        ]),
        ("bulleted_list_item", [
            {"text": "Fireworks AI", "bold": True},
            {"text": ": specialized high-throughput inference rates and fine-tuning pricing for compound AI systems are listed on "},
            {"text": "Fireworks AI Pricing", "bold": True, "url": "https://fireworks.ai/pricing"},
            {"text": "."}
        ]),

        ("heading_1", "How to estimate and manage actual costs"),
        ("paragraph", [
            {"text": "Controlling API expenditure in production systems depends on sound architectural design rather than coupon clipping:"}
        ]),
        ("bulleted_list_item", [
            {"text": "Route tasks by required capability", "bold": True},
            {"text": ": avoid dispatching routine classification, data extraction, or summary tasks to expensive flagship models. Reserve flagship reasoning models for multi-step synthesis and route routine workloads to compact models like Gemini Flash, GPT-4o mini, or Claude Haiku."}
        ]),
        ("bulleted_list_item", [
            {"text": "Structure prompts for prefix caching", "bold": True},
            {"text": ": place invariant content—system prompts, tool definitions, schemas, and few-shot examples—at the very beginning of the prompt. Dynamic variables, timestamps, and user inputs should always appear at the end to prevent invalidating the KV cache."}
        ]),
        ("bulleted_list_item", [
            {"text": "Leverage batch endpoints for background jobs", "bold": True},
            {"text": ": evaluations, dataset backfills, embedding generation, and synthetic training runs rarely require sub-second latency. Submitting them to Batch APIs captures a flat 50% discount across major providers."}
        ]),
        ("bulleted_list_item", [
            {"text": "Cap reasoning token budgets", "bold": True},
            {"text": ": reasoning models can generate thousands of hidden tokens if prompt objectives are ambiguous. Set explicit token caps and clear stop criteria to prevent runaway chain-of-thought loops."}
        ]),
        ("bulleted_list_item", [
            {"text": "Verify live pricing hubs regularly", "bold": True},
            {"text": ": model pricing fluctuates as hardware efficiency and competition evolve. Always consult the linked parent directories and developer dashboards before scaling production deployments."}
        ]),
    ]
}

def make_rich_text(segments):
    rich_text = []
    for s in segments:
        annotations = {}
        if s.get("bold"):
            annotations["bold"] = True
        if s.get("italic"):
            annotations["italic"] = True
        item = {
            "type": "text",
            "text": {"content": s["text"]},
            "annotations": annotations
        }
        if s.get("url"):
            item["text"]["link"] = {"url": s["url"]}
        rich_text.append(item)
    return rich_text

def build_children(article):
    children = []
    # 1. Cover callout
    children.append({
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "\U0001f5bc\ufe0f"},
            "rich_text": [{"type": "text", "text": {"content": article["cover_alt"]}}]
        }
    })
    # 2. Sections
    for block_type, content in article["sections"]:
        if block_type == "heading_1":
            children.append({
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            })
        elif block_type == "paragraph":
            children.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": make_rich_text(content)
                }
            })
        elif block_type == "bulleted_list_item":
            children.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": make_rich_text(content)
                }
            })
    # 3. Divider
    children.append({
        "type": "divider",
        "divider": {}
    })
    # 4. AI disclosure
    children.append({
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Ai disclosure: written with the help of AI (ChatGPT). You are encouraged to point out errors and omissions."},
                    "annotations": {"italic": True}
                }
            ]
        }
    })
    return children

def create_or_update_article():
    slug = ARTICLE["slug"]
    res = notion.databases.query(database_id=database_id, filter={"property": "Id", "title": {"equals": slug}})
    existing = res.get("results", [])

    children = build_children(ARTICLE)

    if existing:
        page_id = existing[0]["id"]
        print(f"Page already exists for slug '{slug}': {page_id}. Updating properties and children...")
        notion.pages.update(
            page_id=page_id,
            properties={
                "Status": {"select": {"name": "publish"}},
                "Label": {"rich_text": [{"text": {"content": ARTICLE["label"]}}]},
                "Title": {"rich_text": [{"text": {"content": ARTICLE["title"]}}]},
                "JS": {"select": {"name": "0"}},
                "Description": {"rich_text": [{"text": {"content": ARTICLE["description"]}}]},
            }
        )
        # Delete existing blocks
        existing_blocks = notion.blocks.children.list(block_id=page_id).get("results", [])
        for block in existing_blocks:
            try:
                notion.blocks.delete(block_id=block["id"])
            except Exception as e:
                print(f"Warning deleting block {block['id']}: {e}")

        # Append new blocks in chunks of 50
        for i in range(0, len(children), 50):
            chunk = children[i:i+50]
            notion.blocks.children.append(block_id=page_id, children=chunk)
        print(f"Successfully updated Notion page '{slug}' ({page_id}) with {len(children)} blocks.")
        return page_id
    else:
        print(f"Creating new Notion page for '{slug}'...")
        first_chunk = children[:50]
        remaining = children[50:]
        page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Id": {"title": [{"text": {"content": slug}}]},
                "Status": {"select": {"name": "publish"}},
                "Label": {"rich_text": [{"text": {"content": ARTICLE["label"]}}]},
                "Title": {"rich_text": [{"text": {"content": ARTICLE["title"]}}]},
                "JS": {"select": {"name": "0"}},
                "Description": {"rich_text": [{"text": {"content": ARTICLE["description"]}}]},
            },
            children=first_chunk
        )
        page_id = page["id"]
        for i in range(0, len(remaining), 50):
            chunk = remaining[i:i+50]
            notion.blocks.children.append(block_id=page_id, children=chunk)
        print(f"Successfully created Notion page '{slug}' with ID: {page_id} and {len(children)} blocks.")
        return page_id

if __name__ == "__main__":
    create_or_update_article()

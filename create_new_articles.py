"""
Script to create the three requested canonical articles in Notion:
1. science/physics/electrical/inductance
2. technology/electronics/inductor
3. technology/computer/artificial_intelligence/machine_learning/models/llm/cache_handling
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

ARTICLES = [
    {
        "slug": "science/physics/electrical/inductance",
        "label": "Inductance",
        "title": "Inductance",
        "description": "How changing current induces opposing voltage, stores energy in magnetic fields, and shapes electrical circuits.",
        "cover_alt": "A coil opposing current change through a magnetic field.",
        "sections": [
            ("heading_1", "What is inductance?"),
            ("paragraph", [
                {"text": "Inductance is the property of an electrical conductor or circuit that opposes any change in electric current passing through it: "},
                {"text": "V = L (dI/dt)", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "It is measured in henrys. An inductor is an electrical component designed to provide concentrated inductance, usually formed by coiling conductive wire around a magnetic core. Stray inductance also exists in every wire, trace and component lead."}
            ]),
            ("heading_1", "How does it work?"),
            ("paragraph", [
                {"text": "When current flows through a conductor, it generates a magnetic field around it. If the current changes, that magnetic field expands or collapses."}
            ]),
            ("paragraph", [
                {"text": "By Faraday's law of induction and Lenz's law, a changing magnetic flux induces an electromotive force (voltage) that directly opposes the change in current that produced it. Because of this, current through an inductor cannot change instantaneously."}
            ]),
            ("heading_1", "What determines it?"),
            ("paragraph", [
                {"text": "For a simple coil, inductance increases with the square of the number of turns and the cross-sectional area, and decreases with the coil's length."}
            ]),
            ("paragraph", [
                {"text": "The core material has a decisive effect: a ferromagnetic core (such as iron or ferrite) concentrates magnetic flux and dramatically multiplies inductance compared to an air core, though magnetic cores can saturate when current becomes too high."}
            ]),
            ("heading_1", "Why is it important?"),
            ("paragraph", [
                {"text": "Inductance is fundamental to managing energy and electrical signals."}
            ]),
            ("paragraph", [
                {"text": "Together with resistance it sets a characteristic time scale "},
                {"text": "τ = L / R", "bold": True},
                {"text": ". Together with capacitance it forms resonant "},
                {"text": "LC", "bold": True},
                {"text": " circuits that can select frequencies, filter unwanted noise and sustain oscillations."}
            ]),
            ("paragraph", [
                {"text": "Inductors store energy in their magnetic field. That makes them indispensable in transformers, switch-mode power converters, motors and chokes that block high-frequency electromagnetic interference while allowing direct current to pass."}
            ]),
            ("heading_1", "Limits and non-ideal effects"),
            ("paragraph", [
                {"text": "Real inductors are never pure inductance. The coiled wire introduces series resistance, adjacent turns create parasitic capacitance, and magnetic cores incur hysteresis and eddy current losses."}
            ]),
            ("paragraph", [
                {"text": "In high-speed digital circuits, rapid switching causes sudden current transients ("},
                {"text": "dI/dt", "bold": True},
                {"text": "). This generates inductive voltage spikes and ground bounce across traces and power pins that circuit designers must carefully suppress."}
            ]),
        ]
    },
    {
        "slug": "technology/electronics/inductor",
        "label": "Inductors",
        "title": "Inductors",
        "description": "How coils store energy in magnetic fields to resist current changes, filter signals and manage power.",
        "cover_alt": "A wire-wound passive component storing energy in a magnetic field.",
        "sections": [
            ("heading_1", "What is an inductor?"),
            ("paragraph", [
                {"text": "An inductor is a passive two-terminal electrical component designed to store energy in a magnetic field when electric current flows through it."}
            ]),
            ("paragraph", [
                {"text": "The stored magnetic energy is given by "},
                {"text": "E = ½ L I²", "bold": True},
                {"text": ", where L is inductance in henrys and I is current in amperes."}
            ]),
            ("heading_1", "How does it behave?"),
            ("paragraph", [
                {"text": "An inductor resists changes in current. Voltage across the inductor is proportional to how fast current changes: "},
                {"text": "V = L (dI/dt)", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "It allows direct current (DC) to pass freely with only minimal resistance, but presents high impedance to alternating current (AC) as frequency increases: "},
                {"text": "X_L = 2π f L", "bold": True},
                {"text": "."}
            ]),
            ("heading_1", "Types and construction"),
            ("paragraph", [
                {"text": "Inductors come in diverse form factors tailored to specific applications:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Air-core inductors", "bold": True},
                {"text": ": coils with no magnetic core, offering zero core loss and high stability for high-frequency radio circuits."}
            ]),
            ("bulleted_list_item", [
                {"text": "Ferrite and iron-core inductors", "bold": True},
                {"text": ": coils wound around high-permeability cores to achieve large inductance in a small volume for power supplies."}
            ]),
            ("bulleted_list_item", [
                {"text": "Toroidal inductors", "bold": True},
                {"text": ": donut-shaped cores that contain magnetic flux within the ring, minimizing electromagnetic radiation and noise."}
            ]),
            ("bulleted_list_item", [
                {"text": "Surface-mount chip inductors", "bold": True},
                {"text": ": compact multi-layer or wire-wound packages soldered directly onto printed circuit boards."}
            ]),
            ("heading_1", "Where are they used?"),
            ("paragraph", [
                {"text": "Inductors are essential across modern electronic systems:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Power conversion", "bold": True},
                {"text": ": buck, boost, and flyback DC-DC converters rely on inductors to store and transfer energy smoothly between different voltage levels."}
            ]),
            ("bulleted_list_item", [
                {"text": "Filtering and EMI suppression", "bold": True},
                {"text": ": choke inductors block high-frequency noise on power rails and communication cables while letting DC pass."}
            ]),
            ("bulleted_list_item", [
                {"text": "Tuned circuits and resonance", "bold": True},
                {"text": ": paired with capacitors, inductors form resonant tanks for radio transmitters, receivers, and oscillators."}
            ]),
            ("heading_1", "Non-ideal limits"),
            ("paragraph", [
                {"text": "Every practical inductor has limitations. The copper wire has DC resistance that produces heat. High currents cause magnetic cores to saturate, collapsing inductance. Parasitic capacitance between wire turns creates a self-resonant frequency above which the inductor behaves as a capacitor."}
            ]),
        ]
    },
    {
        "slug": "technology/computer/artificial_intelligence/machine_learning/models/llm/cache_handling",
        "label": "LLM Cache Handling",
        "title": "LLM Cache Handling",
        "description": "How prompt caching, KV cache management, and context stability reduce latency, save tokens, and improve language model systems.",
        "cover_alt": "Reusing computed attention states and prefixes across language model interactions.",
        "sections": [
            ("heading_1", "What is LLM cache handling?"),
            ("paragraph", [
                {"text": "LLM cache handling is the practice of storing and reusing intermediate computations—attention states, prompt prefixes, or full responses—so a language model does not repeatedly compute what it already knows."}
            ]),
            ("paragraph", [
                {"text": "In large language models, computing attention across long sequences is computationally expensive. Caching transforms repeated queries and multi-turn conversations from redundant recalculation into fast, low-cost memory lookups."}
            ]),
            ("heading_1", "Why is caching essential for language models?"),
            ("paragraph", [
                {"text": "Transformers process text through self-attention, where every token attends to every preceding token. As context grows, prefill latency and computational cost scale sharply."}
            ]),
            ("paragraph", [
                {"text": "In typical applications, much of the input context is static: system instructions, tool schemas, few-shot examples, or uploaded documentation. Re-running the entire model over thousands of identical tokens on every user turn wastes compute, increases response latency, and multiplies API costs."}
            ]),
            ("heading_1", "The three main caching tiers"),
            ("paragraph", [
                {"text": "Effective LLM systems coordinate caching at three distinct layers:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Prompt and prefix caching", "bold": True},
                {"text": ": persists precomputed Key-Value (KV) attention states for common prompt prefixes across independent requests. When requests share an identical preamble, the model skips prefill for those tokens, slashing time-to-first-token and reducing input costs by up to 90%."}
            ]),
            ("bulleted_list_item", [
                {"text": "Inference KV caching", "bold": True},
                {"text": ": stores attention keys and values for previously generated tokens within an active sequence. Instead of re-evaluating the full sequence to generate token N+1, the decoder only computes the projection for the latest token and appends it to the KV cache."}
            ]),
            ("bulleted_list_item", [
                {"text": "Semantic and response caching", "bold": True},
                {"text": ": intercepts incoming requests at the application layer. By comparing prompt embeddings against previously answered queries, the system can return validated answers immediately without calling the model at all."}
            ]),
            ("heading_1", "How to design prompts for maximum cache hits"),
            ("paragraph", [
                {"text": "Prefix caching works from the beginning of the prompt forward. A single changed character at token 0 invalidates the cache for all subsequent tokens. To maximize cache reuse:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Order static content first", "bold": True},
                {"text": ": place permanent system instructions, tool declarations, and reference material at the very beginning of the prompt."}
            ]),
            ("bulleted_list_item", [
                {"text": "Keep volatile tokens at the end", "bold": True},
                {"text": ": never inject timestamps, randomized IDs, or ephemeral state early in the prompt. Place dynamic variables and the user's latest query at the very end."}
            ]),
            ("bulleted_list_item", [
                {"text": "Ensure deterministic formatting", "bold": True},
                {"text": ": maintain consistent serialization for JSON schemas, whitespace, and markdown headings so byte sequences remain identical across calls."}
            ]),
            ("heading_1", "Memory management and engine-level optimization"),
            ("paragraph", [
                {"text": "Because KV cache consumes significant GPU memory under high concurrency, modern serving engines employ advanced memory techniques. PagedAttention allocates KV cache in non-contiguous virtual memory blocks, eliminating external fragmentation. Radix trees enable automatic prefix sharing across branching agent trajectories, while FP8 and INT4 quantization compress KV cache tensors to double concurrent serving capacity without degrading output quality."}
            ]),
            ("heading_1", "Limits and challenges"),
            ("paragraph", [
                {"text": "Caching introduces trade-offs. Cache staleness can cause models to reference outdated context if background documentation changes. Shared caches across multi-tenant environments require strict access control to prevent information leakage, and large KV cache footprints require careful eviction policies to avoid GPU out-of-memory errors."}
            ]),
        ]
    }
]

def make_rich_text(segments):
    rich_text = []
    for s in segments:
        annotations = {}
        if s.get("bold"):
            annotations["bold"] = True
        if s.get("italic"):
            annotations["italic"] = True
        rich_text.append({
            "type": "text",
            "text": {"content": s["text"]},
            "annotations": annotations
        })
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

def create_articles():
    for art in ARTICLES:
        slug = art["slug"]
        # Check if exists
        res = notion.databases.query(database_id=database_id, filter={"property": "Id", "title": {"equals": slug}})
        existing = res.get("results", [])
        if existing:
            print(f"Page already exists for slug '{slug}': {existing[0]['id']}. Updating to status='publish'...")
            notion.pages.update(page_id=existing[0]['id'], properties={"Status": {"select": {"name": "publish"}}})
            continue

        print(f"Creating Notion page for '{slug}'...")
        page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Id": {"title": [{"text": {"content": slug}}]},
                "Status": {"select": {"name": "publish"}},
                "Label": {"rich_text": [{"text": {"content": art["label"]}}]},
                "Title": {"rich_text": [{"text": {"content": art["title"]}}]},
                "JS": {"select": {"name": "0"}},
                "Description": {"rich_text": [{"text": {"content": art["description"]}}]},
            },
            children=build_children(art)
        )
        print(f"Successfully created Notion page '{slug}' with ID: {page['id']}")

if __name__ == "__main__":
    create_articles()

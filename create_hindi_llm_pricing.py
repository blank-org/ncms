"""
Script to create the nested Hindi translation child page under the canonical
'technology/computer/artificial_intelligence/machine_learning/models/llm/pricing' Notion page.
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('D:/Ujnotes/Website/ncms/.env')
notion = Client(auth=os.getenv('NOTION_API_KEY'))
db_id = os.getenv('NOTION_DATABASE_ID')

HINDI_ARTICLE = {
    "parent_slug": "technology/computer/artificial_intelligence/machine_learning/models/llm/pricing",
    "label": "एलएलएम मूल्य निर्धारण",
    "title": "एलएलएम मूल्य निर्धारण संदर्भ",
    "description": "जेमिनी, ओपनएआई, क्लॉड, ग्रोक, डीपसीक और प्रमुख फ्रंटियर एआई प्रदाताओं के आधिकारिक मूल्य निर्धारण केंद्र, मॉडल कार्ड और टोकन लागत संरचना।",
    "sections": [
        ("heading_1", "एलएलएम मूल्य निर्धारण क्या है?"),
        ("paragraph", [
            {"text": "लार्ज लैंग्वेज मॉडल (एलएलएम) मूल्य निर्धारण न्यूरल नेटवर्क पर इनफ़रेंस चलाने की गणना-आधारित लागत है। पारंपरिक सॉफ़्टवेयर के विपरीत जो स्थायी लाइसेंस या निश्चित मासिक शुल्क पर बिकता है, एलएलएम एपीआई केवल उपयोग की गई कंप्यूट क्षमता के लिए शुल्क लेते हैं, जिसे "},
            {"text": "टोकन (tokens)", "bold": True},
            {"text": " में मापा जाता है। एक टोकन आमतौर पर एक अंग्रेज़ी शब्द के लगभग तीन-चौथाई हिस्से के बराबर होता है।"}
        ]),
        ("paragraph", [
            {"text": "एपीआई को भेजे गए प्रत्येक प्रॉम्प्ट में इनपुट टोकन खर्च होते हैं जो संदर्भ को संसाधित करते हैं, और मॉडल द्वारा उत्पन्न प्रत्येक शब्द, वर्ण या विराम चिह्न आउटपुट टोकन के रूप में मापा जाता है। जीपीयू टेन्सर कोर पर नए पाठ को क्रमिक रूप से उत्पन्न करने में अधिक गणना लगती है, इसलिए आउटपुट टोकन आमतौर पर इनपुट टोकन की तुलना में दो से चार गुना अधिक महंगे होते हैं।"}
        ]),
        ("paragraph", [
            {"text": "आधुनिक मूल्य निर्धारण मॉडल में वास्तविक समय के कॉल, पहले से गणना किए गए प्रॉम्प्ट प्रीफ़िक्स (कैशिंग), पृष्ठभूमि बैच अनुरोध, और छिपे हुए तर्क टोकन (रीज़निंग टोकन) के बीच भी अंतर किया जाता है।"}
        ]),

        ("heading_1", "मूल्य निर्धारण संरचनाओं में क्या अंतर है?"),
        ("paragraph", [
            {"text": "विभिन्न प्रदाताओं के बीच मॉडल लागत का मूल्यांकन करते समय पाँच मुख्य पहलुओं को समझना आवश्यक है:"}
        ]),
        ("bulleted_list_item", [
            {"text": "इनपुट बनाम आउटपुट टोकन", "bold": True},
            {"text": ": इनपुट टोकन में प्रॉम्प्ट, सिस्टम निर्देश, उदाहरण और संदर्भ शामिल होते हैं। आउटपुट टोकन में मॉडल द्वारा उत्पन्न प्रतिक्रियाएँ और संरचित आउटपुट शामिल होते हैं।"}
        ]),
        ("bulleted_list_item", [
            {"text": "रीज़निंग टोकन (Reasoning Tokens)", "bold": True},
            {"text": ": फ्रंटियर रीज़निंग मॉडल (जैसे ओपनएआई का o1/o3 और डीपसीक-R1) उत्तर देने से पहले आंतरिक विचार प्रक्रिया उत्पन्न करते हैं। इन आंतरिक टोकनों का बिल भी आउटपुट दर पर लिया जाता है, जिससे कुल लागत बढ़ जाती है।"}
        ]),
        ("bulleted_list_item", [
            {"text": "प्रॉम्प्ट और संदर्भ कैशिंग (Prompt Caching)", "bold": True},
            {"text": ": जब कई अनुरोध एक समान प्रॉम्प्ट प्रीफ़िक्स (जैसे बड़े सिस्टम निर्देश या दस्तावेज़) साझा करते हैं, तो इंजन पहले से गणना किए गए की-वैल्यू (KV) अटेंशन स्टेट्स को सहेजते हैं। कैश्ड टोकन के पुन: उपयोग से इनपुट लागत में 50% से 90% की कमी आती है।"}
        ]),
        ("bulleted_list_item", [
            {"text": "संदर्भ सीमा टियर (Context Tiers)", "bold": True},
            {"text": ": कई मॉडल मानक सीमा (जैसे 128,000 टोकन) से अधिक लंबे प्रॉम्प्ट के लिए उच्च दरें लागू करते हैं, क्योंकि बड़े अटेंशन मैट्रिक्स को बनाए रखने के लिए अधिक जीपीयू मेमोरी बैंडविड्थ की आवश्यकता होती है।"}
        ]),
        ("bulleted_list_item", [
            {"text": "बैच प्रोसेसिंग छूट (Batch API)", "bold": True},
            {"text": ": जो कार्य तुरंत वास्तविक समय में आवश्यक नहीं होते और 24 घंटे के भीतर संसाधित किए जा सकते हैं, उन पर स्वचालित रूप से 50% तक की छूट मिलती है।"}
        ]),

        ("heading_1", "प्रमुख प्रदाताओं के मूल्य निर्धारण और मॉडल निर्देशिकाएँ"),
        ("paragraph", [
            {"text": "अग्रणी एआई प्रयोगशालाएँ आधिकारिक मूल्य निर्धारण पोर्टल, डेवलपर कंसोल और मॉडल कार्ड बनाए रखती हैं जहाँ विनिर्देश और दरें प्रकाशित की जाती हैं:"}
        ]),
        ("bulleted_list_item", [
            {"text": "गूगल डीपमाइंड और जेमिनी (Gemini)", "bold": True},
            {"text": ": जेमिनी परिवार के सभी विनिर्देशों और बेंचमार्क के लिए आधिकारिक "},
            {"text": "DeepMind Model Cards", "bold": True, "url": "https://deepmind.google/models/model-cards"},
            {"text": " देखें। डेवलपर दरों और कैशिंग छूट की जानकारी "},
            {"text": "Google AI Studio Pricing", "bold": True, "url": "https://ai.google.dev/pricing"},
            {"text": " पर उपलब्ध है, जबकि एंटरप्राइज़ दरें "},
            {"text": "Google Cloud Vertex AI Pricing", "bold": True, "url": "https://cloud.google.com/vertex-ai/generative-ai/pricing"},
            {"text": " पर प्रबंधित होती हैं। मॉडल क्षमताओं की सूची "},
            {"text": "Gemini API Models Documentation", "bold": True, "url": "https://ai.google.dev/gemini-api/docs/models/gemini"},
            {"text": " में है।"}
        ]),
        ("bulleted_list_item", [
            {"text": "ओपनएआई (OpenAI)", "bold": True},
            {"text": ": GPT-4o, GPT-4o mini, o1, o1-mini और o3-mini की प्रति मिलियन टोकन दरें "},
            {"text": "OpenAI API Pricing Page", "bold": True, "url": "https://openai.com/api/pricing/"},
            {"text": " पर उपलब्ध हैं। संदर्भ सीमाओं और मॉडल विवरण के लिए "},
            {"text": "OpenAI Platform Models Overview", "bold": True, "url": "https://platform.openai.com/docs/models"},
            {"text": " देखें।"}
        ]),
        ("bulleted_list_item", [
            {"text": "एंथ्रोपिक क्लॉड (Anthropic Claude)", "bold": True},
            {"text": ": Claude 3.5 Sonnet, Claude 3.5 Haiku और Claude 3 Opus की आधिकारिक दरें "},
            {"text": "Anthropic Pricing Hub", "bold": True, "url": "https://www.anthropic.com/pricing"},
            {"text": " पर हैं। प्रॉम्प्ट कैशिंग (90% रीड छूट) और संदेश बैचिंग का विवरण "},
            {"text": "Claude Models Overview & Rates", "bold": True, "url": "https://docs.anthropic.com/en/docs/about-claude/models"},
            {"text": " में दर्ज है।"}
        ]),
        ("bulleted_list_item", [
            {"text": "एक्सएआई ग्रोक (xAI Grok)", "bold": True},
            {"text": ": Grok 2 और Grok Vision की एपीआई दरें "},
            {"text": "xAI API Documentation & Pricing", "bold": True, "url": "https://docs.x.ai/docs/overview#pricing"},
            {"text": " पर सूचीबद्ध हैं। उपयोग और बिलिंग "},
            {"text": "xAI Developer Console", "bold": True, "url": "https://console.x.ai/"},
            {"text": " से प्रबंधित होती है।"}
        ]),
        ("bulleted_list_item", [
            {"text": "डीपसीक (DeepSeek)", "bold": True},
            {"text": ": DeepSeek-V3 और DeepSeek-R1 की लागत "},
            {"text": "DeepSeek API Pricing Page", "bold": True, "url": "https://platform.deepseek.com/api-docs/pricing/"},
            {"text": " पर प्रकाशित है, जिसमें उद्योग की सबसे प्रतिस्पर्धी इनपुट और कैश्ड दरें शामिल हैं। वास्तुकला विवरण "},
            {"text": "DeepSeek API Documentation", "bold": True, "url": "https://api-docs.deepseek.com/"},
            {"text": " में देखा जा सकता है।"}
        ]),

        ("heading_1", "ओपन-वेट्स और एंटरप्राइज़ प्लेटफ़ॉर्म"),
        ("paragraph", [
            {"text": "ओपन-वेट्स निर्माता और क्लाउड कंपनियाँ प्रबंधित होस्टिंग और मॉडल कैटलॉग प्रदान करती हैं:"}
        ]),
        ("bulleted_list_item", [
            {"text": "मिस्ट्रल एआई (Mistral AI)", "bold": True},
            {"text": ": Mistral Large, Mistral Small और Codestral की व्यावसायिक दरें "},
            {"text": "Mistral AI Pricing Directory", "bold": True, "url": "https://mistral.ai/technology/#pricing"},
            {"text": " और गाइड "},
            {"text": "Mistral Models Platform Guide", "bold": True, "url": "https://docs.mistral.ai/getting-started/models/"},
            {"text": " पर उपलब्ध हैं।"}
        ]),
        ("bulleted_list_item", [
            {"text": "कोहियर (Cohere)", "bold": True},
            {"text": ": Command R+, Command R और Rerank की कीमतें "},
            {"text": "Cohere Pricing", "bold": True, "url": "https://cohere.com/pricing"},
            {"text": " पर और तकनीकी दस्तावेज़ "},
            {"text": "Cohere Models Documentation", "bold": True, "url": "https://docs.cohere.com/docs/models"},
            {"text": " पर हैं।"}
        ]),
        ("bulleted_list_item", [
            {"text": "मेटा लामा (Meta Llama)", "bold": True},
            {"text": ": Llama 3.3 और 3.1 के ओपन मॉडल "},
            {"text": "Meta Llama Official Hub", "bold": True, "url": "https://llama.meta.com/"},
            {"text": " पर हैं, और मॉडल कार्ड "},
            {"text": "Meta Model Cards & Prompt Formats", "bold": True, "url": "https://www.llama.com/docs/model-cards-and-prompt-formats/"},
            {"text": " में हैं।"}
        ]),
        ("bulleted_list_item", [
            {"text": "अमेज़ॅन बेडरॉक (Amazon Bedrock)", "bold": True},
            {"text": ": एडब्ल्यूएस पर प्रबंधित मॉडल होस्टिंग की दरें "},
            {"text": "Amazon Bedrock Pricing", "bold": True, "url": "https://aws.amazon.com/bedrock/pricing/"},
            {"text": " पर सूचीबद्ध हैं।"}
        ]),
        ("bulleted_list_item", [
            {"text": "माइक्रोसॉफ्ट अज़्योर एआई (Microsoft Azure AI)", "bold": True},
            {"text": ": अज़्योर ओपनएआई और सर्वरलेस मॉडल की कीमतें "},
            {"text": "Azure AI Services Pricing", "bold": True, "url": "https://azure.microsoft.com/en-us/pricing/details/cognitive-services/"},
            {"text": " पर उपलब्ध हैं।"}
        ]),

        ("heading_1", "डायनामिक मूल्य राउटर और विशेष इनफ़रेंस इंजन"),
        ("paragraph", [
            {"text": "कई मॉडलों के बीच स्वचालित रूटिंग और तुलनात्मक मूल्य देखने के लिए तृतीय-पक्ष प्रदाता उपयोगी हैं:"}
        ]),
        ("bulleted_list_item", [
            {"text": "ओपनराउटर (OpenRouter)", "bold": True},
            {"text": ": 300 से अधिक मॉडलों का वास्तविक समय मूल्य सूचकांक "},
            {"text": "OpenRouter Models Directory", "bold": True, "url": "https://openrouter.ai/models"},
            {"text": " पर बनाए रखता है।"}
        ]),
        ("bulleted_list_item", [
            {"text": "ग्रॉक (Groq)", "bold": True},
            {"text": ": कस्टम एलपीयू हार्डवेयर पर अत्यधिक तेज़ इनफ़रेंस दरें "},
            {"text": "Groq Pricing", "bold": True, "url": "https://groq.com/pricing/"},
            {"text": " पर प्रदान करता है।"}
        ]),
        ("bulleted_list_item", [
            {"text": "टुगेदर एआई (Together AI)", "bold": True},
            {"text": ": ओपन मॉडलों के लिए सर्वरलेस टोकन दरें "},
            {"text": "Together AI Pricing", "bold": True, "url": "https://www.together.ai/pricing"},
            {"text": " पर उपलब्ध हैं।"}
        ]),
        ("bulleted_list_item", [
            {"text": "फ़ायरवर्क्स एआई (Fireworks AI)", "bold": True},
            {"text": ": त्वरित फ़ंक्शन कॉलिंग और इनफ़रेंस दरें "},
            {"text": "Fireworks AI Pricing", "bold": True, "url": "https://fireworks.ai/pricing"},
            {"text": " पर सूचीबद्ध हैं।"}
        ]),

        ("heading_1", "लागत का अनुमान और प्रबंधन कैसे करें"),
        ("paragraph", [
            {"text": "उत्पादन प्रणालियों में खर्च को नियंत्रित करने के लिए व्यावहारिक नियम:"}
        ]),
        ("bulleted_list_item", [
            {"text": "कार्य की जटिलता के अनुसार मॉडल चुनें", "bold": True},
            {"text": ": सामान्य वर्गीकरण या निष्कर्षण के लिए महंगे मॉडलों का उपयोग करने से बचें; नियमित कार्यों के लिए छोटे मॉडल (Gemini Flash, GPT-4o mini, Claude Haiku) चुनें।"}
        ]),
        ("bulleted_list_item", [
            {"text": "प्रॉम्प्ट कैशिंग के अनुकूल संरचना बनाएँ", "bold": True},
            {"text": ": अपरिवर्तनीय सिस्टम निर्देशों और दस्तावेज़ों को प्रॉम्प्ट की शुरुआत में रखें, और गतिशील चर हमेशा अंत में रखें।"}
        ]),
        ("bulleted_list_item", [
            {"text": "पृष्ठभूमि कार्यों के लिए बैच एपीआई का उपयोग करें", "bold": True},
            {"text": ": गैर-तात्कालिक कार्यों के लिए बैच अनुरोध भेजकर 50% तक लागत बचाएँ।"}
        ]),
        ("bulleted_list_item", [
            {"text": "रीज़निंग टोकन की सीमा निर्धारित करें", "bold": True},
            {"text": ": रीज़निंग मॉडलों को अनियंत्रित टोकन खर्च करने से रोकने के लिए अधिकतम टोकन सीमा तय करें।"}
        ]),
        ("bulleted_list_item", [
            {"text": "आधिकारिक मूल्य पृष्ठों की नियमित समीक्षा करें", "bold": True},
            {"text": ": कंप्यूट क्षमता में सुधार के साथ कीमतें अक्सर बदलती हैं; बड़े पैमाने परिनियोजन से पहले आधिकारिक डैशबोर्ड अवश्य देखें।"}
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

def build_hindi_blocks(art):
    children = []
    meta_content = f"Language: hi\nLabel: {art['label']}\nTitle: {art['title']}\nDescription: {art['description']}"
    children.append({
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "🌐"},
            "rich_text": [{"type": "text", "text": {"content": meta_content}}]
        }
    })
    for block_type, content in art["sections"]:
        if block_type == "heading_1":
            children.append({
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": content}}]}
            })
        elif block_type == "paragraph":
            children.append({
                "type": "paragraph",
                "paragraph": {"rich_text": make_rich_text(content)}
            })
        elif block_type == "bulleted_list_item":
            children.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": make_rich_text(content)}
            })
    children.append({"type": "divider", "divider": {}})
    children.append({
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "एआई प्रकटीकरण: एआई (ChatGPT) की सहायता से लिखा गया। आपसे अनुरोध है कि त्रुटियों और चूकों की ओर ध्यान दिलाएँ।"},
                    "annotations": {"italic": True}
                }
            ]
        }
    })
    return children

def create_hindi_page():
    slug = HINDI_ARTICLE["parent_slug"]
    res = notion.databases.query(database_id=db_id, filter={"property": "Id", "title": {"equals": slug}})
    pages = res.get("results", [])
    if not pages:
        print(f"Parent page not found for '{slug}'")
        return
    parent_id = pages[0]['id']

    blocks = notion.blocks.children.list(block_id=parent_id).get('results', [])
    for b in blocks:
        if b.get('type') == 'child_page' and 'हिन्दी' in b.get('child_page', {}).get('title', ''):
            print(f"Deleting existing Hindi child page in '{slug}' ({b['id']})...")
            notion.blocks.delete(block_id=b['id'])

    print(f"Creating Hindi child page for '{slug}'...")
    child_blocks = build_hindi_blocks(HINDI_ARTICLE)
    first_chunk = child_blocks[:50]
    remaining = child_blocks[50:]

    child = notion.pages.create(
        parent={"page_id": parent_id},
        properties={
            "title": [{"type": "text", "text": {"content": "हिन्दी (hi)"}}]
        },
        children=first_chunk
    )
    for i in range(0, len(remaining), 50):
        chunk = remaining[i:i+50]
        notion.blocks.children.append(block_id=child['id'], children=chunk)
    print(f"Created Hindi child for '{slug}': {child['id']} with {len(child_blocks)} blocks.")

if __name__ == "__main__":
    create_hindi_page()

"""
Create the 8 additional canonical English business articles in Notion:
  1. business/plastic_money
  2. business/digital_money
  3. business/stock
  4. business/bond
  5. business/stock_exchange
  6. business/hedging
  7. business/exchange_rate
  8. business/inflation
And update the business hub topic list.
"""

import os
import sys
from dotenv import load_dotenv
from notion_client import Client

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('D:/Ujnotes/Website/ncms/.env')
notion = Client(auth=os.getenv('NOTION_API_KEY'))
database_id = os.getenv('NOTION_DATABASE_ID')

ARTICLES = [
    {
        "slug": "business/plastic_money",
        "label": "Plastic Money",
        "title": "Plastic Money",
        "type": "article",
        "description": "How payment cards, magnetic stripes, and electronic payment networks replaced physical cash with instant card-based transactions.",
        "cover_alt": "Credit and debit cards with embedded microchips and payment terminals.",
        "sections": [
            ("heading_1", "What is plastic money?"),
            ("paragraph", [
                {"text": "Plastic money refers to payment cards—primarily debit cards and credit cards—made of plastic with embedded magnetic stripes or microchips that allow people to pay for goods and services without carrying physical cash."}
            ]),
            ("heading_1", "Debit versus credit"),
            ("paragraph", [
                {"text": "Though they look identical, debit and credit cards represent two completely different financial mechanisms:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Debit cards", "bold": True},
                {"text": " — Deduct money directly from your existing bank account balance in real time. You are spending money you already own."}
            ]),
            ("bulleted_list_item", [
                {"text": "Credit cards", "bold": True},
                {"text": " — Draw on a pre-approved revolving line of credit extended by the card issuer. The bank pays the merchant immediately on your behalf, and you receive an itemised bill at the end of the month to settle the debt."}
            ]),
            ("heading_1", "How does a card transaction work?"),
            ("paragraph", [
                {"text": "When you tap or insert a card at a payment terminal, an intricate series of digital handshakes happens in under two seconds:"}
            ]),
            ("bulleted_list_item", [
                {"text": "1. Terminal to Acquirer", "bold": True},
                {"text": " — The point-of-sale machine encrypts your card details and sends the request to the merchant's bank (the acquiring bank)."}
            ]),
            ("bulleted_list_item", [
                {"text": "2. Payment Network", "bold": True},
                {"text": " — The acquirer routes the transaction through a global payment network such as Visa, Mastercard, RuPay, or American Express."}
            ]),
            ("bulleted_list_item", [
                {"text": "3. Card Issuer Approval", "bold": True},
                {"text": " — The network contacts your bank (the issuing bank), which checks available funds or credit limit, screens for fraud, and returns an approval code back through the chain."}
            ]),
            ("heading_1", "Benefits and risks"),
            ("paragraph", [
                {"text": "Plastic money dramatically reduced the risk of carrying large bundles of paper cash and made cross-border purchases and online commerce seamless. It also provides fraud protections where compromised cards can be blocked instantly."}
            ]),
            ("paragraph", [
                {"text": "However, credit cards can easily become debt traps. Because swiping plastic decouples the psychological pain of parting with physical cash from the purchase, consumers often overspend, incurring steep compound interest rates on unpaid revolving balances."}
            ]),
        ]
    },
    {
        "slug": "business/digital_money",
        "label": "Digital Money",
        "title": "Digital Money",
        "type": "article",
        "description": "How currency transformed into purely electronic ledger entries, real-time payment networks, and programmable money.",
        "cover_alt": "Digital transaction streams connecting smartphones, bank servers, and electronic ledgers.",
        "sections": [
            ("heading_1", "What is digital money?"),
            ("paragraph", [
                {"text": "Digital money is currency that exists exclusively in electronic form rather than as physical paper banknotes or metal coins. Today, more than ninety percent of the world's money supply exists only as digital entries on computerised bank ledgers."}
            ]),
            ("heading_1", "How does digital money move?"),
            ("paragraph", [
                {"text": "When you transfer money digitally, no physical currency changes hands. Instead, central and commercial banks update corresponding debit and credit entries on their databases."}
            ]),
            ("paragraph", [
                {"text": "Modern payment rails make these updates instantaneous. Systems like India's Unified Payments Interface ("},
                {"text": "UPI", "bold": True},
                {"text": "), the UK's Faster Payments, and Europe's SEPA allow individuals and merchants to settle transactions in seconds using mobile apps and QR codes, bypassing traditional multi-day clearing delays."}
            ]),
            ("heading_1", "Forms of digital currency"),
            ("paragraph", [
                {"text": "Digital money encompasses several distinct architectures:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Commercial bank money", "bold": True},
                {"text": " — Electronic deposits in checking and savings accounts, backed by commercial banks and protected by deposit insurance."}
            ]),
            ("bulleted_list_item", [
                {"text": "Central Bank Digital Currencies (CBDCs)", "bold": True},
                {"text": " — A digital form of sovereign fiat currency issued and backed directly by a nation's central bank, serving as legal tender alongside cash."}
            ]),
            ("bulleted_list_item", [
                {"text": "Cryptocurrencies", "bold": True},
                {"text": " — Private digital tokens managed on decentralised cryptographic blockchains without central bank intermediaries."}
            ]),
            ("heading_1", "Why does it matter?"),
            ("paragraph", [
                {"text": "Digital money drastically lowers transaction friction, eliminates the logistical cost of minting, transporting, and securing physical cash, and expands financial inclusion to anyone with a basic mobile phone."}
            ]),
            ("paragraph", [
                {"text": "At the same time, it raises major questions about privacy, financial surveillance, and systemic reliance on unbroken electricity and telecommunication networks."}
            ]),
        ]
    },
    {
        "slug": "business/stock",
        "label": "Stock",
        "title": "Stock",
        "type": "article",
        "description": "How shares represent fractional ownership in a corporation, giving holders residual claims on profits and voting rights.",
        "cover_alt": "Stock certificates and financial market charts illustrating equity shares in a company.",
        "sections": [
            ("heading_1", "What is a stock?"),
            ("paragraph", [
                {"text": "A stock (also called a share or equity) represents fractional ownership in a corporation. When you own a share of a company, you legally own a proportional piece of that company's assets and future earnings."}
            ]),
            ("heading_1", "How do stockholders make money?"),
            ("paragraph", [
                {"text": "Investors make money from holding stocks through two distinct paths:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Dividends", "bold": True},
                {"text": " — Regular cash distributions paid to shareholders when a profitable company decides to share a portion of its net earnings rather than reinvesting all of it back into operations."}
            ]),
            ("bulleted_list_item", [
                {"text": "Capital appreciation", "bold": True},
                {"text": " — Selling the share for a higher price than what you paid for it. If a company invents popular products, grows revenues, and expands its profit margins, other investors will value its shares more highly, driving up the stock price."}
            ]),
            ("heading_1", "Limited liability and residual claims"),
            ("paragraph", [
                {"text": "Two legal concepts make corporate stock powerful:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Limited liability", "bold": True},
                {"text": " — As a shareholder, your financial loss is strictly limited to the amount you invested. If the corporation goes bankrupt or gets sued, creditors cannot seize your personal home, car, or bank savings."}
            ]),
            ("bulleted_list_item", [
                {"text": "Residual claim", "bold": True},
                {"text": " — Stockholders stand last in line. If a company liquidates, bondholders, suppliers, employees, and tax authorities must be fully paid before shareholders receive any remaining assets. In exchange for taking that risk, shareholders enjoy unlimited upside when the company thrives."}
            ]),
            ("heading_1", "Primary versus secondary markets"),
            ("paragraph", [
                {"text": "When a company first sells shares to the public to raise capital for factories or research, it does so in the "},
                {"text": "primary market", "bold": True},
                {"text": " through an Initial Public Offering (IPO)."}
            ]),
            ("paragraph", [
                {"text": "After that initial sale, those shares trade continuously between investors on the "},
                {"text": "secondary market", "bold": True},
                {"text": " (the stock exchange). In secondary trading, money flows between investors, not to the company itself."}
            ]),
        ]
    },
    {
        "slug": "business/bond",
        "label": "Bond",
        "title": "Bond",
        "type": "article",
        "description": "How debt securities allow governments and companies to borrow capital from the public, paying fixed interest until maturity.",
        "cover_alt": "A formal sovereign bond certificate with coupon schedule and seal.",
        "sections": [
            ("heading_1", "What is a bond?"),
            ("paragraph", [
                {"text": "A bond is a debt security issued by a government or corporation to raise capital from investors. In plain terms, a bond is a formal IOU: when you buy a bond, you are lending money to the issuer in exchange for regular interest payments and the full return of your principal on a set date."}
            ]),
            ("heading_1", "Anatomy of a bond"),
            ("paragraph", [
                {"text": "Every bond is defined by three core characteristics:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Face value (Par value)", "bold": True},
                {"text": " — The nominal amount the issuer borrows and promises to pay back when the bond matures (for example, ₹1,000 or $1,000)."}
            ]),
            ("bulleted_list_item", [
                {"text": "Coupon rate", "bold": True},
                {"text": " — The annual interest rate paid by the issuer, usually distributed semi-annually or annually. A 6% coupon on a ₹1,000 bond pays ₹60 each year."}
            ]),
            ("bulleted_list_item", [
                {"text": "Maturity date", "bold": True},
                {"text": " — The specific future date when the loan ends and the issuer repays the full principal face value to the bondholder."}
            ]),
            ("heading_1", "The bond seesaw: prices and yields"),
            ("paragraph", [
                {"text": "Bonds can be bought and sold on secondary markets before they mature. When prevailing market interest rates change, existing bond prices move in the opposite direction, like a seesaw:"}
            ]),
            ("paragraph", [
                {"text": "If current interest rates rise to 8%, nobody will pay full price for an existing bond paying only 6%. To attract buyers, the price of that 6% bond must drop until its effective yield matches current market rates. Conversely, when interest rates drop, older higher-paying bonds trade at a premium."}
            ]),
            ("heading_1", "Stocks versus bonds"),
            ("paragraph", [
                {"text": "Stocks and bonds represent two halves of capital markets:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Stocks are equity", "bold": True},
                {"text": " — You own a piece of the company. Returns are unpredictable, but potential upside is unlimited."}
            ]),
            ("bulleted_list_item", [
                {"text": "Bonds are debt", "bold": True},
                {"text": " — You are a creditor. Returns are contractually fixed, and bondholders have legal priority over stockholders if the issuer defaults."}
            ]),
        ]
    },
    {
        "slug": "business/stock_exchange",
        "label": "Stock Exchange",
        "title": "Stock Exchange",
        "type": "article",
        "description": "How organized, regulated marketplaces provide liquidity, price discovery, and fair trading for buyers and sellers of securities.",
        "cover_alt": "Trading floor terminals and digital order books matching buy and sell bids.",
        "sections": [
            ("heading_1", "What is a stock exchange?"),
            ("paragraph", [
                {"text": "A stock exchange is a centralised, highly regulated marketplace where brokers, institutional investors, and individual traders buy and sell securities like stocks, bonds, and exchange-traded funds."}
            ]),
            ("heading_1", "How does an exchange work?"),
            ("paragraph", [
                {"text": "At the core of every modern stock exchange is an electronic "},
                {"text": "order book", "bold": True},
                {"text": ". Buyers submit bids (the highest price they are willing to pay), and sellers submit asks (the lowest price they are willing to accept)."}
            ]),
            ("paragraph", [
                {"text": "Automated matching engines continuously pair compatible buy and sell orders in microseconds. When a buyer's bid meets a seller's ask, a trade executes, and the transaction details are broadcast publicly."}
            ]),
            ("heading_1", "Two vital functions of an exchange"),
            ("paragraph", [
                {"text": "Stock exchanges perform two functions essential to a healthy modern economy:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Liquidity", "bold": True},
                {"text": " — Without an exchange, selling shares in a company would require privately searching for a willing buyer, negotiating legal contracts, and waiting weeks. An exchange guarantees that you can convert your investments into cash in seconds at transparent market prices."}
            ]),
            ("bulleted_list_item", [
                {"text": "Price discovery", "bold": True},
                {"text": " — By pooling thousands of independent buyers and sellers, the exchange constantly incorporates new news, company earnings, and macroeconomic trends into an objective consensus price."}
            ]),
            ("heading_1", "From trading floors to high-frequency servers"),
            ("paragraph", [
                {"text": "Historically, stock exchanges operated as crowded trading pits where floor traders shouted orders and used hand signals (open-outcry)."}
            ]),
            ("paragraph", [
                {"text": "Today, nearly all trading is entirely digital. Major exchanges like the NYSE, Nasdaq, London Stock Exchange, and National Stock Exchange of India (NSE) operate out of high-speed data centres, where algorithmic systems execute millions of trades per second."}
            ]),
        ]
    },
    {
        "slug": "business/hedging",
        "label": "Hedging",
        "title": "Hedging",
        "type": "article",
        "description": "How businesses and investors take offsetting positions in markets to reduce or eliminate the risk of adverse price movements.",
        "cover_alt": "An umbrella shielding an investment portfolio from volatile market swings.",
        "sections": [
            ("heading_1", "What is hedging?"),
            ("paragraph", [
                {"text": "Hedging is a risk management strategy where an investor or business takes an offsetting financial position to protect against potential losses from adverse price fluctuations. In plain terms, hedging is financial insurance."}
            ]),
            ("heading_1", "An everyday analogy"),
            ("paragraph", [
                {"text": "Consider a farmer planting wheat in the spring. If wheat prices crash by harvest time in autumn, the farmer might make a heavy loss. To protect themselves, the farmer enters a contract today agreeing to sell their wheat in six months at a locked-in price."}
            ]),
            ("paragraph", [
                {"text": "If wheat prices plunge, the contract protects the farmer. If wheat prices skyrocket, the farmer misses out on extra profits, but their business survives. The hedge eliminated the existential risk of price volatility."}
            ]),
            ("heading_1", "How do hedges work in practice?"),
            ("paragraph", [
                {"text": "Hedging commonly relies on derivative contracts:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Futures and forwards", "bold": True},
                {"text": " — Binding agreements to buy or sell an asset (such as crude oil, currency, or grain) at a predetermined price on a future date. Airlines routinely buy jet fuel futures to protect themselves from unexpected oil price spikes."}
            ]),
            ("bulleted_list_item", [
                {"text": "Options", "bold": True},
                {"text": " — Contracts giving the buyer the right, but not the obligation, to buy or sell an asset at a fixed strike price. A put option acts like an insurance policy against falling stock prices."}
            ]),
            ("heading_1", "Hedging versus speculating"),
            ("paragraph", [
                {"text": "People often confuse hedging with speculation because both use derivative markets, but their motivations are exact opposites:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Speculators accept risk", "bold": True},
                {"text": " — They bet on price movements with the goal of making a profit."}
            ]),
            ("bulleted_list_item", [
                {"text": "Hedgers avoid risk", "bold": True},
                {"text": " — They gladly pay a small fee or forgo windfall profits in order to secure predictability for their core operations."}
            ]),
        ]
    },
    {
        "slug": "business/exchange_rate",
        "label": "Exchange Rate",
        "title": "Exchange Rate",
        "type": "article",
        "description": "Why different countries have different currency values, and the fundamental economic forces that drive exchange rates.",
        "cover_alt": "Currency symbols interacting on a balancing scale, illustrating foreign exchange valuation.",
        "sections": [
            ("heading_1", "What is an exchange rate?"),
            ("paragraph", [
                {"text": "An exchange rate is the price of one country's currency expressed in terms of another country's currency. For example, if 1 US dollar equals 85 Indian rupees, the exchange rate is USD/INR = 85."}
            ]),
            ("heading_1", "Why do different countries have different exchange rates?"),
            ("paragraph", [
                {"text": "Currencies are traded around the clock in the global foreign exchange (forex) market. Just like any other good, the exchange rate is determined by supply and demand: how many people want to buy that currency compared to how many want to sell it."}
            ]),
            ("heading_1", "Key forces driving currency values"),
            ("paragraph", [
                {"text": "Five main economic factors dictate whether a currency strengthens or weakens:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Trade balance (Exports vs Imports)", "bold": True},
                {"text": " — When a country exports goods that global buyers demand, foreigners must purchase the exporter's local currency to pay for them, driving up its value. Heavy net importers constantly sell local currency to buy foreign goods, putting downward pressure on their exchange rate."}
            ]),
            ("bulleted_list_item", [
                {"text": "Interest rates", "bold": True},
                {"text": " — Central banks set benchmark interest rates. Higher interest rates offer lenders better returns than other nations, attracting foreign investment capital and strengthening the currency."}
            ]),
            ("bulleted_list_item", [
                {"text": "Inflation differentials", "bold": True},
                {"text": " — A country with persistently high inflation sees its domestic purchasing power erode rapidly. According to Purchasing Power Parity (PPP), high-inflation currencies tend to depreciate against currencies with lower inflation."}
            ]),
            ("bulleted_list_item", [
                {"text": "Public debt and economic stability", "bold": True},
                {"text": " — Countries with stable governments, strong rule of law, and manageable debt attract international confidence. Political turmoil or risk of debt default triggers rapid capital flight."}
            ]),
            ("bulleted_list_item", [
                {"text": "Speculation and reserve status", "bold": True},
                {"text": " — Currencies like the US dollar or Swiss franc function as \"safe havens.\" During global crises, international investors rush into them, temporarily boosting their value regardless of trade deficits."}
            ]),
            ("heading_1", "Is a stronger currency always better?"),
            ("paragraph", [
                {"text": "Not necessarily. A strong currency makes imported goods, electronics, and foreign travel cheaper for citizens. However, it also makes the country's domestic exports more expensive for foreign buyers, hurting local manufacturers and agricultural producers."}
            ]),
        ]
    },
    {
        "slug": "business/inflation",
        "label": "Inflation",
        "title": "Inflation",
        "type": "article",
        "description": "How the general rise in prices erodes purchasing power, what causes money to lose value, and how central banks manage it.",
        "cover_alt": "A shopping cart filled with fewer goods over time, illustrating the eroding purchasing power of money.",
        "sections": [
            ("heading_1", "What is inflation?"),
            ("paragraph", [
                {"text": "Inflation is the gradual, sustained increase in the general level of prices for goods and services across an economy over time. As prices rise, each unit of currency buys fewer goods than it did before: inflation is the erosion of money's purchasing power."}
            ]),
            ("heading_1", "What causes inflation?"),
            ("paragraph", [
                {"text": "Economists categorize inflation by its underlying triggers:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Demand-pull inflation", "bold": True},
                {"text": " — Occurs when consumer and business demand grows faster than the economy's capacity to produce goods. When \"too much money chases too few goods,\" sellers naturally raise prices."}
            ]),
            ("bulleted_list_item", [
                {"text": "Cost-push inflation", "bold": True},
                {"text": " — Occurs when the cost of essential production inputs—such as crude oil, raw materials, or shipping—spikes. Businesses pass these increased operating costs on to consumers in higher retail prices."}
            ]),
            ("bulleted_list_item", [
                {"text": "Money supply expansion", "bold": True},
                {"text": " — If a government or central bank increases the money supply significantly faster than the actual output of real goods and services, the value of each individual monetary unit inevitably falls."}
            ]),
            ("heading_1", "Winners and losers from inflation"),
            ("paragraph", [
                {"text": "Inflation does not affect everyone equally:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Borrowers win", "bold": True},
                {"text": " — If you borrowed money on a fixed interest rate, you repay the debt with future currency that has less purchasing power than when you borrowed it."}
            ]),
            ("bulleted_list_item", [
                {"text": "Savers and fixed-income earners lose", "bold": True},
                {"text": " — Cash stored in savings accounts earning low interest steadily loses real value, and pensioners living on fixed payments struggle as the cost of living escalates."}
            ]),
            ("heading_1", "How do central banks fight inflation?"),
            ("paragraph", [
                {"text": "Central banks use monetary policy to manage inflation, usually targeting a moderate annual rate around 2% to 4%. When inflation surges too high, central banks raise benchmark interest rates, making borrowing more expensive, cooling demand, and restoring price stability."}
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
        res = notion.databases.query(database_id=database_id, filter={"property": "Id", "title": {"equals": slug}})
        existing = res.get("results", [])
        if existing:
            page_id = existing[0]['id']
            print(f"Page already exists for slug '{slug}': {page_id}. Updating status to 'draft'...")
            notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {"select": {"name": "draft"}},
                    "Label": {"rich_text": [{"text": {"content": art["label"]}}]},
                    "Title": {"rich_text": [{"text": {"content": art["title"]}}]},
                    "JS": {"select": {"name": "0"}},
                    "Description": {"rich_text": [{"text": {"content": art["description"]}}]},
                }
            )
            continue

        print(f"Creating Notion page for '{slug}'...")
        page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Id": {"title": [{"text": {"content": slug}}]},
                "Status": {"select": {"name": "draft"}},
                "Label": {"rich_text": [{"text": {"content": art["label"]}}]},
                "Title": {"rich_text": [{"text": {"content": art["title"]}}]},
                "JS": {"select": {"name": "0"}},
                "Description": {"rich_text": [{"text": {"content": art["description"]}}]},
            },
            children=build_children(art)
        )
        print(f"Successfully created Notion page '{slug}' with ID: {page['id']}")

def update_business_hub():
    business_pid = '3dfbbfdb-4729-81b7-9d0b-f1350ee1b53d'
    blocks = notion.blocks.children.list(block_id=business_pid).get('results', [])
    for b in blocks:
        notion.blocks.delete(block_id=b['id'])

    topics = [
        ("Trade", "Why voluntary exchange creates mutual benefit and drives specialization."),
        ("Barter", "Direct exchange without money, and the frictions that led to currency."),
        ("Money", "A medium of exchange, unit of account, and store of value built on trust."),
        ("Plastic Money", "How payment cards and authorization networks replaced cash."),
        ("Digital Money", "Electronic ledgers, real-time settlement, and central bank currencies."),
        ("Debt", "Why money is fundamentally debt and how credit mobilizes future productivity."),
        ("Interest", "The price of time, opportunity cost, and default risk in borrowing."),
        ("Compound Interest", "Exponential growth from interest earning interest over time."),
        ("Stock", "Fractional ownership in a corporation, dividends, and residual claims."),
        ("Bond", "Debt securities, fixed interest coupons, and the yield seesaw."),
        ("Stock Exchange", "Order books, liquidity, and continuous public price discovery."),
        ("Hedging", "Offsetting risk and protecting core operations with derivatives."),
        ("Exchange Rate", "Why currencies differ in value, forex markets, and trade balances."),
        ("Inflation", "How the gradual rise in prices erodes purchasing power."),
        ("Startup", "Practical notes on starting, shaping, and presenting a company.")
    ]

    new_blocks = [
        {
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "\U0001f5bc\ufe0f"},
                "rich_text": [{"type": "text", "text": {"content": "Commerce, financial markets, currency, credit, and enterprise."}}]
            }
        },
        {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "Business notes covering commerce, currency, credit, financial instruments, capital markets, and entrepreneurship."}}]
            }
        },
        {
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "Topics"}}]
            }
        }
    ]

    for title, desc in topics:
        new_blocks.append({
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": title}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": f" — {desc}"}}
                ]
            }
        })

    new_blocks.extend([
        {
            "type": "divider",
            "divider": {}
        },
        {
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
        }
    ])

    notion.blocks.children.append(block_id=business_pid, children=new_blocks)
    print("Updated business hub with all 15 topics in Notion.")

if __name__ == "__main__":
    create_articles()
    update_business_hub()

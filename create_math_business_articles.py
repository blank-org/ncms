"""
Create canonical English articles in Notion for:
Mathematics:
  1. science/mathematics
  2. science/mathematics/axioms
  3. science/mathematics/proof
  4. science/mathematics/multiplication
  5. science/mathematics/zero
  6. science/mathematics/division_by_zero
Business:
  7. business/trade
  8. business/barter
  9. business/money
  10. business/debt
  11. business/interest
  12. business/compound_interest
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
    # -------------------------------------------------------------------------
    # MATHEMATICS
    # -------------------------------------------------------------------------
    {
        "slug": "science/mathematics",
        "label": "Mathematics",
        "title": "Mathematics",
        "type": "page",
        "description": "The abstract study of number, quantity, space and patterns, built on definitions, axioms and deductive proof.",
        "cover_alt": "Geometric forms, numeric sequences and intersecting logical planes.",
        "sections": [
            ("heading_1", "What is mathematics?"),
            ("paragraph", [
                {"text": "Mathematics is the study of numbers, structures, shapes and patterns through logical reasoning. Unlike the natural sciences, which test ideas against physical observations, mathematics begins with precise definitions and a small set of starting assumptions (axioms), deriving truths that follow with deductive certainty."}
            ]),
            ("heading_1", "How does it work?"),
            ("paragraph", [
                {"text": "Mathematical knowledge is cumulative. Once a statement is proven from accepted axioms, it becomes a permanent theorem. Future mathematicians do not need to re-prove it; they can cite it directly as a stepping stone to explore further. This unbroken chain of proof allows mathematics to build vast and intricate structures of verified knowledge."}
            ]),
            ("heading_1", "Why does it matter?"),
            ("paragraph", [
                {"text": "Mathematics provides the universal language for all rigorous thinking. Physics uses calculus to describe planetary orbits and quantum fields, computer science relies on discrete logic and boolean algebra to process information, and cryptography uses number theory to secure global communications."}
            ]),
            ("heading_1", "Topics"),
            ("bulleted_list_item", [
                {"text": "Axioms", "bold": True},
                {"text": " — The starting assumptions accepted without proof that define the rules of a mathematical system."}
            ]),
            ("bulleted_list_item", [
                {"text": "Proof", "bold": True},
                {"text": " — How rigorous deduction establishes permanent truths, where one proof builds on another."}
            ]),
            ("bulleted_list_item", [
                {"text": "Multiplication", "bold": True},
                {"text": " — How repeated addition expands into rectangular grids, area, and continuous scaling."}
            ]),
            ("bulleted_list_item", [
                {"text": "Zero", "bold": True},
                {"text": " — Why zero represents the absence of quantity, serves as an identity, and carries no unit."}
            ]),
            ("bulleted_list_item", [
                {"text": "Division by Zero", "bold": True},
                {"text": " — Why dividing by zero is undefined in arithmetic and what happens when approaching the boundary."}
            ]),
        ]
    },
    {
        "slug": "science/mathematics/axioms",
        "label": "Axioms",
        "title": "Mathematical Axioms",
        "type": "article",
        "description": "How foundational assumptions accepted without proof establish the starting ground for consistent mathematical systems.",
        "cover_alt": "A solid architectural foundation stone supporting interlocking pillars of logic.",
        "sections": [
            ("heading_1", "What is an axiom?"),
            ("paragraph", [
                {"text": "An axiom is a basic statement accepted as true without proof, serving as the starting premise for deriving further truths."}
            ]),
            ("paragraph", [
                {"text": "In any formal system, if you demand a proof for every claim, each proof requires prior statements, which in turn require earlier proofs. To avoid an infinite loop or circular reasoning, we must agree on where to begin. Axioms are that starting ground."}
            ]),
            ("heading_1", "The rules of chess analogy"),
            ("paragraph", [
                {"text": "Consider the rules of chess. We do not \"prove\" that a knight moves in an L-shape; that rule is not a discovery about the physical universe. It is simply an agreement. Once players accept that rule, an endless variety of games can unfold with complete logical consistency."}
            ]),
            ("paragraph", [
                {"text": "Axioms function in the exact same way. They define the playground. Mathematicians do not ask whether an axiom is \"physically real\"; they ask whether a set of axioms is consistent and what logical consequences flow from it."}
            ]),
            ("heading_1", "Classic examples"),
            ("paragraph", [
                {"text": "Two well-known axiom systems shape modern thought:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Euclid's postulates", "bold": True},
                {"text": " — Euclid founded classical geometry on five simple geometric assumptions, such as the statement that a straight line segment can be drawn between any two points."}
            ]),
            ("bulleted_list_item", [
                {"text": "The Peano axioms", "bold": True},
                {"text": " — Giuseppe Peano defined arithmetic on natural numbers using a few minimalist rules about zero and the concept of a successor number."}
            ]),
            ("heading_1", "What happens when you change an axiom?"),
            ("paragraph", [
                {"text": "Changing an axiom does not break mathematics; it creates a new system."}
            ]),
            ("paragraph", [
                {"text": "For two thousand years, mathematicians tried to prove Euclid's fifth axiom—the parallel postulate—from his other four. In the nineteenth century, mathematicians asked: what if parallel lines can diverge or converge? By replacing that single assumption, they discovered non-Euclidean geometries. Decades later, Albert Einstein used those very geometries to formulate general relativity, showing that space and time are physically curved by gravity."}
            ]),
        ]
    },
    {
        "slug": "science/mathematics/proof",
        "label": "Proof",
        "title": "Mathematical Proof",
        "type": "article",
        "description": "How rigorous logical deduction establishes permanent truths, and how each proven result becomes the foundation for future proofs.",
        "cover_alt": "Interlocking stepping stones forming an ascending staircase of deductive reasoning.",
        "sections": [
            ("heading_1", "What is a mathematical proof?"),
            ("paragraph", [
                {"text": "A mathematical proof is an unbroken chain of logical deductions showing that if certain axioms and definitions are true, a specific conclusion must inevitably follow."}
            ]),
            ("heading_1", "How is one proof used for another?"),
            ("paragraph", [
                {"text": "Mathematics is built like a scaffold. Mathematicians do not return to primary axioms every time they solve a new problem. Once a statement is rigorously proven, it becomes an established theorem. From that moment on, anyone can cite it as a single verified step inside a larger proof."}
            ]),
            ("paragraph", [
                {"text": "Mathematicians organize these stepping stones into clear roles:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Lemma", "bold": True},
                {"text": " — A smaller, preliminary result proven specifically to help prove a larger theorem."}
            ]),
            ("bulleted_list_item", [
                {"text": "Theorem", "bold": True},
                {"text": " — A major, significant mathematical statement established by proof."}
            ]),
            ("bulleted_list_item", [
                {"text": "Corollary", "bold": True},
                {"text": " — An immediate consequence that follows effortlessly from an already proven theorem."}
            ]),
            ("heading_1", "The Pythagorean stepping stone"),
            ("paragraph", [
                {"text": "Consider the Pythagorean theorem ("},
                {"text": "a² + b² = c²", "bold": True},
                {"text": "). Once proven, it is no longer just a curious fact about right-angled triangles. It is used to prove distance formulas on Cartesian grids, which are used to prove trigonometric identities, which are used to prove theorems in calculus and Fourier analysis."}
            ]),
            ("paragraph", [
                {"text": "A single proof from ancient Greece remains a load-bearing beam in modern GPS navigation, satellite orbits, and 3D computer graphics engines."}
            ]),
            ("heading_1", "Proof versus scientific evidence"),
            ("paragraph", [
                {"text": "In natural science, evidence is inductive and provisional. Even if a theory has been tested a million times, a new observation tomorrow can refine or overturn it."}
            ]),
            ("paragraph", [
                {"text": "In mathematics, truth is deductive. Once a theorem is proven from consistent axioms, it remains true for all time. No future observation will ever make the square root of two a rational number, or find a largest prime number."}
            ]),
        ]
    },
    {
        "slug": "science/mathematics/multiplication",
        "label": "Multiplication",
        "title": "Multiplication",
        "type": "article",
        "description": "How multiplication begins as applied addition, expands into rectangular grids and area, and scales continuous quantities.",
        "cover_alt": "A neat rectangular grid of identical elements illustrating repeated groups and area scaling.",
        "sections": [
            ("heading_1", "What is multiplication?"),
            ("paragraph", [
                {"text": "At its root, multiplication is applied addition: adding the same quantity repeatedly. Writing "},
                {"text": "3 × 4", "bold": True},
                {"text": " means taking 4 and adding it 3 times: "},
                {"text": "4 + 4 + 4 = 12", "bold": True},
                {"text": "."}
            ]),
            ("heading_1", "From repeated addition to grids and area"),
            ("paragraph", [
                {"text": "When you arrange items in rows and columns—like eggs in a carton or trees in an orchard—multiplication becomes geometric. A tray with 3 rows of 4 eggs contains 12 eggs."}
            ]),
            ("paragraph", [
                {"text": "If you rotate the tray a quarter turn, you now have 4 rows of 3 eggs. The total count does not change. This simple rotation provides an immediate visual proof of "},
                {"text": "commutativity", "bold": True},
                {"text": ":"}
            ]),
            ("paragraph", [
                {"text": "a × b = b × a", "bold": True}
            ]),
            ("paragraph", [
                {"text": "Multiplication naturally bridges one-dimensional counting to two-dimensional geometry: multiplying two lengths gives an area."}
            ]),
            ("heading_1", "Scaling and continuous quantities"),
            ("paragraph", [
                {"text": "Repeated addition works well for whole numbers, but multiplication extends far beyond discrete counting. Multiplying by 2.5 or 0.5 means scaling: stretching or shrinking a quantity continuously."}
            ]),
            ("paragraph", [
                {"text": "When you adjust the volume slider on an audio amplifier or resize a photograph on a screen, you are multiplying signal amplitudes and pixel coordinates. Multiplication transforms one scale into another."}
            ]),
            ("heading_1", "Why does it matter?"),
            ("paragraph", [
                {"text": "Multiplication allows us to calculate compound rates and multi-dimensional quantities efficiently. Calculating kinetic energy, electrical power, or mortgage amortization without multiplication would require an impractical amount of manual addition."}
            ]),
        ]
    },
    {
        "slug": "science/mathematics/zero",
        "label": "Zero",
        "title": "Zero",
        "type": "article",
        "description": "Why zero is both an identity element and a positional placeholder, and why pure zero carries no physical unit.",
        "cover_alt": "A clean circular ring balancing positive and negative coordinate axes at the origin.",
        "sections": [
            ("heading_1", "What is zero?"),
            ("paragraph", [
                {"text": "Zero is the number representing the absence of quantity. In arithmetic, it serves as the additive identity: adding zero to any number leaves that number unchanged ("},
                {"text": "x + 0 = x", "bold": True},
                {"text": ")."}
            ]),
            ("heading_1", "Why does zero have no unit?"),
            ("paragraph", [
                {"text": "When you count physical things, numbers normally attach to units: 5 apples, 10 metres, or 3 seconds. But consider what happens when there are none. Zero apples, zero metres, and zero seconds all describe the exact same mathematical state: an empty set."}
            ]),
            ("paragraph", [
                {"text": "Units exist to give scale and meaning to positive and negative magnitudes. Zero is the origin—the neutral baseline from which measurement begins. Because pure zero represents the complete absence of magnitude, it does not inherit physical dimensions."}
            ]),
            ("heading_1", "The dual nature of zero"),
            ("paragraph", [
                {"text": "Throughout mathematical history, zero had to be conceived in two distinct roles:"}
            ]),
            ("bulleted_list_item", [
                {"text": "As a positional placeholder", "bold": True},
                {"text": " — In place-value number systems, zero marks an empty power of ten so we can distinguish 15, 105, and 1005."}
            ]),
            ("bulleted_list_item", [
                {"text": "As a number in its own right", "bold": True},
                {"text": " — An algebraic entity that can be added, subtracted, and multiplied just like any positive or negative integer."}
            ]),
            ("heading_1", "Algebraic behaviour"),
            ("paragraph", [
                {"text": "Zero behaves uniquely across operations. While it is completely neutral in addition, it is the absorbing element in multiplication: any number multiplied by zero becomes zero ("},
                {"text": "x × 0 = 0", "bold": True},
                {"text": ")."}
            ]),
            ("paragraph", [
                {"text": "This property yields the "},
                {"text": "zero-product rule", "bold": True},
                {"text": ": if "},
                {"text": "a × b = 0", "bold": True},
                {"text": ", then at least one of "},
                {"text": "a", "bold": True},
                {"text": " or "},
                {"text": "b", "bold": True},
                {"text": " must be zero. This simple insight is one of the most fundamental tools in solving algebraic equations."}
            ]),
        ]
    },
    {
        "slug": "science/mathematics/division_by_zero",
        "label": "Division by Zero",
        "title": "Division by Zero",
        "type": "article",
        "description": "Why dividing by zero is undefined in arithmetic, what breaks when we attempt it, and how calculus approaches the boundary.",
        "cover_alt": "A hyperbolic curve splitting dramatically toward positive and negative infinity near the vertical axis.",
        "sections": [
            ("heading_1", "What is division by zero?"),
            ("paragraph", [
                {"text": "In standard arithmetic, division by zero is undefined. It does not produce infinity, nor does it equal zero; it simply has no valid mathematical answer."}
            ]),
            ("heading_1", "Division as inverse multiplication"),
            ("paragraph", [
                {"text": "To see why division by zero fails, consider what division actually means. The expression "},
                {"text": "a / b = c", "bold": True},
                {"text": " asks: find a unique number "},
                {"text": "c", "bold": True},
                {"text": " such that "},
                {"text": "c × b = a", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "Now attempt to divide a non-zero number by zero, say "},
                {"text": "5 / 0 = c", "bold": True},
                {"text": ". This requires finding a number "},
                {"text": "c", "bold": True},
                {"text": " such that:"}
            ]),
            ("paragraph", [
                {"text": "c × 0 = 5", "bold": True}
            ]),
            ("paragraph", [
                {"text": "Because any number multiplied by zero equals zero, no such number "},
                {"text": "c", "bold": True},
                {"text": " can ever exist."}
            ]),
            ("paragraph", [
                {"text": "What about dividing zero by zero ("},
                {"text": "0 / 0 = c", "bold": True},
                {"text": ")? That requires "},
                {"text": "c × 0 = 0", "bold": True},
                {"text": ". Here the problem reverses: every single number satisfies the equation. Whether "},
                {"text": "c", "bold": True},
                {"text": " is 1, 42, or -7, the statement is true. Because there is no single, well-defined answer, "},
                {"text": "0 / 0", "bold": True},
                {"text": " is indeterminate."}
            ]),
            ("heading_1", "Division as repeated subtraction"),
            ("paragraph", [
                {"text": "Another intuitive way to view division is repeated subtraction. Dividing 12 by 3 asks: how many times can you subtract 3 from 12 until nothing remains? The answer is 4 times."}
            ]),
            ("paragraph", [
                {"text": "Now try dividing 12 by 0. You subtract 0, leaving 12. You subtract 0 again, still leaving 12. You can subtract forever and you will never make any progress toward zero. The process never terminates."}
            ]),
            ("heading_1", "What happens when you approach zero?"),
            ("paragraph", [
                {"text": "In calculus, we can examine what happens as the divisor becomes infinitesimally close to zero without reaching it."}
            ]),
            ("paragraph", [
                {"text": "If you divide 1 by positive numbers approaching zero (0.1, 0.01, 0.0001), the quotient grows without bound toward positive infinity (+∞). But if you approach zero from negative numbers (-0.1, -0.01, -0.0001), the quotient plunges toward negative infinity (-∞)."}
            ]),
            ("paragraph", [
                {"text": "Because approaching zero from the left and right leads in opposite directions, division by zero cannot be assigned a single consistent value."}
            ]),
        ]
    },

    # -------------------------------------------------------------------------
    # BUSINESS
    # -------------------------------------------------------------------------
    {
        "slug": "business/trade",
        "label": "Trade",
        "title": "Trade",
        "type": "article",
        "description": "Why voluntary exchange creates mutual benefit, drives specialization, and forms the basis of commerce.",
        "cover_alt": "Merchants exchanging goods across trade routes and commercial ports.",
        "sections": [
            ("heading_1", "What is trade?"),
            ("paragraph", [
                {"text": "Trade is the voluntary exchange of goods, services, or money between two or more parties."}
            ]),
            ("paragraph", [
                {"text": "Because each party only agrees to a voluntary trade if they value what they receive more than what they give up, trade creates mutual benefit. It is not a zero-sum game where one person wins only if another loses; it creates new value for both sides."}
            ]),
            ("heading_1", "Why do people trade?"),
            ("paragraph", [
                {"text": "No single individual, town, or nation can produce everything needed efficiently. Trade allows people to specialize in what they do best: a farmer grows crops, a carpenter builds furniture, and a programmer writes software. By exchanging their surpluses, everyone enjoys a wider variety and higher quality of goods than if each tried to be completely self-sufficient."}
            ]),
            ("heading_1", "Comparative advantage"),
            ("paragraph", [
                {"text": "Even if one person or country is better at producing everything than another, trade still benefits both. By concentrating effort on the activity where their relative efficiency is highest (their comparative advantage) and trading for the rest, the total productive output of the whole system increases."}
            ]),
            ("heading_1", "From local markets to global networks"),
            ("paragraph", [
                {"text": "Trade began as face-to-face exchanges in village squares. Over centuries, trade routes, shipping containers, and digital networks transformed commerce into interconnected global supply chains, allowing resources, technology, and products to move wherever they are needed most."}
            ]),
        ]
    },
    {
        "slug": "business/barter",
        "label": "Barter",
        "title": "Barter",
        "type": "article",
        "description": "How direct exchange operates without money, and the severe frictions that led societies to create currency.",
        "cover_alt": "Two people directly trading agricultural goods for handcrafted pottery.",
        "sections": [
            ("heading_1", "What is barter?"),
            ("paragraph", [
                {"text": "Barter is a system of exchange where goods or services are directly traded for other goods or services without using a medium of exchange such as money."}
            ]),
            ("heading_1", "The double coincidence of wants"),
            ("paragraph", [
                {"text": "The greatest structural problem with barter is the "},
                {"text": "double coincidence of wants", "bold": True},
                {"text": ". For a trade to occur, person A must want exactly what person B has, and person B must want exactly what person A has, at the exact same time and in compatible quantities."}
            ]),
            ("paragraph", [
                {"text": "If a farmer has extra wheat and needs a pair of boots, they must find a cobbler who happens to need wheat right now. If the cobbler already has plenty of wheat, no trade can happen until the farmer trades wheat for something else the cobbler wants."}
            ]),
            ("heading_1", "Other limits of barter"),
            ("paragraph", [
                {"text": "Beyond the coincidence of wants, direct barter suffers from three major hurdles:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Indivisibility", "bold": True},
                {"text": " — You cannot cut a cow or a horse in half to buy a small basket of vegetables without destroying the animal's value."}
            ]),
            ("bulleted_list_item", [
                {"text": "Perishability", "bold": True},
                {"text": " — Fresh milk, fish, or fruit spoil quickly, making it impossible to store wealth for future trades."}
            ]),
            ("bulleted_list_item", [
                {"text": "Pricing complexity", "bold": True},
                {"text": " — In an economy with 100 goods, a barter system requires tracking thousands of individual exchange ratios between every possible pair of items."}
            ]),
            ("paragraph", [
                {"text": "These frictions naturally drove human societies to converge on universally accepted intermediate commodities, giving rise to money."}
            ]),
        ]
    },
    {
        "slug": "business/money",
        "label": "Money",
        "title": "Money",
        "type": "article",
        "description": "What makes an object or ledger entry money, how it solves barter frictions, and why trust is its true foundation.",
        "cover_alt": "Historic coins, paper currency, and digital ledger nodes tracing the evolution of money.",
        "sections": [
            ("heading_1", "What is money?"),
            ("paragraph", [
                {"text": "Money is anything that is universally accepted as payment for goods and services, or in the settlement of debts. It is not necessarily gold, silver, or paper; it is fundamentally an accounting system based on social trust."}
            ]),
            ("heading_1", "The three functions of money"),
            ("paragraph", [
                {"text": "To serve as money, an asset must perform three distinct roles:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Medium of exchange", "bold": True},
                {"text": " — It eliminates the double coincidence of wants by being accepted by everyone in trade."}
            ]),
            ("bulleted_list_item", [
                {"text": "Unit of account", "bold": True},
                {"text": " — It provides a common measurement scale so that the price and value of completely different goods can be directly compared."}
            ]),
            ("bulleted_list_item", [
                {"text": "Store of value", "bold": True},
                {"text": " — It allows people to save purchasing power earned today and spend it weeks, months, or years later."}
            ]),
            ("heading_1", "From commodities to digital ledgers"),
            ("paragraph", [
                {"text": "Money has evolved through three major stages:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Commodity money", "bold": True},
                {"text": " — Goods with intrinsic utility or durability, such as salt, cowrie shells, silver, and gold."}
            ]),
            ("bulleted_list_item", [
                {"text": "Representative money", "bold": True},
                {"text": " — Paper certificates issued by merchants, goldsmiths, or banks, promising to deliver a fixed weight of gold or silver on demand."}
            ]),
            ("bulleted_list_item", [
                {"text": "Fiat and digital money", "bold": True},
                {"text": " — Currency backed not by physical commodities, but by government decree and widespread public trust. Today, the vast majority of money exists solely as digital entries in banking ledgers."}
            ]),
            ("heading_1", "Why does money have value?"),
            ("paragraph", [
                {"text": "A piece of paper or a number on a smartphone screen has virtually no intrinsic physical value. It works because everyone in a society shares the collective confidence that others will accept it tomorrow for real food, housing, and labour."}
            ]),
        ]
    },
    {
        "slug": "business/debt",
        "label": "Debt",
        "title": "Debt",
        "type": "article",
        "description": "Why money is fundamentally debt, how credit pulls future productivity into the present, and how ledgers record social obligations.",
        "cover_alt": "A balance ledger recording credits and debits connecting lenders and borrowers.",
        "sections": [
            ("heading_1", "What is debt?"),
            ("paragraph", [
                {"text": "Debt is an obligation where one party (the borrower) receives resources today and commits to repaying the lender at a specified future date, typically with interest."}
            ]),
            ("heading_1", "Money is fundamentally debt"),
            ("paragraph", [
                {"text": "A common misconception is that physical money was invented first, and debt came later as a way to borrow money. Historical and anthropological evidence shows the opposite: credit and debt systems existed long before physical coinage was minted."}
            ]),
            ("paragraph", [
                {"text": "Ancient Mesopotamian temples and agrarian villages recorded mutual debts and obligations on clay tablets thousands of years ago. The ledger of mutual credit was the medium of exchange."}
            ]),
            ("paragraph", [
                {"text": "In modern financial systems, this principle remains completely true:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Paper banknotes are central bank debt", "bold": True},
                {"text": " — A currency note is legally a non-interest-bearing liability of the central bank."}
            ]),
            ("bulleted_list_item", [
                {"text": "Bank deposits are commercial bank debt", "bold": True},
                {"text": " — Money in a bank account is not a vault of cash; it is an IOU from the bank promising to pay you on demand."}
            ]),
            ("bulleted_list_item", [
                {"text": "Money is created through lending", "bold": True},
                {"text": " — When a commercial bank issues a mortgage or business loan, it does not lend out pre-existing cash deposited by others. It writes a new deposit into the borrower's account, creating new purchasing power against an asset (the borrower's promise to repay)."}
            ]),
            ("heading_1", "Why does debt matter?"),
            ("paragraph", [
                {"text": "Debt allows society to pull future productive capacity into the present. An entrepreneur with an innovative idea but no capital can borrow funds to construct a factory today. The wealth generated by that factory over time pays off the loan."}
            ]),
            ("paragraph", [
                {"text": "Without credit, economic development would be limited to individuals who already have accumulated savings."}
            ]),
            ("heading_1", "The risk of debt"),
            ("paragraph", [
                {"text": "When debt expands faster than real productivity, borrowers cannot generate enough income to service their obligations. When defaults multiply across an economy, credit contracts, banks fail, and economic recessions follow."}
            ]),
        ]
    },
    {
        "slug": "business/interest",
        "label": "Interest",
        "title": "Interest",
        "type": "article",
        "description": "How interest acts as the price of time and risk, balancing deferred consumption with capital productivity.",
        "cover_alt": "An hourglass beside an accumulating balance, symbolising the price of time in finance.",
        "sections": [
            ("heading_1", "What is interest?"),
            ("paragraph", [
                {"text": "Interest is the fee paid by a borrower to a lender for the use of money over time, expressed as a percentage of the borrowed amount (the principal)."}
            ]),
            ("heading_1", "Why does interest exist?"),
            ("paragraph", [
                {"text": "Interest is the market price of time and risk, reflecting four economic realities:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Time preference", "bold": True},
                {"text": " — People naturally prefer having goods and resources now rather than later. When a lender lends money, they postpone their own consumption. Interest compensates them for waiting."}
            ]),
            ("bulleted_list_item", [
                {"text": "Opportunity cost", "bold": True},
                {"text": " — While the money is in the borrower's hands, the lender cannot use it for other profitable investments, such as starting a business or purchasing property."}
            ]),
            ("bulleted_list_item", [
                {"text": "Default risk", "bold": True},
                {"text": " — There is always a possibility that the borrower will be unable to repay the loan. Part of the interest rate is an insurance premium against loss."}
            ]),
            ("bulleted_list_item", [
                {"text": "Inflation", "bold": True},
                {"text": " — As prices rise over time, the purchasing power of money decreases. Interest ensures the lender is not repaid with currency that buys less than what was originally lent."}
            ]),
            ("heading_1", "Simple interest"),
            ("paragraph", [
                {"text": "Simple interest is calculated strictly on the original principal:"}
            ]),
            ("paragraph", [
                {"text": "Interest = Principal × Rate × Time", "bold": True}
            ]),
            ("paragraph", [
                {"text": "If you borrow ₹10,000 at 5% simple annual interest for 3 years, you pay ₹500 each year, totalling ₹1,500 in interest. The principal balance remains constant."}
            ]),
        ]
    },
    {
        "slug": "business/compound_interest",
        "label": "Compound Interest",
        "title": "Compound Interest",
        "type": "article",
        "description": "How interest earning interest creates exponential growth over time, rewarding early savings and punishing long-term debt.",
        "cover_alt": "An exponential curve climbing steadily upwards, visualising the compounding growth of reinvested gains.",
        "sections": [
            ("heading_1", "What is compound interest?"),
            ("paragraph", [
                {"text": "Compound interest is interest calculated on both the initial principal and the accumulated interest from previous periods. In everyday terms, it is \"interest on interest.\""}
            ]),
            ("heading_1", "How does compounding work?"),
            ("paragraph", [
                {"text": "In simple interest, your earnings stay constant every year. In compound interest, each year's interest is added back to the principal, so the base on which future interest is calculated grows larger each cycle."}
            ]),
            ("paragraph", [
                {"text": "If you invest ₹10,000 at 10% annual compound interest:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Year 1", "bold": True},
                {"text": " — 10% on ₹10,000 = ₹1,000. New balance: ₹11,000."}
            ]),
            ("bulleted_list_item", [
                {"text": "Year 2", "bold": True},
                {"text": " — 10% on ₹11,000 = ₹1,100. New balance: ₹12,100."}
            ]),
            ("bulleted_list_item", [
                {"text": "Year 3", "bold": True},
                {"text": " — 10% on ₹12,100 = ₹1,210. New balance: ₹13,310."}
            ]),
            ("paragraph", [
                {"text": "The standard formula for the final amount is:"}
            ]),
            ("paragraph", [
                {"text": "A = P (1 + r / n)^(n t)", "bold": True}
            ]),
            ("paragraph", [
                {"text": "where P is principal, r is the annual interest rate, n is the number of times interest compounds per year, and t is time in years."}
            ]),
            ("heading_1", "The snowball of time"),
            ("paragraph", [
                {"text": "Over short periods, compounding looks almost identical to simple interest. But because the growth rate multiplies itself, compounding produces an exponential curve that bends steeply upward over decades."}
            ]),
            ("paragraph", [
                {"text": "Eventually, the interest generated each year dwarfs the original principal. This makes time the single most critical factor in investing: starting early with modest amounts produces far more wealth than starting late with large sums."}
            ]),
            ("heading_1", "The double-edged sword"),
            ("paragraph", [
                {"text": "Compound interest works with equal force in both directions. When you save and invest, it accelerates your wealth. But when you carry revolving high-interest debt, compounding multiplies what you owe, turning small unpaid balances into overwhelming liabilities."}
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

def create_or_update_articles():
    for art in ARTICLES:
        slug = art["slug"]
        res = notion.databases.query(database_id=database_id, filter={"property": "Id", "title": {"equals": slug}})
        existing = res.get("results", [])
        if existing:
            page_id = existing[0]['id']
            print(f"Page already exists for slug '{slug}': {page_id}. Updating properties and status to 'draft'...")
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

if __name__ == "__main__":
    create_or_update_articles()

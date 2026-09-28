"""
Script to create the 7 requested canonical English articles in Notion:
1. science/physics/electrical/circuit
2. science/physics/electrical/kirchhoffs_laws
3. science/physics/electromagnetism/coulombs_law
4. science/physics/electromagnetism/faradays_law
5. science/physics/electromagnetism/lenzs_law
6. science/physics/quantum_physics/photoelectric_effect
7. technology/computer/artificial_intelligence/machine_learning/models/llm/flow_architecture
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
        "slug": "science/physics/electrical/circuit",
        "label": "Circuit",
        "title": "Electric Circuit",
        "description": "How closed conductive paths allow continuous charge flow, transfer electrical energy, and form working systems.",
        "cover_alt": "A closed loop connecting an electrical energy source, conductors and a load.",
        "sections": [
            ("heading_1", "What is an electric circuit?"),
            ("paragraph", [
                {"text": "An electric circuit is an unbroken conductive loop that allows electric charge to flow continuously from a power source, through one or more components, and back to the source."}
            ]),
            ("paragraph", [
                {"text": "If the loop is broken at any point, charges cannot complete the path, the electric field collapses, and current stops everywhere along that branch."}
            ]),
            ("heading_1", "What does a circuit need to work?"),
            ("paragraph", [
                {"text": "Every functional circuit requires at least three essential elements:"}
            ]),
            ("bulleted_list_item", [
                {"text": "A source of electromotive force", "bold": True},
                {"text": ": a battery, generator, or solar cell that maintains an electrical potential difference (voltage) across its terminals."}
            ]),
            ("bulleted_list_item", [
                {"text": "A conductive path", "bold": True},
                {"text": ": copper wires, printed circuit board traces, or metallic tracks that provide mobile charge carriers with low resistance."}
            ]),
            ("bulleted_list_item", [
                {"text": "A load", "bold": True},
                {"text": ": a component such as a resistor, lamp, heating element, or motor that converts electrical energy into heat, light, or mechanical work."}
            ]),
            ("paragraph", [
                {"text": "Most practical circuits also incorporate a switch or control element to open and close the conductive loop safely without disconnecting wires."}
            ]),
            ("heading_1", "Closed, open, and short circuits"),
            ("paragraph", [
                {"text": "When a circuit is operating normally, it is a "},
                {"text": "closed circuit", "bold": True},
                {"text": ": charges circulate steadily, potential drops across the load, and energy transfers smoothly from the source to the load."}
            ]),
            ("paragraph", [
                {"text": "When a connection is severed or a switch is turned off, it becomes an "},
                {"text": "open circuit", "bold": True},
                {"text": ". Air has extremely high resistance, so current drops to zero immediately, even though the power source continues to maintain voltage across the gap."}
            ]),
            ("paragraph", [
                {"text": "A "},
                {"text": "short circuit", "bold": True},
                {"text": " occurs when an unintended low-resistance connection bypasses the load entirely. Because circuit resistance plunges close to zero, Ohm's law ("},
                {"text": "I = V / R", "bold": True},
                {"text": ") dictates that current surges to dangerous levels, melting insulation, blowing fuses, or starting electrical fires."}
            ]),
            ("heading_1", "Series and parallel connections"),
            ("paragraph", [
                {"text": "Components connect together in two fundamental configurations:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Series circuits", "bold": True},
                {"text": ": components are arranged along a single continuous path. The identical current flows through each component sequentially, while the total supply voltage divides across them. If any single component fails or disconnects, the entire loop opens and all components turn off."}
            ]),
            ("bulleted_list_item", [
                {"text": "Parallel circuits", "bold": True},
                {"text": ": components connect across shared common junctions. Every branch experiences the full source voltage, while total current divides among the branches according to their individual resistance. If one branch is disconnected, all other branches continue operating without interruption."}
            ]),
            ("paragraph", [
                {"text": "Household electrical wiring is wired almost exclusively in parallel so that switching off a desk lamp does not shut down the computer or the refrigerator."}
            ]),
            ("heading_1", "How is electrical energy actually transferred?"),
            ("paragraph", [
                {"text": "It is tempting to imagine electrons marching like marbles through a pipe from the battery to the load, but individual electrons drift through metallic conductors at less than a millimetre per second."}
            ]),
            ("paragraph", [
                {"text": "Energy does not travel through the slow mechanical motion of individual particles. It travels through the electromagnetic field established in the space surrounding the conductors. The field forms along the loop at nearly the speed of light, exerting force on charges throughout the entire circuit almost instantaneously."}
            ]),
        ]
    },
    {
        "slug": "science/physics/electrical/kirchhoffs_laws",
        "label": "Kirchhoff's Laws",
        "title": "Kirchhoff's Laws",
        "description": "How conservation of charge at nodes and conservation of energy around loops allow complete circuit analysis.",
        "cover_alt": "Currents meeting at a circuit junction and voltages balancing around a closed loop.",
        "sections": [
            ("heading_1", "What are Kirchhoff's laws?"),
            ("paragraph", [
                {"text": "Kirchhoff's laws are two fundamental principles that govern how electric current and voltage behave across any electrical network."}
            ]),
            ("paragraph", [
                {"text": "Formulated by German physicist Gustav Kirchhoff in 1845, they generalize Ohm's law to handle complex multi-loop circuits with multiple power sources and branching junctions."}
            ]),
            ("heading_1", "Kirchhoff's Current Law (The Junction Rule)"),
            ("paragraph", [
                {"text": "Kirchhoff's Current Law (KCL) states that the total current entering any electrical junction (or node) must equal the total current leaving that junction: "},
                {"text": "∑ I_in = ∑ I_out", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "This rule is a direct physical expression of the conservation of electric charge. Electric charge cannot accumulate or vanish into thin air at a wire joint. Whatever charge arrives at a junction during any interval must depart through the connected branches."}
            ]),
            ("paragraph", [
                {"text": "If 5 amperes flow into a junction and 2 amperes exit through one branch, exactly 3 amperes must exit through the remaining branch."}
            ]),
            ("heading_1", "Kirchhoff's Voltage Law (The Loop Rule)"),
            ("paragraph", [
                {"text": "Kirchhoff's Voltage Law (KVL) states that the algebraic sum of all potential differences (voltages) around any closed loop in a circuit must equal zero: "},
                {"text": "∑ V = 0", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "This rule reflects the conservation of energy. Electric potential measures potential energy per unit charge. If you begin at any point in a circuit, follow a complete closed path through batteries and components, and return to your starting position, your net change in electrical potential energy must be zero."}
            ]),
            ("paragraph", [
                {"text": "Gaining voltage across a battery is like climbing a hill; losing voltage across a resistor is like walking back down. By the time you complete the round trip, the gains and drops cancel out completely."}
            ]),
            ("heading_1", "Why are they necessary beyond Ohm's law?"),
            ("paragraph", [
                {"text": "Ohm's law ("},
                {"text": "V = I R", "bold": True},
                {"text": ") describes the relationship across a single resistive component. However, practical circuits—such as electrical distribution grids, Wheatstone bridges, and multi-transistor amplifiers—contain cross-linked loops and multiple interacting voltage sources where simple series or parallel reductions cannot work."}
            ]),
            ("paragraph", [
                {"text": "Kirchhoff's laws transform any complicated circuit into a solvable system of linear equations that directly yields every branch current and node potential."}
            ]),
            ("heading_1", "How to apply them in practice"),
            ("paragraph", [
                {"text": "Applying Kirchhoff's laws systematically involves three basic steps:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Identify nodes and loops", "bold": True},
                {"text": ": find all junctions where three or more conductors meet, and select enough independent closed loops to cover all circuit branches."}
            ]),
            ("bulleted_list_item", [
                {"text": "Assign reference directions", "bold": True},
                {"text": ": label each branch current with an assumed arrow direction. If your algebraic solution produces a negative current, it simply means the true current flows opposite to your initial guess."}
            ]),
            ("bulleted_list_item", [
                {"text": "Maintain consistent loop signs", "bold": True},
                {"text": ": traverse each chosen loop in one direction (clockwise or counter-clockwise). Treat potential rises across power sources as positive and potential drops across resistors (traversed in the direction of current) as negative."}
            ]),
        ]
    },
    {
        "slug": "science/physics/electromagnetism/coulombs_law",
        "label": "Coulomb's Law",
        "title": "Coulomb's Law",
        "description": "How stationary electric charges attract or repel with a force inversely proportional to the square of their distance.",
        "cover_alt": "Two point charges exerting equal and opposite electrostatic forces along the line between them.",
        "sections": [
            ("heading_1", "What is Coulomb's law?"),
            ("paragraph", [
                {"text": "Coulomb's law is the physical law that quantifies the electrostatic force of attraction or repulsion between two stationary, electrically charged particles."}
            ]),
            ("paragraph", [
                {"text": "Formulated experimentally by French physicist Charles-Augustin de Coulomb in 1785 using a sensitive torsion balance, the law states: "},
                {"text": "F = k_e (|q₁ q₂| / r²)", "bold": True},
                {"text": ", where q₁ and q₂ are the quantities of charge, r is the separation distance between them, and k_e is Coulomb's constant."}
            ]),
            ("heading_1", "How does the electrostatic force behave?"),
            ("paragraph", [
                {"text": "The electrostatic force follows three straightforward physical rules:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Like charges repel", "bold": True},
                {"text": ": two positive charges or two negative charges exert mutually repulsive forces that push them apart."}
            ]),
            ("bulleted_list_item", [
                {"text": "Opposite charges attract", "bold": True},
                {"text": ": a positive charge and a negative charge exert attractive forces that pull them toward each other."}
            ]),
            ("bulleted_list_item", [
                {"text": "Inverse-square drop", "bold": True},
                {"text": ": the force weakens rapidly with distance. Doubling the distance between two charges slashes the force to one-quarter; tripling the distance reduces it to one-ninth."}
            ]),
            ("paragraph", [
                {"text": "By Newton's third law of motion, the force that charge 1 exerts on charge 2 is strictly equal in magnitude and opposite in direction to the force that charge 2 exerts on charge 1, regardless of which charge is larger."}
            ]),
            ("heading_1", "The medium and the electric constant"),
            ("paragraph", [
                {"text": "In a vacuum, Coulomb's constant has the value "},
                {"text": "k_e ≈ 8.988 × 10⁹ N·m²/C²", "bold": True},
                {"text": ". It is frequently written in terms of the permittivity of free space (ε₀) as "},
                {"text": "k_e = 1 / (4πε₀)", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "When charges are placed inside an insulating material medium—such as water, oil, or glass—the molecules of the medium polarize, setting up an opposing internal field that shields the charges from one another. This reduces the effective electrostatic attraction by the material's relative permittivity (dielectric constant). In water, the force drops to roughly one-eightieth of its vacuum strength, which is why water dissolves ionic salts so readily."}
            ]),
            ("heading_1", "From point charges to electric fields"),
            ("paragraph", [
                {"text": "Coulomb's law describes an interaction between separated objects across empty space. To understand how that force transmits, physics defines the concept of the "},
                {"text": "electric field", "bold": True},
                {"text": ": any charge creates an electric field in the space surrounding itself, and a second charge experiences a force directly from the local field at its own location: "},
                {"text": "E = F / q", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "Summing the Coulomb forces produced by continuous charge distributions leads directly to Gauss's law—the first of Maxwell's four equations that form the foundation of classical electromagnetism."}
            ]),
            ("heading_1", "Limits of the law"),
            ("paragraph", [
                {"text": "Coulomb's law holds strictly for point charges that are stationary relative to one another."}
            ]),
            ("paragraph", [
                {"text": "When charges move, they generate magnetic fields in addition to electric fields. Furthermore, disturbances in the electromagnetic field travel at the finite speed of light rather than acting instantaneously across space. In dynamic systems, electrostatic force must be expanded into the complete Lorentz force and Maxwell's equations."}
            ]),
        ]
    },
    {
        "slug": "science/physics/electromagnetism/faradays_law",
        "label": "Faraday's Law",
        "title": "Faraday's Law",
        "description": "How changing magnetic flux induces an electromotive force, linking magnetic fields directly to electricity.",
        "cover_alt": "A magnet moving through a wire coil inducing an electric current.",
        "sections": [
            ("heading_1", "What is Faraday's law of induction?"),
            ("paragraph", [
                {"text": "Faraday's law of induction states that whenever the magnetic flux passing through a conductive loop changes over time, an electromotive force (voltage) is induced in that loop."}
            ]),
            ("paragraph", [
                {"text": "Discovered by English scientist Michael Faraday in 1831, it demonstrated that electricity and magnetism are not independent forces, but two sides of a single physical interaction: a changing magnetic field actively creates an electric field."}
            ]),
            ("heading_1", "What is magnetic flux?"),
            ("paragraph", [
                {"text": "Magnetic flux ("},
                {"text": "Φ_B", "bold": True},
                {"text": ") measures the total quantity of magnetic field lines passing perpendicularly through a given surface area: "},
                {"text": "Φ_B = B · A = B A cos(θ)", "bold": True},
                {"text": ", where B is the magnetic field strength, A is the surface area, and θ is the angle between the field lines and the surface normal."}
            ]),
            ("paragraph", [
                {"text": "Think of a wire loop as an open net held in a flowing stream. The total water passing through the net depends on how swiftly the stream moves, how large the net opening is, and whether the net faces the current squarely or is tilted on an angle."}
            ]),
            ("heading_1", "How is voltage induced?"),
            ("paragraph", [
                {"text": "The induced electromotive force is directly proportional to how fast the magnetic flux changes: "},
                {"text": "E = -N (dΦ_B / dt)", "bold": True},
                {"text": ", where N is the number of tightly wound turns in the coil."}
            ]),
            ("paragraph", [
                {"text": "A stationary, motionless magnet sitting inside a coil produces zero induced voltage, no matter how powerful its magnetic field may be. Voltage appears only while the flux is "},
                {"text": "changing", "bold": True},
                {"text": ". This change can be produced in three distinct ways:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Varying magnetic field strength", "bold": True},
                {"text": ": moving a magnet closer or farther from the coil, or changing the current flowing through an adjacent electromagnet."}
            ]),
            ("bulleted_list_item", [
                {"text": "Altering the coil area", "bold": True},
                {"text": ": stretching, compressing, or sliding the boundary of the conductive loop within the magnetic field."}
            ]),
            ("bulleted_list_item", [
                {"text": "Rotating the loop", "bold": True},
                {"text": ": spinning the coil within a steady magnetic field so that its surface orientation relative to the field lines changes continuously."}
            ]),
            ("heading_1", "Why did this discovery transform the world?"),
            ("paragraph", [
                {"text": "Before Faraday's discovery, electrical power came almost exclusively from chemical batteries, which were expensive, bulky, and quick to drain."}
            ]),
            ("paragraph", [
                {"text": "Faraday's law proved that mechanical energy—from falling water in hydroelectric dams, steam turbines powered by coal or nuclear reactions, or spinning wind turbines—could be converted directly into continuous, high-voltage electrical power. Every modern electrical generator, utility power grid, step-up transformer, induction cooktop, and microphone relies on this principle."}
            ]),
            ("heading_1", "The Maxwell-Faraday equation"),
            ("paragraph", [
                {"text": "James Clerk Maxwell expressed Faraday's experimental discovery in mathematical differential form as the third of his four fundamental equations: "},
                {"text": "∇ × E = -∂B/∂t", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "This equation revealed something revolutionary: a changing magnetic field produces an electric field in empty space even if no physical wire or loop is present. When combined with Maxwell's fourth equation (a changing electric field produces a magnetic field), it proved that electromagnetic disturbances propagate through space as self-sustaining waves—unveiling the true physical nature of light."}
            ]),
        ]
    },
    {
        "slug": "science/physics/electromagnetism/lenzs_law",
        "label": "Lenz's Law",
        "title": "Lenz's Law",
        "description": "Why an induced current always opposes the change in magnetic flux that caused it, preserving conservation of energy.",
        "cover_alt": "An induced magnetic field resisting the motion of an approaching magnet.",
        "sections": [
            ("heading_1", "What is Lenz's law?"),
            ("paragraph", [
                {"text": "Lenz's law states that the direction of an induced electric current always opposes the change in magnetic flux that created it."}
            ]),
            ("paragraph", [
                {"text": "Formulated in 1834 by Russian physicist Heinrich Lenz, it provides the physical direction behind Faraday's law of induction and explains the negative sign in Faraday's equation: "},
                {"text": "E = -dΦ_B / dt", "bold": True},
                {"text": "."}
            ]),
            ("heading_1", "How does the opposition work?"),
            ("paragraph", [
                {"text": "When an external magnetic field changes through a conductive loop, the loop responds by resisting that change:"}
            ]),
            ("bulleted_list_item", [
                {"text": "If magnetic flux is increasing", "bold": True},
                {"text": ": the induced current flows in a direction whose own generated magnetic field points opposite to the external field, attempting to cancel out the increase."}
            ]),
            ("bulleted_list_item", [
                {"text": "If magnetic flux is decreasing", "bold": True},
                {"text": ": the induced current flows in a direction whose own magnetic field reinforces the fading field, attempting to sustain it."}
            ]),
            ("paragraph", [
                {"text": "If you push the north pole of a permanent bar magnet toward a wire coil, the coil induces a current that establishes an opposing north pole facing the magnet, repelling your push. If you pull the magnet away, the coil reverses its current to create an attractive south pole, pulling back against your motion."}
            ]),
            ("heading_1", "Conservation of energy in disguise"),
            ("paragraph", [
                {"text": "Lenz's law is not an arbitrary magnetic preference; it is a strict requirement imposed by the conservation of energy."}
            ]),
            ("paragraph", [
                {"text": "Suppose nature worked the opposite way: pushing a magnet toward a coil created an attractive pole. The magnet would accelerate automatically into the coil, which would increase the induced current, pulling the magnet even faster, generating endless kinetic and electrical energy out of nowhere."}
            ]),
            ("paragraph", [
                {"text": "Because perpetual energy creation is impossible, you must do real mechanical work against the repelling magnetic force to push the magnet forward. That mechanical work is the exact physical source of the electrical energy generated in the wire."}
            ]),
            ("heading_1", "Everyday demonstrations: eddy currents and braking"),
            ("paragraph", [
                {"text": "Lenz's law produces visible, counterintuitive physical phenomena:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Magnet in a copper pipe", "bold": True},
                {"text": ": drop a strong neodymium magnet through an ordinary plastic tube, and it falls in a fraction of a second. Drop the same magnet through a non-magnetic vertical copper pipe, and it drifts downward slowly like a feather in honey. The falling magnet induces swirling circular currents ("},
                {"text": "eddy currents", "bold": True},
                {"text": ") in the copper walls whose magnetic fields push upward against the magnet's descent."}
            ]),
            ("bulleted_list_item", [
                {"text": "Eddy current braking", "bold": True},
                {"text": ": high-speed trains, rollercoasters, and modern gym rowers use electromagnets mounted beside spinning copper or aluminium discs. Activating the magnet creates opposing eddy currents that decelerate the vehicle smoothly and silently, without friction pads, mechanical wear, or brake dust."}
            ]),
            ("heading_1", "Back-EMF in inductors and motors"),
            ("paragraph", [
                {"text": "Lenz's law explains why inductors resist sudden changes in current and why electric motors draw far less power once they spin up to full speed."}
            ]),
            ("paragraph", [
                {"text": "As an electric motor rotates, its spinning coils cut through internal magnetic fields, inducing an opposing voltage called "},
                {"text": "back-electromotive force (back-EMF)", "bold": True},
                {"text": ". This back-EMF pushes directly against the incoming supply voltage, limiting operating current. If the motor is mechanically jammed, back-EMF collapses, current surges unchecked, and the coils can quickly overheat and burn out."}
            ]),
        ]
    },
    {
        "slug": "science/physics/quantum_physics/photoelectric_effect",
        "label": "Photoelectric Effect",
        "title": "Photoelectric Effect",
        "description": "How light ejects electrons from matter only above a threshold frequency, proving light is quantized into photons.",
        "cover_alt": "Incident light photons striking a metal surface and ejecting photoelectrons.",
        "sections": [
            ("heading_1", "What is the photoelectric effect?"),
            ("paragraph", [
                {"text": "The photoelectric effect is the physical phenomenon in which electrons are emitted from the surface of a material—typically a clean metal—when light of sufficient frequency shines upon it."}
            ]),
            ("paragraph", [
                {"text": "First observed by Heinrich Hertz in 1887 and explained by Albert Einstein in 1905, it provided experimental proof that light cannot be understood solely as continuous waves, but also behaves as discrete packets of energy known as photons."}
            ]),
            ("heading_1", "The puzzle classical physics could not explain"),
            ("paragraph", [
                {"text": "By the late nineteenth century, Maxwell's wave theory of light was widely considered complete. According to classical wave mechanics, light energy spreads out continuously across a wave front."}
            ]),
            ("paragraph", [
                {"text": "Classical wave theory made two clear predictions:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Brighter light should eject faster electrons", "bold": True},
                {"text": ": higher light intensity carries more energy, so emitted electrons should leave with greater kinetic energy."}
            ]),
            ("bulleted_list_item", [
                {"text": "Dim light should cause a time delay", "bold": True},
                {"text": ": faint light carries less energy per second, so electrons should need time to absorb enough wave energy before escaping."}
            ]),
            ("paragraph", [
                {"text": "Careful experiments showed that both classical predictions were completely wrong. If the light frequency fell below a specific cutoff threshold, even intense red light failed to eject a single electron. But above that threshold frequency, even extraordinarily dim ultraviolet light ejected electrons instantaneously, with no detectable delay."}
            ]),
            ("heading_1", "Einstein's photon explanation"),
            ("paragraph", [
                {"text": "Einstein solved the contradiction by applying Max Planck's quantum hypothesis to electromagnetic radiation itself: light is emitted, transmitted, and absorbed in localized discrete packets of energy called "},
                {"text": "photons", "bold": True},
                {"text": ", each carrying energy proportional to frequency: "},
                {"text": "E = h f", "bold": True},
                {"text": ", where h is Planck's constant and f is light frequency."}
            ]),
            ("paragraph", [
                {"text": "Inside the metal, an incoming photon transfers its entire energy to a single electron in an instantaneous one-to-one collision:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Work function (Φ)", "bold": True},
                {"text": ": the minimum energy required to liberate an electron from the metal surface."}
            ]),
            ("bulleted_list_item", [
                {"text": "Below threshold frequency (h f < Φ)", "bold": True},
                {"text": ": no individual photon possesses enough energy to free an electron, no matter how many photons hit the surface per second."}
            ]),
            ("bulleted_list_item", [
                {"text": "Above threshold frequency (h f ≥ Φ)", "bold": True},
                {"text": ": the electron absorbs the photon, pays the work function fee to escape, and leaves with the remaining energy as kinetic energy: "},
                {"text": "K_max = h f - Φ", "bold": True},
                {"text": "."}
            ]),
            ("paragraph", [
                {"text": "Increasing light brightness simply means delivering more photons per second, ejecting more electrons, but without altering the speed of any individual electron. To increase an electron's kinetic energy, you must increase the light's frequency."}
            ]),
            ("heading_1", "The birth of the quantum revolution"),
            ("paragraph", [
                {"text": "Einstein was awarded the 1921 Nobel Prize in Physics not for his general theory of relativity, but specifically for his theoretical explanation of the photoelectric effect."}
            ]),
            ("paragraph", [
                {"text": "The discovery established the foundation of quantum mechanics and proved "},
                {"text": "wave-particle duality", "bold": True},
                {"text": ": light travels across space with wave characteristics such as interference and diffraction, yet exchanges energy with matter in localized, particle-like packets."}
            ]),
            ("heading_1", "Practical technologies that rely on it"),
            ("paragraph", [
                {"text": "The photoelectric effect is behind several everyday modern technologies:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Solar photovoltaic panels", "bold": True},
                {"text": ": solar cells absorb sunlight photons to liberate electrons within semiconductor junctions, generating clean direct-current electricity."}
            ]),
            ("bulleted_list_item", [
                {"text": "Digital camera sensors", "bold": True},
                {"text": ": CMOS and CCD image sensors convert incoming scene photons into proportional electrical charges at every pixel site to record digital photographs."}
            ]),
            ("bulleted_list_item", [
                {"text": "Photomultiplier tubes and night vision", "bold": True},
                {"text": ": high-gain optical detectors amplify faint light by converting individual incident photons into cascading showers of electrons that illuminate digital screens."}
            ]),
        ]
    },
    {
        "slug": "technology/computer/artificial_intelligence/machine_learning/models/llm/flow_architecture",
        "label": "LLM Flow Architecture",
        "title": "LLM Flow Architecture",
        "description": "How modern language model applications structure pipelines, routing, retrieval, tools and state to produce reliable systems.",
        "cover_alt": "A structured flow diagram showing routing, retrieval, caching, execution loops and verification in an LLM system.",
        "sections": [
            ("heading_1", "What is an LLM flow architecture?"),
            ("paragraph", [
                {"text": "An LLM flow architecture is the structural design of software systems built around large language models."}
            ]),
            ("paragraph", [
                {"text": "A raw language model is simply a statistical next-token predictor. Left on its own, it has no memory, cannot query internal business databases, cannot execute external tools, and cannot verify whether its own assertions are factually correct."}
            ]),
            ("paragraph", [
                {"text": "Flow architecture surrounds the model with deterministic workflows, query routers, context retrieval, tool integrations, and verification guardrails, turning an unpredictable model into a dependable production system."}
            ]),
            ("heading_1", "Why single-prompt interactions fall short"),
            ("paragraph", [
                {"text": "In exploratory demos, people interact with an LLM by submitting a single question and reading the output. In production software, this monolithic approach quickly collapses:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Context clutter and cost inflation", "bold": True},
                {"text": ": cramming complete instructions, historical conversation, and tool specifications into one giant prompt wastes tokens and multiplies response latency."}
            ]),
            ("bulleted_list_item", [
                {"text": "Knowledge cutoffs and hallucination", "bold": True},
                {"text": ": models cannot inspect live databases, code repositories, or recent events without dedicated external retrieval pipelines."}
            ]),
            ("bulleted_list_item", [
                {"text": "Compounding probabilistic error", "bold": True},
                {"text": ": if an operation requires five chained steps and each step has a 90% success rate, a single unguided prompt completes the task correctly only about 59% of the time."}
            ]),
            ("bulleted_list_item", [
                {"text": "Lack of self-correction", "bold": True},
                {"text": ": once a model makes a flawed assumption early in its generation, it rationalizes that mistake and continues building upon it."}
            ]),
            ("heading_1", "The core stages of a modern flow"),
            ("paragraph", [
                {"text": "High-reliability LLM applications organize execution into distinct, modular pipeline stages:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Gateway and semantic caching", "bold": True},
                {"text": ": when a request enters the application, an ingress gateway evaluates incoming prompt embeddings against a semantic response cache. Identical or closely equivalent queries return pre-validated answers immediately, bypassing model invocation entirely and reducing latency to milliseconds."}
            ]),
            ("bulleted_list_item", [
                {"text": "Intent routing and classification", "bold": True},
                {"text": ": a lightweight classifier assesses the query's complexity and intent. Simple factual queries route to compact, fast models; complex multi-step reasoning routes to frontier reasoning models; and structured data lookups route directly to SQL databases without calling any model."}
            ]),
            ("bulleted_list_item", [
                {"text": "Context assembly and retrieval (RAG)", "bold": True},
                {"text": ": relevant documents and domain knowledge are retrieved and reranked. The system deliberately arranges prompts with static rules and base instructions placed first to maximize prefix/prompt caching reuse across user sessions."}
            ]),
            ("bulleted_list_item", [
                {"text": "Orchestration patterns", "bold": True},
                {"text": ": the flow coordinates execution using proven patterns—sequential chains for multi-step pipelines, parallel branches for consensus evaluation, or orchestrator-subagent loops for complex workflows."}
            ]),
            ("bulleted_list_item", [
                {"text": "Tool execution in isolated environments", "bold": True},
                {"text": ": when the model needs to take actions, it produces typed parameters conforming to strict JSON schemas. Execution occurs in sandboxed runtimes, and real execution outputs feed back into the active context."}
            ]),
            ("bulleted_list_item", [
                {"text": "State management and active KV caching", "bold": True},
                {"text": ": the system preserves conversational history and working scratchpads. Serving engines retain computed Key-Value attention tensors across turns, allowing multi-turn agent interactions to advance without recomputing earlier context."}
            ]),
            ("bulleted_list_item", [
                {"text": "Verification and output guardrails", "bold": True},
                {"text": ": model responses undergo deterministic schema validation, source context fact-checking, and safety policy filters before reaching the user. If an output fails validation, an automated retry loop provides specific error feedback to guide self-correction."}
            ]),
            ("heading_1", "How caching anchors the entire flow"),
            ("paragraph", [
                {"text": "Flow architecture and cache handling reinforce each other at every step:"}
            ]),
            ("bulleted_list_item", [
                {"text": "At the front entrance", "bold": True},
                {"text": ": semantic response caching intercepts high-volume queries before they ever consume GPU compute."}
            ]),
            ("bulleted_list_item", [
                {"text": "During prompt prefill", "bold": True},
                {"text": ": designing deterministic prompt templates with static system instructions and documentation at the start ensures serving engines achieve high prompt prefix cache hit rates."}
            ]),
            ("bulleted_list_item", [
                {"text": "During iterative execution", "bold": True},
                {"text": ": multi-turn agent loops append observations to the end of the context, keeping the shared history stable so the model engine reuses its KV cache rather than recomputing the full trajectory."}
            ]),
            ("heading_1", "Engineering principles for dependable flows"),
            ("paragraph", [
                {"text": "Three core engineering principles distinguish robust LLM systems from brittle prototypes:"}
            ]),
            ("bulleted_list_item", [
                {"text": "Be deterministic wherever possible", "bold": True},
                {"text": ": rely on standard code for sorting, routing, schema validation, and calculations; use language models only where natural language understanding, reasoning, or synthesis is genuinely required."}
            ]),
            ("bulleted_list_item", [
                {"text": "Small, focused prompts outperform sprawling contexts", "bold": True},
                {"text": ": decomposing a complex job into three chained subtasks with narrow, task-specific context consistently yields higher accuracy, lower cost, and faster response times than one enormous prompt."}
            ]),
            ("bulleted_list_item", [
                {"text": "Instrument end-to-end observability", "bold": True},
                {"text": ": log complete execution traces for every routing decision, retrieved chunk, model prompt, tool call, and validation result. Without comprehensive tracing, diagnosing failure modes in non-deterministic systems is impossible."}
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
    created_count = 0
    for art in ARTICLES:
        slug = art["slug"]
        # Check if already exists
        res = notion.databases.query(database_id=database_id, filter={"property": "Id", "title": {"equals": slug}})
        existing = res.get("results", [])
        if existing:
            print(f"Page already exists for slug '{slug}': {existing[0]['id']}. Skipping creation.")
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
        created_count += 1
        print(f"Successfully created Notion page '{slug}' with ID: {page['id']}")

    print(f"\nDone! Created {created_count} new Notion page(s).")

if __name__ == "__main__":
    create_articles()

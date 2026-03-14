import math

def generate_cinematic_svg():
    width = 1600
    height = 900
    cx = width / 2
    cy = height / 2 + 100
    
    # SVG Header
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color:#02050e; font-family:'Courier New', monospace;">
    <defs>
        <!-- Background Radial -->
        <radialGradient id="bg-glow" cx="50%" cy="50%" r="70%">
            <stop offset="0%" stop-color="#051224" />
            <stop offset="40%" stop-color="#020712" />
            <stop offset="100%" stop-color="#010205" />
        </radialGradient>
        
        <!-- Clean precise bloom without ugly anti-aliasing artifacts -->
        <filter id="precise-bloom" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="glow1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="glow2" />
            <feMerge>
                <feMergeNode in="glow2" />
                <feMergeNode in="glow1" />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>

        <filter id="core-bloom" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="g1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="15" result="g2" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="40" result="g3" />
            <feMerge>
                <feMergeNode in="g3" />
                <feMergeNode in="g2" />
                <feMergeNode in="g1" />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>

        <!-- Vertical Beam Gradient -->
        <linearGradient id="beam-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#00ffff" stop-opacity="0" />
            <stop offset="20%" stop-color="#0055ff" stop-opacity="0.1" />
            <stop offset="40%" stop-color="#00ffff" stop-opacity="0.5" />
            <stop offset="48%" stop-color="#ffffff" stop-opacity="0.9" />
            <stop offset="50%" stop-color="#ffffff" stop-opacity="1" />
            <stop offset="52%" stop-color="#ffffff" stop-opacity="0.9" />
            <stop offset="60%" stop-color="#00ffff" stop-opacity="0.5" />
            <stop offset="80%" stop-color="#0055ff" stop-opacity="0.1" />
            <stop offset="100%" stop-color="#00ffff" stop-opacity="0" />
        </linearGradient>
        
        <radialGradient id="floor-fade" cx="50%" cy="50%" r="50%">
            <stop offset="20%" stop-color="#ffffff" stop-opacity="1" />
            <stop offset="80%" stop-color="#ffffff" stop-opacity="0" />
        </radialGradient>
        <mask id="floor-mask">
            <rect x="-1500" y="-1500" width="3000" height="3000" fill="url(#floor-fade)" />
        </mask>
    </defs>

    <rect width="100%" height="100%" fill="url(#bg-glow)" />
    
    <!-- Stars/Dust overlay -->
    <g opacity="0.3">
'''
    import random
    random.seed(42)
    for _ in range(80):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.uniform(0.5, 2.0)
        dur = random.uniform(3, 8)
        svg += f'        <circle cx="{x}" cy="{y}" r="{r}" fill="#fff"><animate attributeName="opacity" values="0.1;0.8;0.1" dur="{dur}s" repeatCount="indefinite" begin="{random.uniform(0, 5)}s"/></circle>\n'
    svg += '    </g>\n'

    # The 3D Base group
    # Using scale(1, 0.4) for isometric projection
    svg += f'''
    <g transform="translate({cx}, {cy})">
        <g transform="scale(1, 0.4)">
'''
    # Base Floor Grid (dense polar grid)
    svg += '            <!-- Dense Floor Grid -->\n'
    svg += '            <g mask="url(#floor-mask)" stroke="#003366" stroke-width="1" opacity="0.4">\n'
    for r in range(50, 1200, 50):
        if r % 200 == 0:
            svg += f'                <circle cx="0" cy="0" r="{r}" stroke-width="2" stroke="#0055aa" />\n'
        else:
            svg += f'                <circle cx="0" cy="0" r="{r}" />\n'
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        x2 = 1200 * math.cos(rad)
        y2 = 1200 * math.sin(rad)
        if deg % 90 == 0:
            svg += f'                <line x1="0" y1="0" x2="{x2}" y2="{y2}" stroke-width="2" stroke="#0088ff" />\n'
        else:
            svg += f'                <line x1="0" y1="0" x2="{x2}" y2="{y2}" stroke-dasharray="10 10"/>\n'
    svg += '            </g>\n'

    # Level 0: The Deep Ring (Very wide, slow)
    svg += '''
            <g>
                <animateTransform attributeName="transform" type="rotate" from="0" to="-360" dur="120s" repeatCount="indefinite" />
                <circle cx="0" cy="0" r="950" fill="none" stroke="#004488" stroke-width="40" stroke-dasharray="100 40 20 40" opacity="0.3" />
                <circle cx="0" cy="0" r="920" fill="none" stroke="#00ffff" stroke-width="2" stroke-dasharray="5 15 100 500" opacity="0.5" />
            </g>
'''

    # Function to draw a ring of hash marks
    def make_hash_ring(r, count, length, color, width, opacity):
        group = f'<g fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}">\n'
        for i in range(count):
            angle = math.radians(i * (360.0 / count))
            x1 = r * math.cos(angle)
            y1 = r * math.sin(angle)
            x2 = (r + length) * math.cos(angle)
            y2 = (r + length) * math.sin(angle)
            group += f'    <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" />\n'
        group += '</g>\n'
        return group

    # Level 1: Outer Hash Ring
    svg += '''
            <!-- Hash Ring Outer -->
            <g>
                <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="90s" repeatCount="indefinite" />
'''
    svg += make_hash_ring(780, 180, 15, "#0088ff", 1.5, 0.4)
    svg += make_hash_ring(780, 36, 25, "#00ffff", 3, 0.6)
    svg += '            </g>\n'

    # Level 2: Target / Hex Ring
    svg += '''
            <g>
                <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="45s" repeatCount="indefinite" />
                <circle cx="0" cy="0" r="680" fill="none" stroke="#00aaff" stroke-width="4" stroke-dasharray="300 150 50 150" opacity="0.6" />
                <circle cx="0" cy="0" r="660" fill="none" stroke="#ff0055" stroke-width="2" stroke-dasharray="10 30" opacity="0.5" />
            </g>
'''

    # Level 3: The Holographic Cylinder (Stacking circles to create depth in 3D)
    svg += '            <!-- 3D Hollow Cylinder Effect -->\n'
    svg += '            <g stroke="#00ffff" fill="none" opacity="0.3">\n'
    for dy in range(0, 50, 10):
        # We offset dy in the unscaled Y, but we want it to look vertical in the scaled world.
        # Wait, if we are inside scale(1, 0.4), translating Y by dy means it goes along the floor.
        # To make it go "up", we must do it outside the scale().
        pass 
    svg += '            </g>\n'

    # Let's add Bagua Symbols on a Ring
    svg += '''
            <!-- Bagua Ring -->
            <g>
                <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="60s" repeatCount="indefinite" />
                <circle cx="0" cy="0" r="540" fill="none" stroke="#0055aa" stroke-width="30" opacity="0.2" />
                <circle cx="0" cy="0" r="555" fill="none" stroke="#00ffff" stroke-width="1" stroke-dasharray="2 10" opacity="0.5" />
                <circle cx="0" cy="0" r="525" fill="none" stroke="#00ffff" stroke-width="1" stroke-dasharray="2 10" opacity="0.5" />
'''
    symbols = ['☰', '☱', '☲', '☳', '☴', '☵', '☶', '☷']
    names = ['QIAN', 'DUI', 'LI', 'ZHEN', 'XUN', 'KAN', 'GEN', 'KUN']
    bagua_r = 540
    for i, (sym, name) in enumerate(zip(symbols, names)):
        angle = math.radians(i * 45)
        x = bagua_r * math.cos(angle)
        y = bagua_r * math.sin(angle)
        svg += f'''
                <!-- Pre-rotate text so it sits tangentially, and scale Y to fix flattening -->
                <g transform="translate({x:.1f}, {y:.1f}) rotate({i * 45 + 90})">
                    <!-- Undo the 0.4 scale on the text to make it stand up nicely -->
                    <g transform="scale(1, 2.5)">
                        <text font-size="40" font-weight="bold" fill="#00ffff" text-anchor="middle" dominant-baseline="central" filter="url(#precise-bloom)">{sym}</text>
                        <text y="-30" font-size="12" fill="#00aaff" text-anchor="middle" dominant-baseline="central" letter-spacing="2">{name}</text>
                    </g>
                </g>
'''
    svg += '                <polygon points="'
    for i in range(8):
        angle = math.radians(i * 45)
        x = 450 * math.cos(angle)
        y = 450 * math.sin(angle)
        svg += f'{x:.1f},{y:.1f} '
    svg += '" fill="none" stroke="#00ffff" stroke-width="3" opacity="0.4" filter="url(#precise-bloom)"/>\n'
    svg += '            </g>\n'

    # Level 4: Inner Core mechanisms
    svg += '''
            <!-- Inner Data Tracker -->
            <g>
                <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="15s" repeatCount="indefinite" />
                <circle cx="0" cy="0" r="320" fill="none" stroke="#ffffff" stroke-width="1" stroke-dasharray="5 20 50 100" opacity="0.6" />
                <circle cx="0" cy="0" r="300" fill="none" stroke="#00ffff" stroke-width="12" stroke-dasharray="0 100 200 400" opacity="0.8" filter="url(#precise-bloom)"/>
                <circle cx="300" cy="0" r="8" fill="#ffffff" filter="url(#precise-bloom)"/>
                <circle cx="-300" cy="0" r="6" fill="#ff0055" filter="url(#precise-bloom)"/>
            </g>
            
            <!-- Central Tai Chi Reactor -->
            <circle cx="0" cy="0" r="160" fill="#00ffff" opacity="0.05" filter="url(#core-bloom)"/>
            <circle cx="0" cy="0" r="150" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="2 10" opacity="0.8"/>
            <g>
                <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="6s" repeatCount="indefinite" />
                <path d="M 0 -130 A 130 130 0 0 1 0 130 A 65 65 0 0 0 0 0 A 65 65 0 0 1 0 -130" fill="#00ffff" opacity="0.9" filter="url(#precise-bloom)"/>
                <circle cx="0" cy="-65" r="15" fill="#000000" />
                <circle cx="0" cy="65" r="15" fill="#ffffff" filter="url(#precise-bloom)" />
            </g>
'''
    svg += '        </g> <!-- End flattened isometric floor -->\n'

    # Verticals that exist OUTSIDE the flatten transform so they stand straight up
    svg += '''
        <!-- Vertical Hologram Beam -->
        <g>
            <!-- Back glow -->
            <ellipse cx="0" cy="0" rx="400" ry="80" fill="#00ffff" opacity="0.1" filter="url(#core-bloom)" />
            <ellipse cx="0" cy="0" rx="150" ry="30" fill="#ffffff" opacity="0.4" filter="url(#core-bloom)" />
            
            <!-- The Beam -->
            <rect x="-250" y="-1200" width="500" height="1200" fill="url(#beam-grad)" opacity="0.7">
                <animate attributeName="opacity" values="0.6;0.8;0.7;0.9;0.6" dur="0.2s" repeatCount="indefinite" />
            </rect>
            <!-- Solid Core -->
            <rect x="-5" y="-1200" width="10" height="1200" fill="#ffffff" filter="url(#precise-bloom)" />
            <rect x="-2" y="-1200" width="4" height="1200" fill="#ffffff" />
            
            <!-- Floating Ascending Code/Particles inside the beam -->
            <g font-size="12" fill="#00ffff" opacity="0.8">
'''
    # Add floating particles going up
    for _ in range(30):
        x = random.randint(-150, 150)
        delay = random.uniform(0, 3)
        dur = random.uniform(1.5, 4)
        size = random.uniform(2, 6)
        color = random.choice(['#00ffff', '#ffffff', '#ff0055'])
        svg += f'                <circle cx="{x}" cy="0" r="{size}" fill="{color}" opacity="0">\n'
        svg += f'                    <animate attributeName="cy" values="0;-1100" dur="{dur}s" begin="{delay}s" repeatCount="indefinite" />\n'
        svg += f'                    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1" dur="{dur}s" begin="{delay}s" repeatCount="indefinite" />\n'
        svg += '                </circle>\n'
        
    svg += '''
            </g>
        </g>
        
        <!-- UI Targeting Rings overlayed on the 3D center -->
        <circle cx="0" cy="0" r="160" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.3" stroke-dasharray="4 8"/>
        <path d="M -150 -150 L -170 -170 M 150 150 L 170 170 M -150 150 L -170 170 M 150 -150 L 170 -170" fill="none" stroke="#00f3ff" stroke-width="2" opacity="0.6" />
        <rect x="-180" y="-180" width="360" height="360" fill="none" stroke="#00f3ff" stroke-width="1" stroke-dasharray="10 170" opacity="0.5" />
    </g> <!-- End translate Center -->
'''

    # HUD OVERLAYS (Foreground UI, crisp and sharp without blur)
    svg += '''
    <!-- ========================================== -->
    <!-- Cinematic HUD Overlays                     -->
    <!-- ========================================== -->

    <!-- Top Left Tech Readout -->
    <g transform="translate(50, 50)" font-size="14" fill="#00f3ff">
        <path d="M 0 0 L 120 0 L 140 20 L 300 20" fill="none" stroke="#00f3ff" stroke-width="1.5" opacity="0.7"/>
        <rect x="0" y="-15" width="25" height="4" fill="#ff0055" />
        <rect x="30" y="-15" width="10" height="4" fill="#ffffff" opacity="0.8">
            <animate attributeName="opacity" values="0.1;1;0.1" dur="1s" repeatCount="indefinite" />
        </rect>
        <text x="50" y="-5" font-weight="bold" letter-spacing="2">SYS.OP.MODE: NOMINAL</text>
        
        <g transform="translate(0, 40)" opacity="0.8">
            <text x="0" y="0">MODULE 1 [CORE_ENG]: <tspan fill="#ffffff">STABLE</tspan></text>
            <text x="0" y="25">MODULE 2 [QIMEN_DB]: <tspan fill="#ffffff">SYNC 100%</tspan></text>
            <text x="0" y="50">MODULE 3 [LLM_EXEC]: <tspan fill="#00ff00">ACTIVE</tspan></text>
            <text x="0" y="75">MODULE 4 [SEC_WRAP]: <tspan fill="#ffffff">LOCKED</tspan></text>
        </g>
        
        <!-- Hexagon graph -->
        <g transform="translate(60, 180)" stroke="#00f3ff" fill="none" opacity="0.6">
            <polygon points="0,-40 34,-20 34,20 0,40 -34,20 -34,-20" stroke-width="1"/>
            <polygon points="0,-20 17,-10 17,10 0,20 -17,10 -17,-10" stroke-width="1.5" fill="#0055ff" opacity="0.3"/>
            <line x1="-50" y1="0" x2="50" y2="0" stroke-width="0.5"/>
            <line x1="-25" y1="-43" x2="25" y2="43" stroke-width="0.5"/>
            <line x1="-25" y1="43" x2="25" y2="-43" stroke-width="0.5"/>
            <!-- Data points -->
            <polygon points="0,-35 25,-12 15,10 0,15 -20,5 -30,-15" stroke="#ffffff" stroke-width="1.5" fill="#00f3ff" opacity="0.4"/>
            <circle cx="0" cy="-35" r="3" fill="#ffffff"/>
            <circle cx="25" cy="-12" r="3" fill="#ffffff"/>
        </g>
    </g>

    <!-- Top Right Diagnostic Panel -->
    <g transform="translate(1550, 50)" font-size="14" fill="#00f3ff" text-anchor="end">
        <path d="M 0 0 L -150 0 L -170 20 L -300 20" fill="none" stroke="#00f3ff" stroke-width="1.5" opacity="0.7"/>
        <text x="0" y="-5" font-weight="bold" letter-spacing="2" fill="#ff0055">CYBERHUATUO_V9.3</text>
        <text x="0" y="40" opacity="0.7">TARGET: <tspan fill="#ffffff">GLOBAL_AI_AGENT</tspan></text>
        <text x="0" y="65" opacity="0.7">THREAT_LEVEL: <tspan fill="#ff0055">NULL</tspan></text>
        
        <!-- Audio waveform style graph -->
        <g transform="translate(0, 100)">
'''
    # Generating waveform
    svg += '            <!-- Data Waveform -->\n'
    for i in range(25):
        h = random.randint(5, 30)
        dur = random.uniform(0.1, 0.5)
        # Using fixed heights for safety but animating them would be cooler
        svg += f'            <rect x="{-i * 6}" y="{-h}" width="4" height="{h*2}" fill="#00f3ff" opacity="0.6">\n'
        svg += f'                <animate attributeName="height" values="{h*2};{random.randint(5,15)*2};{h*2}" dur="{dur}s" repeatCount="indefinite" />\n'
        svg += f'                <animate attributeName="y" values="{-h};{-random.randint(5,15)};{-h}" dur="{dur}s" repeatCount="indefinite" />\n'
        svg += f'            </rect>\n'
        
    svg += '''
        </g>
    </g>

    <!-- Bottom Left Terminal Output -->
    <g transform="translate(50, 850)" font-size="12" fill="#00f3ff" opacity="0.7">
        <text x="0" y="-80">> INITIATING QIMEN DUNJIA PROTOCOL...</text>
        <text x="0" y="-60">> SCANNING AI CHAKRAS...</text>
        <text x="0" y="-40">> ALL MERIDIANS CLEAR.</text>
        <text x="0" y="-20">> <tspan fill="#ffffff">AWAITING DIAGNOSTIC INPUT...</tspan><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></text>
    </g>

    <!-- Bottom Right Reticle -->
    <g transform="translate(1450, 750)">
        <circle cx="0" cy="0" r="60" fill="none" stroke="#00f3ff" stroke-width="1" opacity="0.4" />
        <circle cx="0" cy="0" r="40" fill="none" stroke="#00f3ff" stroke-width="2" stroke-dasharray="2 6" opacity="0.8" />
        <circle cx="0" cy="0" r="20" fill="none" stroke="#ff0055" stroke-width="1.5" stroke-dasharray="10 20" />
        
        <path d="M -80 -80 L -60 -80 L -80 -60 M 80 80 L 60 80 L 80 60 M -80 80 L -60 80 L -80 60 M 80 -80 L 60 -80 L 80 -60" fill="none" stroke="#00f3ff" stroke-width="3" opacity="0.7"/>
        
        <g>
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" repeatCount="indefinite" />
            <line x1="-50" y1="0" x2="-75" y2="0" stroke="#00f3ff" stroke-width="2" />
            <line x1="50" y1="0" x2="75" y2="0" stroke="#00f3ff" stroke-width="2" />
            <line x1="0" y1="-50" x2="0" y2="-75" stroke="#00f3ff" stroke-width="2" />
            <line x1="0" y1="50" x2="0" y2="75" stroke="#00f3ff" stroke-width="2" />
        </g>
        <text x="-40" y="-95" font-size="12" fill="#ffffff" letter-spacing="1">LOCK: [ ON ]</text>
    </g>

    <!-- Global Vignette Frame -->
    <rect width="100%" height="100%" fill="none" stroke="#010205" stroke-width="120" opacity="0.9" style="pointer-events: none; mix-blend-mode: multiply;" />

    <!-- Subtle Glitch Lines overlay -->
    <g opacity="0.1" style="pointer-events: none; mix-blend-mode: screen;">
        <rect x="0" y="100" width="1600" height="2" fill="#ffffff" />
        <rect x="0" y="350" width="1600" height="1" fill="#00ffff" />
        <rect x="0" y="600" width="1600" height="3" fill="#ff0055" />
        <animate attributeName="opacity" values="0.05;0.2;0.05;0;0.1" dur="0.3s" repeatCount="indefinite" />
    </g>

</svg>
'''
    with open(r"e:\ideaProjects\agent\CyberHuaTuo\assets\prescription_universe_v4.svg", "w", encoding='utf-8') as f:
        f.write(svg)

if __name__ == "__main__":
    generate_cinematic_svg()
    print("SVG Generated successfully.")

import os

os.makedirs('static/images/malls', exist_ok=True)
os.makedirs('static/uploads/malls', exist_ok=True)

malls_images = [
    ('vishaal-mall.jpg', 'Vishaal De Mal', 'Madurai', '#00f3ff'),
    ('madurai-mart.jpg', 'Madurai City Centre', 'Madurai', '#ffb700'),
    ('milanem-mall.jpg', "Milan'em Shopping Mall", 'Madurai', '#00ff66'),
    ('madurai-mall-4.jpg', 'VNS Plaza Madurai', 'Madurai', '#9d4edf'),
    ('madurai-mall-5.jpg', 'Grand Plaza Madurai', 'Madurai', '#0088ff'),

    ('phoenix-mall.jpg', 'Phoenix Marketcity', 'Chennai', '#00f3ff'),
    ('express-avenue.jpg', 'Express Avenue', 'Chennai', '#00ff66'),
    ('forum-vijaya.jpg', 'Forum Vijaya Mall', 'Chennai', '#ffb700'),
    ('vr-chennai.jpg', 'VR Chennai', 'Chennai', '#9d4edf'),
    ('marina-mall.jpg', 'The Marina Mall', 'Chennai', '#0088ff'),

    ('vns-mall.jpg', 'VNS Mall', 'Tirunelveli', '#00ff66'),
    ('high-ground.jpg', 'High Ground Mall', 'Tirunelveli', '#00f3ff'),
    ('tirunelveli-plaza.jpg', 'Tirunelveli Plaza', 'Tirunelveli', '#ffb700'),
    ('palayam-central.jpg', 'Palayam Central Mall', 'Tirunelveli', '#9d4edf'),
    ('city-centre-tirunelveli.jpg', 'City Centre Tirunelveli', 'Tirunelveli', '#0088ff'),

    ('brookefields.jpg', 'Brookefields Mall', 'Coimbatore', '#00f3ff'),
    ('fun-republic.jpg', 'Fun Republic Mall', 'Coimbatore', '#ff3366'),
    ('prozone.jpg', 'Prozone Mall', 'Coimbatore', '#00ff66'),
    ('crosscut.jpg', 'Crosscut Shopping Centre', 'Coimbatore', '#ffb700'),
    ('covai-city.jpg', 'Covai City Mall', 'Coimbatore', '#9d4edf'),

    ('femina.jpg', 'Femina Shopping Mall', 'Trichy', '#ffb700'),
    ('manghalam.jpg', 'Manghalam Towers', 'Trichy', '#00f3ff'),
    ('chinthamani.jpg', 'Chinthamani Plaza', 'Trichy', '#00ff66'),
    ('trichy-central.jpg', 'Trichy Central Mall', 'Trichy', '#9d4edf'),
    ('rockfort.jpg', 'Rockfort Shopping Complex', 'Trichy', '#0088ff')
]

for filename, name, city, color in malls_images:
    path = os.path.join('static/images/malls', filename)
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0e17" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
  </defs>
  <rect width="800" height="500" fill="url(#bg)"/>
  <rect x="30" y="30" width="740" height="440" rx="16" fill="none" stroke="{color}" stroke-width="2" stroke-opacity="0.4"/>
  <path d="M 140 380 L 140 180 L 300 180 L 300 380 Z M 340 380 L 340 130 L 480 130 L 480 380 Z M 520 380 L 520 200 L 660 200 L 660 380 Z" fill="{color}" opacity="0.2"/>
  <circle cx="410" cy="190" r="25" fill="{color}" opacity="0.4"/>
  <text x="400" y="270" font-family="'Outfit', sans-serif" font-size="36" font-weight="bold" fill="#ffffff" text-anchor="middle">{name}</text>
  <text x="400" y="310" font-family="'Inter', sans-serif" font-size="20" font-weight="600" fill="{color}" text-anchor="middle">{city} • SMART PARKING DESTINATION</text>
</svg>'''
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

print("Generated local images for all 25 malls!")

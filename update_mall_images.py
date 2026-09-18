from app import app
from models.db import db
from models.models import Mall

mall_image_mapping = {
    "Vishaal De Mal": "/static/images/malls/vishaal-mall.jpg",
    "Madurai City Centre": "/static/images/malls/madurai-mart.jpg",
    "Milan'em Shopping Mall": "/static/images/malls/milanem-mall.jpg",
    "VNS Plaza Madurai": "/static/images/malls/madurai-mall-4.jpg",
    "Grand Plaza Madurai": "/static/images/malls/madurai-mall-5.jpg",

    "Phoenix Marketcity": "/static/images/malls/phoenix-mall.jpg",
    "Express Avenue": "/static/images/malls/express-avenue.jpg",
    "Forum Vijaya Mall": "/static/images/malls/forum-vijaya.jpg",
    "VR Chennai": "/static/images/malls/vr-chennai.jpg",
    "The Marina Mall": "/static/images/malls/marina-mall.jpg",

    "VNS Mall": "/static/images/malls/vns-mall.jpg",
    "High Ground Mall": "/static/images/malls/high-ground.jpg",
    "Tirunelveli Plaza": "/static/images/malls/tirunelveli-plaza.jpg",
    "Palayam Central Mall": "/static/images/malls/palayam-central.jpg",
    "City Centre Tirunelveli": "/static/images/malls/city-centre-tirunelveli.jpg",

    "Brookefields Mall": "/static/images/malls/brookefields.jpg",
    "Fun Republic Mall": "/static/images/malls/fun-republic.jpg",
    "Prozone Mall": "/static/images/malls/prozone.jpg",
    "Crosscut Shopping Centre": "/static/images/malls/crosscut.jpg",
    "Covai City Mall": "/static/images/malls/covai-city.jpg",

    "Femina Shopping Mall": "/static/images/malls/femina.jpg",
    "Manghalam Towers": "/static/images/malls/manghalam.jpg",
    "Chinthamani Plaza": "/static/images/malls/chinthamani.jpg",
    "Trichy Central Mall": "/static/images/malls/trichy-central.jpg",
    "Rockfort Shopping Complex": "/static/images/malls/rockfort.jpg"
}

with app.app_context():
    malls = Mall.query.all()
    updated_count = 0
    for m in malls:
        if m.name in mall_image_mapping:
            m.image_url = mall_image_mapping[m.name]
            updated_count += 1
        elif not m.image_url:
            m.image_url = "/static/images/malls/default-mall.jpg"
            updated_count += 1
            
    db.session.commit()
    print(f"Successfully updated image_url for {updated_count} malls in existing database.")

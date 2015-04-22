intro = """
You have subscribed to receive forest change alerts through <a href='http://www.globalforestwatch.org/'>Global Forest Watch</a>. This message reports new forest change alerts and user stories for the area of interest you selected (a country, subnational jurisdiction, or user-drawn shape). You will receive a separate email for each distinct area of interest you subscribe to.
<br><br>Digest:<br><br>
"""

alert = """
<b><a href='{url}'>{link_text}</a></b> (<i>{description}</i>): {alerts}<br><br>
"""

simple_alert = """
<b><a href='{url}'>{link_text}</a></b>: {alerts}<br><br>
"""

outro = """
<br><br>
Please note that this information is subject to the Global Forest Watch <a href='http://globalforestwatch.com/terms'>Terms of Service</a>. You can unsubscribe or manage your subscriptions by emailing gfw@wri.org. Please visit <a href='http://fires.globalforestwatch.org/#v=home&x=115&y=0&l=5&lyrs=Active_Fires'>GFW Fires</a> to subscribe to receive fire alerts. 
"""

link_geom = """http://www.globalforestwatch.org/map/3/{lat}/{lon}/ALL/grayscale/{url_id}?geojson={geom}&begin={begin}&end={end}"""
link_iso = """http://www.globalforestwatch.org/map/4/0/0/{iso}/grayscale/{url_id}?begin={begin}&end={end}"""

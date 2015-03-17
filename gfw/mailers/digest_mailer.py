intro = """You have subscribed to forest change alerts through Global
Forest Watch. This message reports new forest change alerts for one of your
areas of interest (a country or self-drawn polygon).

<br><br>
h4 Digest:
"""

summary = """
<b>{name} (<a href='{link}'>details</a>):</b> {value} alerts <br>
"""

list_summary_lead = """
<b>{name} (<a href='{link}'>details</a>):</b><br>
"""

list_summary_row = """
  -- {value} {data_type} alerts  <br>
"""


dump_summary = """
"""



outro = """
<br><br>

You can unsubscribe or manage your subscriptions by emailing: gfw@wri.org

<br><br>

You will receive a separate e-mail for each distinct polygon, country, or shape
on the GFW map. You will also receive a separate e-mail for each dataset for
which you have requested alerts (FORMA alerts, Imazon SAD Alerts, and NASA
QUICC alerts.)

<br><br>

Please note that this information is subject to the Global Forest Watch <a
href='http://globalforestwatch.com/terms'>Terms of Service</a>.
"""

link_geom = """http://www.globalforestwatch.org/map/3/{lat}/{lon}/ALL/grayscale/forma?geojson={geom}&begin={begin}&end={end}"""
link_iso = """http://www.globalforestwatch.org/map/4/0/0/{iso}/grayscale/forma?begin={begin}&end={end}"""



intro = """
<br>
You have subscribed to receive alerts from <a href='http://www.globalforestwatch.org/'>Global Forest Watch</a>. This message reports new forest change alerts and user stories for the area of interest you selected. You will receive a separate email for each distinct area of interest you subscribe to. 
<br><br>
"""

header="""
<b><u>Selected area</u>: {selected_area_name}</b>
<br><br><br>
"""

table_header = """
<table>
  <tr>
    <th style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" ><b>New alerts</b></th>
    <th style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" ><b>Type of Alert</b></th>
    <th style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" ><b>Date of Alerts*</b></th>
    <th style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" ><b>Summary</b></th>
    <th style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" ><b>Specs</b></th>
    <th style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" ><b>View & Download</b></th>
  </tr>
"""

table_row = """
<tr>
  <td style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" >{alerts}</td>
  <td style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" >{email_name}</td>
  <td style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" >{date_range}</td>
  <td style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" >{summary}</td>
  <td style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" >{alert_types}{specs}</td>
  <td style="border-left: solid 1px #bbbbbb;padding:2px;font-size:90%;" ><a href='{url}'>Link</a></td>
</tr>
"""

table_footer = """
</table>
"""

outro = """
<br>
<em style="font-size:90%;">*"Date of Alerts" refers to the date range within which change was actually detected. There may be lag time between detection and when you receive this email.</em>
<br>
<br>
<br>
Please note that this information is subject to the Global Forest Watch <a href='http://globalforestwatch.com/terms'>Terms of Service</a>. You can unsubscribe or manage your subscriptions by emailing gfw@wri.org. Please visit <a href='http://fires.globalforestwatch.org/#v=home&x=115&y=0&l=5&lyrs=Active_Fires'>GFW Fires</a> to subscribe to receive fire alerts. 
<br>
<br>
<br>
"""
link_country_iso = """http://www.globalforestwatch.org/country/{iso}"""
link_country_id1 = """http://www.globalforestwatch.org/country/{iso}/{id1}"""
link_geom = """http://www.globalforestwatch.org/map/3/{lat}/{lon}/ALL/grayscale/{url_id}?geojson={geom}&begin={begin}&end={end}"""
link_iso = """http://www.globalforestwatch.org/map/4/0/0/{iso}/grayscale/{url_id}?begin={begin}&end={end}"""

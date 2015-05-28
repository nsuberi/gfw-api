intro = """
<br>
You have subscribed to receive alerts from <a href='http://www.globalforestwatch.org/'>Global Forest Watch</a>. This message reports new forest change alerts and user stories for the area of interest you selected. You will receive a separate email for each distinct area of interest you subscribe to. 
<br><br>
"""

header="""
<b><u>Selected area</u>: {selected_area_name}</b>
<br><br>
"""

table_header = """
<table>
  <tr>
    <th><b>New alerts</b></th>
    <th><b>Type of Alert</b></th>
    <th><b>Date of Alerts*</b></th>
    <th><b>Summary</b></th>
    <th><b>Specs</b></th>
    <th><b>View & Download</b></th>
  </tr>
"""

table_row = """
<tr>
  #<td>{alerts}</td>
  <td>{email_name}</td>
  #<td>{min_date} to {max_date}</td>
  <td>{summary}</td>
  <td>{specs}</td>
  <td><a href='{url}'>Link</a></td>
</tr>
"""

table_footer = """
</table>
"""

outro = """
<em>*"Date of Alerts" refers to the date range within which change was actually detected. There may be lag time between detection and when you receive this email.</em>
<br>
<br>
Please note that this information is subject to the Global Forest Watch <a href='http://globalforestwatch.com/terms'>Terms of Service</a>. You can unsubscribe or manage your subscriptions by emailing gfw@wri.org. Please visit <a href='http://fires.globalforestwatch.org/#v=home&x=115&y=0&l=5&lyrs=Active_Fires'>GFW Fires</a> to subscribe to receive fire alerts. 
<br>
<br>
<br>
"""

link_geom = """http://www.globalforestwatch.org/map/3/{lat}/{lon}/ALL/grayscale/{url_id}?geojson={geom}&begin={min_date}&end={max_date}"""
link_iso = """http://www.globalforestwatch.org/map/4/0/0/{iso}/grayscale/{url_id}?begin={min_date}&end={max_date}"""

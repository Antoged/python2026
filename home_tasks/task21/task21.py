page = {
    "title": "Тег BODY",
    "charset": "utf-8",
    "alert": "Документ загружен",
    "p": "Ut wisis enim ad minim veniam,  suscipit lobortis nisl ut aliquip ex ea commodo consequat."
}

html_content = f"""<!DOCTYPE HTML>
<html>
 <head>
  <title> {page["title"]} </title>
  <meta charset="{page["charset"]}">
 </head>
 <body onload="alert('{page["alert"]}')">
 
  <p>{page["p"]}</p>

 </body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

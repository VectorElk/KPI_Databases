## About
Lab #1 project for databases 5th semester course: basic XML documents processing. Variant #2
## Goals
* Fetch 20 HTML pages starting from `http.ru.golos.ua` recursively, parse, extract text and image urls using XPATH. Parsing results save as XML file of the following structure:
```xml
<data>
<page url=”wwww.example.com/index.hml”>
<fragment type=”text”>
.... text data
</fragment>
<fragment type=”image”>
.... image url
</fragment>
</page>
<page url=”wwww.example.com/page.hml”>
<fragment type=”text”>
.... text data
</fragment>
<fragment type=”image”>
.... image url
</fragment>
</page>
...
</data>
```

* Using XPATH get average text fragments count in dataset
* Fetch name, price and image for 20 products from online store `petmarket.ua` using XPATH, save as XML file.
* Transform product list XML into HTML table using XSLT

## Usage
* run main.py
* enjoy
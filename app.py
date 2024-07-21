from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import scraping

app = Flask(__name__)
CORS(app)

@app.route('/')
@cross_origin()
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
@cross_origin()
def result():
    query = request.form['query']
    product_info, df = scraping.scrape_amazon(query)
    table = df.to_html(classes='table table-striped', index=False)
    return render_template('result.html', query=query, table=table, product_info=product_info)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=False)
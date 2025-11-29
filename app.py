from flask import Flask,render_template,request
from pipeline.prediction_pipeline import hybrid_recommendation
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram
import time
from prometheus_client import start_http_server


app = Flask(__name__)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

# Custom metrics
recommendation_requests = Counter('recommendation_requests_total', 'Total recommendation requests')
recommendation_errors = Counter('recommendation_errors_total', 'Total recommendation errors')
recommendation_duration = Histogram('recommendation_duration_seconds', 'Time spent generating recommendations')

@app.route('/' , methods=['GET','POST'])
def home():
    recommendations = None

    if request.method == 'POST':
        recommendation_requests.inc()
        start_time = time.time()
        try:
            user_id = int(request.form["userID"])
            recommendations = hybrid_recommendation(user_id)
        except Exception as e:
            recommendation_errors.inc()
            print("Erorr occured....")
        finally:
            recommendation_duration.observe(time.time() - start_time)

    return render_template('index.html' , recommendations=recommendations)

if __name__=="__main__":
    start_http_server(8000)
    app.run(debug=True,host='0.0.0.0',port=5000)
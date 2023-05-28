from flask import Flask, render_template, request, session
from stock_view import StockView
import multiprocessing
import os

# import firebase_admin
# from firebase_admin import credentials

# cred = credentials.Certificate("path/to/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)


app = Flask(__name__)
app.config["SECRET_KEY"] = "Emilywillisx3"


@app.route('/')
def index():
    return render_template('index.html')


def generate_plots(stock_name):
    stock_view = StockView(stock_name)
    stock_view.create_graph()
    # Save the plot image to the temporary file system
    stock_view.save_plot_to_tmp()


@app.route('/stockview', methods=['GET', 'POST'])
def project():
    # Clear previous image file
    image_path = os.path.join(app.static_folder, 'stock_plot.png')
    if os.path.exists(image_path):
        os.remove(image_path)
    if request.method == 'POST':
        stock_name = request.form['stock_name']



        # Run the generate_plots function in a separate process
        process = multiprocessing.Process(target=generate_plots, args=(stock_name,))
        process.start()
        process.join()  # Wait for the process to finish before rendering the template

        session['show_result'] = True  # Set show_result to True for initial display
        session['stock_name'] = stock_name
        return render_template('project.html', show_result=session['show_result'], stock_name=session['stock_name'])

    session['show_result'] = False  # Set show_result to False when the page is refreshed
    return render_template('project.html', show_result=session['show_result'])


if __name__ == '__main__':
    app.run()

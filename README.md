Before the following steps, please make sure that you have a MySQL connection with host="127.0.0.1", port=3306, user="root", password="1234" and database="ChessDB". Also make sure that you have python and pip installed in your system.

- First open a command shell on the same directory as run.py.
- Download the required packages by running:
  ``` pip install -r requirements.txt ```
- Next:
  - To run the app with initialization (reset data, reload triggers and procedures), run the command:
   ``` python run.py initialize ```
  - To run the app without reset, run the command:
    ``` python run.py ```
- Your app will be accessible at http://127.0.0.1:5000


import random
import time
import json
from flask import Flask, request, render_template, jsonify
import openai

# Set up OpenAI API key
openai.api_key = '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'

# Initialize the Flask app
app = Flask(__name__)

# List of famous people and their possible alternative names
famous_people = {
    # Statesmen
    "Julius Caesar": [
        "julius caesar", "caesar", "gaius julius caesar", "dictator caesar",
        "emperor caesar", "j caesar"
    ],
    "Augustus": [
        "augustus", "octavian", "gaius octavius", "caesar augustus",
        "octavius", "emperor augustus"
    ],
    "Napoleon Bonaparte": [
        "napoleon", "napoleon bonaparte", "napoleon i", "emperor napoleon",
        "bonaparte", "napoleon b."
    ],
    "Winston Churchill": [
        "winston churchill", "churchill", "winston", "sir winston churchill",
        "winston leonard spencer-churchill", "prime minister churchill"
    ],
    "Nelson Mandela": [
        "nelson mandela", "mandela", "nelson rolihlahla mandela", 
        "madiba", "president mandela", "tata mandela"
    ],
    "Mahatma Gandhi": [
        "mahatma gandhi", "gandhi", "mohandas gandhi", "mohandas karamchand gandhi", 
        "bapu", "mohandas k. gandhi"
    ],
    "Abraham Lincoln": [
        "abraham lincoln", "lincoln", "abe lincoln", "abraham l", "abe", 
        "president lincoln", "honest abe"
    ],
    "Franklin D. Roosevelt": [
        "franklin d. roosevelt", "fdr", "roosevelt", "franklin roosevelt", 
        "franklin delano roosevelt", "frank roosevelt", "franklin d r", 
        "delano roosevelt", "president roosevelt"
    ],
    "George Washington": [
        "george washington", "washington", "george w", "g washington", 
        "george w.", "general washington", "president washington"
    ],
    "Ronald Reagan": [
        "ronald reagan", "reagan", "ron reagan", "ronald wilson reagan", 
        "president reagan", "ronnie reagan"
    ],
    "Barack Obama": [
        "barack obama", "obama", "barack h. obama", "barack hussein obama", 
        "barry obama", "president obama", "b. obama"
    ],
    "Vladimir Lenin": [
        "vladimir lenin", "lenin", "vladimir ilyich lenin", "ulyanov", 
        "vladimir i. lenin", "comrade lenin"
    ],
    "Joseph Stalin": [
        "joseph stalin", "stalin", "josef stalin", "josef vissarionovich stalin", 
        "comrade stalin", "generalissimo stalin"
    ],
    "Vladimir Putin": [
        "vladimir putin", "putin", "vladimir vladimirovich putin", "vlady putin", 
        "president putin", "v. putin"
    ],
    "Margaret Thatcher": [
        "margaret thatcher", "thatcher", "maggie thatcher", "the iron lady", 
        "margaret hilda thatcher", "prime minister thatcher"
    ],
    "Angela Merkel": [
        "angela merkel", "merkel", "angela dorothea merkel", 
        "chancellor merkel", "a. merkel"
    ],
    "Charles de Gaulle": [
        "charles de gaulle", "de gaulle", "charles andré joseph marie de gaulle", 
        "general de gaulle", "president de gaulle"
    ],
    "Jawaharlal Nehru": [
        "jawaharlal nehru", "nehru", "pandit nehru", "chacha nehru", 
        "prime minister nehru", "j nehru"
    ],
}



# Variables to track the game
start_time = None
question_count = 0
selected_person = None
selected_alternatives = []

# File to store high scores
HIGH_SCORES_FILE = 'high_scores.json'

def load_high_scores():
    """Loads high scores from the file."""
    try:
        with open(HIGH_SCORES_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'fastest_time': None, 'lowest_questions': None}

def save_high_scores(high_scores):
    """Saves high scores to the file."""
    with open(HIGH_SCORES_FILE, 'w') as file:
        json.dump(high_scores, file)

# Load high scores at startup
high_scores = load_high_scores()

def select_new_person():
    """Selects a new random famous person and its alternatives."""
    global selected_person, selected_alternatives
    selected_person = random.choice(list(famous_people.keys()))
    selected_alternatives = famous_people[selected_person]
    print(f"Selected person for this session (developer info): {selected_person}")

@app.route('/')
def index():
    global start_time, question_count
    start_time = time.time()  # Start the timer
    question_count = 0  # Reset the question count
    select_new_person()  # Select a new person at the start of the game
    return render_template('index.html', high_scores=high_scores)

@app.route('/ask', methods=['POST'])
def ask():
    global question_count
    question = request.json.get('question')
    question_count += 1

    # Check if the user's guess matches any variation of the selected person
    if any(name in question.lower() for name in selected_alternatives):
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        update_high_scores(duration, question_count)  # Update high scores
        save_high_scores(high_scores)  # Save high scores to the file
        select_new_person()  # Choose a new person for the next round
        return jsonify({
            'answer': f"Yes, I am {selected_person}! You guessed it in {question_count} questions and {duration} seconds.",
            'success': True,
            'time_taken': duration,
            'question_count': question_count
        })

    try:
        # Use the updated API for GPT-3.5 Turbo to answer yes/no questions
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"The selected person is {selected_person}. You will be asked Yes or No questions about the personality. Respond Yes or No. If the question is not a yes/no question, then reply Invalid Question"},
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message["content"].strip().lower()

        # Ensure the response is only "yes" or "no"
        if "yes" in answer:
            answer = "Yes"
        elif "no" in answer:
            answer = "No"
        else:
            answer = "I can only answer yes or no."

        return jsonify({'answer': answer, 'success': False})

    except Exception as e:
        return jsonify({'answer': f"Error: {str(e)}", 'success': False})

def update_high_scores(time, questions):
    """Updates the high scores for fastest time and lowest questions."""
    global high_scores
    if high_scores['fastest_time'] is None or time < high_scores['fastest_time']:
        high_scores['fastest_time'] = time
    if high_scores['lowest_questions'] is None or questions < high_scores['lowest_questions']:
        high_scores['lowest_questions'] = questions

if __name__ == '__main__':
    app.run(debug=True)

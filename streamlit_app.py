import streamlit as st
import sqlite3
import pandas as pd
import json
import uuid
from datetime import datetime
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Form Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
def init_database():
    conn = sqlite3.connect('forms.db')
    cursor = conn.cursor()
    
    # Create forms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            questions TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_published BOOLEAN DEFAULT FALSE,
            settings TEXT
        )
    ''')
    
    # Create responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id TEXT PRIMARY KEY,
            form_id TEXT NOT NULL,
            answers TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT,
            ip_address TEXT,
            FOREIGN KEY (form_id) REFERENCES forms (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Helper functions
def generate_unique_id():
    return f"form_{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"

def save_form(form_data):
    conn = sqlite3.connect('forms.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO forms 
        (id, title, questions, last_modified, is_published, settings)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        form_data['id'],
        form_data['title'],
        json.dumps(form_data['questions']),
        datetime.now(),
        form_data.get('is_published', False),
        json.dumps(form_data.get('settings', {}))
    ))
    
    conn.commit()
    conn.close()

def load_form(form_id):
    conn = sqlite3.connect('forms.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM forms WHERE id = ?', (form_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'title': result[1],
            'questions': json.loads(result[2]),
            'created_at': result[3],
            'last_modified': result[4],
            'is_published': bool(result[5]),
            'settings': json.loads(result[6]) if result[6] else {}
        }
    return None

def get_all_forms():
    conn = sqlite3.connect('forms.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, title, created_at, is_published FROM forms ORDER BY last_modified DESC')
    results = cursor.fetchall()
    conn.close()
    
    return [{'id': r[0], 'title': r[1], 'created_at': r[2], 'is_published': bool(r[3])} for r in results]

def save_response(form_id, answers):
    conn = sqlite3.connect('forms.db')
    cursor = conn.cursor()
    
    response_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO responses 
        (id, form_id, answers, submitted_at, user_agent, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        response_id,
        form_id,
        json.dumps(answers),
        datetime.now(),
        "Streamlit App",
        "localhost"
    ))
    
    conn.commit()
    conn.close()
    return response_id

def get_form_responses(form_id):
    conn = sqlite3.connect('forms.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM responses WHERE form_id = ? ORDER BY submitted_at DESC', (form_id,))
    results = cursor.fetchall()
    conn.close()
    
    return [{
        'id': r[0],
        'form_id': r[1],
        'answers': json.loads(r[2]),
        'submitted_at': r[3],
        'user_agent': r[4],
        'ip_address': r[5]
    } for r in results]

def calculate_screening_status(answers, total_questions):
    answered = len([a for a in answers.values() if a])
    percentage = answered / total_questions if total_questions > 0 else 0
    
    if percentage == 1.0:
        return "Passed"
    elif percentage > 0.5:
        return "Pending"
    else:
        return "Failed"

# Initialize session state
if 'current_form' not in st.session_state:
    st.session_state.current_form = {
        'id': generate_unique_id(),
        'title': 'Untitled Form',
        'questions': [],
        'is_published': False,
        'settings': {
            'custom_message': 'Thank you for your participation!'
        }
    }

if 'mode' not in st.session_state:
    st.session_state.mode = 'builder'

if 'selected_form_id' not in st.session_state:
    st.session_state.selected_form_id = None

# Main app
def main():
    st.title("📋 Form Generator with Shareable Links")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        mode = st.radio(
            "Choose Mode:",
            ["🛠️ Form Builder", "📝 Fill Form", "📊 View Responses", "📚 My Forms"],
            key="mode_selector"
        )
        
        if mode == "📚 My Forms":
            show_forms_list()
        
    # Main content based on mode
    if mode == "🛠️ Form Builder":
        show_form_builder()
    elif mode == "📝 Fill Form":
        show_form_filler()
    elif mode == "📊 View Responses":
        show_responses_viewer()

def show_forms_list():
    st.sidebar.subheader("Your Forms")
    forms = get_all_forms()
    
    if not forms:
        st.sidebar.info("No forms created yet.")
        return
    
    for form in forms:
        with st.sidebar.expander(f"📋 {form['title'][:20]}{'...' if len(form['title']) > 20 else ''}"):
            st.write(f"**Created:** {form['created_at'][:16]}")
            st.write(f"**Status:** {'🟢 Published' if form['is_published'] else '🔴 Draft'}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", key=f"edit_{form['id']}"):
                    st.session_state.current_form = load_form(form['id'])
                    st.session_state.selected_form_id = form['id']
                    st.rerun()
            
            with col2:
                if st.button("Delete", key=f"delete_{form['id']}"):
                    delete_form(form['id'])
                    st.rerun()

def delete_form(form_id):
    conn = sqlite3.connect('forms.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM forms WHERE id = ?', (form_id,))
    cursor.execute('DELETE FROM responses WHERE form_id = ?', (form_id,))
    conn.commit()
    conn.close()
    st.success("Form deleted successfully!")

def show_form_builder():
    st.header("🛠️ Form Builder")
    
    # Form settings
    col1, col2 = st.columns([3, 1])
    
    with col1:
        title = st.text_input("Form Title", value=st.session_state.current_form['title'])
        st.session_state.current_form['title'] = title
    
    with col2:
        if st.button("💾 Save Form"):
            save_form(st.session_state.current_form)
            st.success("Form saved!")
    
    # Form info
    with st.expander("📋 Form Information"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Form ID", st.session_state.current_form['id'])
        with col2:
            st.metric("Questions", len(st.session_state.current_form['questions']))
        with col3:
            status = "Published" if st.session_state.current_form['is_published'] else "Draft"
            st.metric("Status", status)
    
    # Question builder
    st.subheader("Add Questions")
    
    question_type = st.selectbox(
        "Question Type",
        ["Short Text", "Paragraph", "Multiple Choice", "Checkboxes", "Dropdown", "Number", "Email", "Scale"]
    )
    
    with st.form("add_question_form"):
        question_text = st.text_input("Question Text")
        description = st.text_input("Description (optional)")
        required = st.checkbox("Required")
        
        # Question-specific options
        options = []
        if question_type in ["Multiple Choice", "Checkboxes", "Dropdown"]:
            st.write("Options:")
            num_options = st.number_input("Number of options", min_value=2, max_value=10, value=3)
            for i in range(num_options):
                option = st.text_input(f"Option {i+1}", key=f"option_{i}")
                if option:
                    options.append(option)
        
        if st.form_submit_button("Add Question"):
            if question_text:
                question_data = {
                    'text': question_text,
                    'description': description,
                    'type': question_type.lower().replace(' ', '-'),
                    'required': required
                }
                
                if options:
                    question_data['options'] = options
                
                st.session_state.current_form['questions'].append(question_data)
                st.success("Question added!")
                st.rerun()
    
    # Show current questions
    if st.session_state.current_form['questions']:
        st.subheader("Current Questions")
        for i, q in enumerate(st.session_state.current_form['questions']):
            with st.expander(f"Question {i+1}: {q['text'][:50]}{'...' if len(q['text']) > 50 else ''}"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Type:** {q['type'].title()}")
                    st.write(f"**Required:** {'Yes' if q['required'] else 'No'}")
                    if 'options' in q:
                        st.write(f"**Options:** {', '.join(q['options'])}")
                with col2:
                    if st.button("🗑️ Delete", key=f"del_q_{i}"):
                        st.session_state.current_form['questions'].pop(i)
                        st.rerun()
    
    # Publish form
    st.subheader("📤 Publish & Share")
    
    if st.button("🚀 Generate Shareable Link"):
        st.session_state.current_form['is_published'] = True
        save_form(st.session_state.current_form)
        
        # Generate shareable URL
        base_url = "http://localhost:8501"  # Change this for deployment
        shareable_url = f"{base_url}?form_id={st.session_state.current_form['id']}&mode=fill"
        
        st.success("Form published successfully!")
        st.code(shareable_url, language="text")
        
        # Generate embed code
        embed_code = f'''<iframe src="{shareable_url}" width="100%" height="600" frameborder="0"></iframe>'''
        st.text_area("Embed Code:", embed_code, height=100)

def show_form_filler():
    st.header("📝 Fill Form")
    
    # Get form ID from URL params or user input
    form_id = st.experimental_get_query_params().get('form_id', [None])[0]
    
    if not form_id:
        form_id = st.text_input("Enter Form ID:")
    
    if form_id:
        form_data = load_form(form_id)
        
        if not form_data:
            st.error("Form not found!")
            return
        
        if not form_data['is_published']:
            st.warning("This form is not published yet.")
            return
        
        st.subheader(form_data['title'])
        
        # Create form
        with st.form("response_form"):
            answers = {}
            
            for i, question in enumerate(form_data['questions']):
                st.write(f"**Question {i+1}:** {question['text']}")
                if question.get('description'):
                    st.caption(question['description'])
                
                q_type = question['type']
                key = f"q_{i}"
                
                if q_type == 'short-text':
                    answers[i] = st.text_input("", key=key)
                elif q_type == 'paragraph':
                    answers[i] = st.text_area("", key=key)
                elif q_type == 'multiple-choice':
                    answers[i] = st.radio("", question['options'], key=key)
                elif q_type == 'checkboxes':
                    selected = []
                    for opt in question['options']:
                        if st.checkbox(opt, key=f"{key}_{opt}"):
                            selected.append(opt)
                    answers[i] = selected
                elif q_type == 'dropdown':
                    answers[i] = st.selectbox("", [""] + question['options'], key=key)
                elif q_type == 'number':
                    answers[i] = st.number_input("", key=key)
                elif q_type == 'email':
                    answers[i] = st.text_input("", key=key, placeholder="email@example.com")
                elif q_type == 'scale':
                    answers[i] = st.slider("", 1, 10, 5, key=key)
                
                st.write("---")
            
            if st.form_submit_button("Submit Response"):
                # Validate required fields
                valid = True
                for i, question in enumerate(form_data['questions']):
                    if question['required'] and not answers.get(i):
                        st.error(f"Question {i+1} is required!")
                        valid = False
                
                if valid:
                    save_response(form_id, answers)
                    st.success(form_data['settings'].get('custom_message', 'Thank you for your response!'))
                    st.balloons()

def show_responses_viewer():
    st.header("📊 Response Viewer")
    
    # Form selector
    forms = get_all_forms()
    if not forms:
        st.info("No forms available. Create a form first!")
        return
    
    form_options = {f"{f['title']} ({f['id']})": f['id'] for f in forms}
    selected_form_title = st.selectbox("Select Form:", list(form_options.keys()))
    
    if selected_form_title:
        form_id = form_options[selected_form_title]
        form_data = load_form(form_id)
        responses = get_form_responses(form_id)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Responses", len(responses))
        with col2:
            passed = len([r for r in responses if calculate_screening_status(r['answers'], len(form_data['questions'])) == "Passed"])
            st.metric("Passed", passed)
        with col3:
            if len(responses) > 0:
                pass_rate = (passed / len(responses)) * 100
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
        
        # Export functionality
        if responses:
            if st.button("📥 Export as CSV"):
                # Create DataFrame
                export_data = []
                for r in responses:
                    row = {
                        'Response ID': r['id'],
                        'Submitted At': r['submitted_at'],
                        'Screening Status': calculate_screening_status(r['answers'], len(form_data['questions']))
                    }
                    
                    # Add answers
                    for i, question in enumerate(form_data['questions']):
                        answer = r['answers'].get(str(i), '')
                        if isinstance(answer, list):
                            answer = ', '.join(answer)
                        row[f"Q{i+1}: {question['text'][:30]}..."] = answer
                    
                    export_data.append(row)
                
                df = pd.DataFrame(export_data)
                
                # Create download link
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="responses.csv">Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
        
        # Show responses
        for i, response in enumerate(responses):
            with st.expander(f"Response #{i+1} - {response['submitted_at'][:16]}"):
                status = calculate_screening_status(response['answers'], len(form_data['questions']))
                
                if status == "Passed":
                    st.success(f"Status: {status}")
                elif status == "Pending":
                    st.warning(f"Status: {status}")
                else:
                    st.error(f"Status: {status}")
                
                for j, question in enumerate(form_data['questions']):
                    answer = response['answers'].get(str(j), 'No answer')
                    if isinstance(answer, list):
                        answer = ', '.join(answer)
                    st.write(f"**{question['text']}:** {answer}")

if __name__ == "__main__":
    main()

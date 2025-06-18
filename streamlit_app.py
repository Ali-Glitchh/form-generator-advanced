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

# Enhanced question types
QUESTION_TYPES = [
    "Short Text", "Paragraph", "Multiple Choice", "Checkboxes", 
    "Dropdown", "Number", "Email", "Scale", "Grid", "Likert Scale", "Multiple Grids"
]

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

def check_skip_logic(question, answer, all_questions):
    """Check if skip logic should be applied based on the answer"""
    if 'skipLogic' not in question or not question['skipLogic']:
        return None
    
    for rule in question['skipLogic']:
        should_skip = False
        
        if question['type'] in ['multiple-choice', 'dropdown', 'likert']:
            should_skip = answer == rule.get('option')
        elif question['type'] == 'checkbox':
            should_skip = isinstance(answer, list) and rule.get('option') in answer
        elif question['type'] in ['short-text', 'paragraph', 'email']:
            should_skip = answer == rule.get('value')
        elif question['type'] in ['number', 'scale']:
            operator = rule.get('operator', 'equals')
            value = rule.get('value')
            if operator == 'equals':
                should_skip = answer == value
            elif operator == 'greater':
                should_skip = answer > value
            elif operator == 'less':
                should_skip = answer < value
        
        if should_skip:
            return rule.get('target')
    
    return None

def should_hide_option(question, option_value, all_answers, all_questions):
    """Check if an option should be hidden based on option rules"""
    if 'optionRules' not in question or not question['optionRules']:
        return False
    
    for rule in question['optionRules']:
        source_question_idx = rule.get('sourceQuestion')
        source_value = rule.get('sourceValue')
        hidden_options = rule.get('hiddenOptions', [])
        
        if (source_question_idx is not None and 
            source_value and 
            option_value in hidden_options):
            
            source_answer = all_answers.get(source_question_idx)
            
            if isinstance(source_answer, list):
                if source_value in source_answer:
                    return True
            else:
                if source_answer == source_value:
                    return True
    
    return False

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
    
    # Advanced form settings
    with st.expander("⚙️ Advanced Settings"):
        settings = st.session_state.current_form.get('settings', {})
        
        custom_message = st.text_area(
            "Custom completion message:",
            value=settings.get('custom_message', 'Thank you for your participation!')
        )
        
        enable_screening = st.checkbox(
            "Enable screening (track completion status)",
            value=settings.get('enable_screening', False)
        )
        
        require_full_completion = st.checkbox(
            "Require full completion for 'Passed' status",
            value=settings.get('require_full_completion', True)
        )
        
        st.session_state.current_form['settings'] = {
            'custom_message': custom_message,
            'enable_screening': enable_screening,
            'require_full_completion': require_full_completion
        }
    
    # Question builder
    st.subheader("Add Questions")
    
    question_type = st.selectbox(
        "Question Type",
        QUESTION_TYPES
    )
    
    with st.form("add_question_form"):
        question_text = st.text_input("Question Text")
        description = st.text_input("Description (optional)")
        required = st.checkbox("Required")
        
        # Question-specific options
        options = []
        if question_type in ["Multiple Choice", "Checkboxes", "Dropdown", "Likert Scale"]:
            st.write("Options:")
            num_options = st.number_input("Number of options", min_value=2, max_value=10, value=3)
            for i in range(num_options):
                option = st.text_input(f"Option {i+1}", key=f"option_{i}")
                if option:
                    options.append(option)
        elif question_type == "Scale":
            min_val = st.number_input("Minimum value", value=1)
            max_val = st.number_input("Maximum value", value=10)
            options = [str(i) for i in range(min_val, max_val + 1)]
        
        # Advanced logic settings
        with st.expander("🔀 Advanced Logic"):
            enable_skip_logic = st.checkbox("Enable skip logic for this question")
            skip_rules = []
            
            if enable_skip_logic:
                st.write("Skip Logic Rules:")
                num_rules = st.number_input("Number of skip rules", min_value=1, max_value=5, value=1)
                
                for i in range(num_rules):
                    st.write(f"**Rule {i+1}:**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if question_type in ["Multiple Choice", "Dropdown", "Likert Scale"]:
                            condition_option = st.selectbox(f"If answer is:", options if options else [""], key=f"skip_option_{i}")
                        elif question_type in ["Short Text", "Paragraph", "Email"]:
                            condition_option = st.text_input(f"If answer equals:", key=f"skip_text_{i}")
                        elif question_type in ["Number", "Scale"]:
                            operator = st.selectbox(f"Operator:", ["equals", "greater", "less"], key=f"skip_op_{i}")
                            condition_value = st.number_input(f"Value:", key=f"skip_val_{i}")
                            condition_option = {"operator": operator, "value": condition_value}
                        else:
                            condition_option = None
                    
                    with col2:
                        target_question = st.number_input(
                            f"Skip to question #:",
                            min_value=1,
                            max_value=len(st.session_state.current_form['questions']) + 10,
                            value=len(st.session_state.current_form['questions']) + 2,
                            key=f"skip_target_{i}"
                        )
                    
                    with col3:
                        end_form = st.checkbox(f"End form", key=f"skip_end_{i}")
                    
                    if condition_option:
                        rule = {
                            "option" if isinstance(condition_option, str) else "condition": condition_option,
                            "target": "end" if end_form else target_question - 1
                        }
                        skip_rules.append(rule)
            
            # Option hiding rules
            enable_option_rules = st.checkbox("Enable option hiding rules")
            option_rules = []
            
            if enable_option_rules and question_type in ["Multiple Choice", "Checkboxes", "Dropdown"]:
                st.write("Option Hiding Rules:")
                
                source_questions = [f"Question {i+1}: {q['text'][:30]}" for i, q in enumerate(st.session_state.current_form['questions'])]
                
                if source_questions:
                    source_q_idx = st.selectbox("Based on question:", range(len(source_questions)), format_func=lambda x: source_questions[x])
                    source_question = st.session_state.current_form['questions'][source_q_idx]
                    
                    if 'options' in source_question:
                        source_value = st.selectbox("When answer is:", source_question['options'])
                        hidden_options = st.multiselect("Hide these options:", options if options else [])
                        
                        if source_value and hidden_options:
                            option_rules.append({
                                "sourceQuestion": source_q_idx,
                                "sourceValue": source_value,
                                "hiddenOptions": hidden_options
                            })
        
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
                
                if enable_skip_logic and skip_rules:
                    question_data['skipLogic'] = skip_rules
                
                if enable_option_rules and option_rules:
                    question_data['optionRules'] = option_rules
                
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
                    if 'skipLogic' in q:
                        st.write(f"**Skip Logic:** {len(q['skipLogic'])} rule(s)")
                    if 'optionRules' in q:
                        st.write(f"**Option Rules:** {len(q['optionRules'])} rule(s)")
                with col2:
                    if st.button("✏️ Edit", key=f"edit_q_{i}"):
                        st.info("Click on question details above to modify")
                    if st.button("🗑️ Delete", key=f"del_q_{i}"):
                        st.session_state.current_form['questions'].pop(i)
                        st.rerun()
    
    # Preview form
    if st.session_state.current_form['questions']:
        st.subheader("👀 Form Preview")
        
        if st.button("🔍 Preview Form", use_container_width=True):
            st.info("**Preview Mode** - This is how your form will look to respondents:")
            
            with st.container():
                st.markdown("---")
                st.write(f"### {st.session_state.current_form['title']}")
                
                for i, question in enumerate(st.session_state.current_form['questions']):
                    st.write(f"**Question {i+1}:** {question['text']}")
                    if question.get('description'):
                        st.caption(question['description'])
                    
                    q_type = question['type']
                    
                    # Show preview of question input
                    if q_type == 'short-text':
                        st.text_input("", placeholder="Short text answer...", disabled=True, key=f"preview_{i}")
                    elif q_type == 'paragraph':
                        st.text_area("", placeholder="Longer text answer...", disabled=True, key=f"preview_{i}")
                    elif q_type in ['multiple-choice', 'dropdown', 'likert-scale']:
                        if 'options' in question:
                            if q_type == 'dropdown':
                                st.selectbox("", ["Select an option..."] + question['options'], disabled=True, key=f"preview_{i}")
                            else:
                                st.radio("", question['options'], disabled=True, key=f"preview_{i}")
                    elif q_type == 'checkboxes':
                        if 'options' in question:
                            for opt in question['options']:
                                st.checkbox(opt, disabled=True, key=f"preview_{i}_{opt}")
                    elif q_type == 'number':
                        st.number_input("", disabled=True, key=f"preview_{i}")
                    elif q_type == 'email':
                        st.text_input("", placeholder="email@example.com", disabled=True, key=f"preview_{i}")
                    elif q_type == 'scale':
                        options = question.get('options', [str(i) for i in range(1, 11)])
                        min_val, max_val = int(options[0]), int(options[-1])
                        st.slider("", min_val, max_val, min_val, disabled=True, key=f"preview_{i}")
                    
                    # Show logic indicators
                    logic_info = []
                    if 'skipLogic' in question:
                        logic_info.append(f"Skip Logic: {len(question['skipLogic'])} rule(s)")
                    if 'optionRules' in question:
                        logic_info.append(f"Option Rules: {len(question['optionRules'])} rule(s)")
                    
                    if logic_info:
                        st.caption("🔀 " + " • ".join(logic_info))
                    
                    if question['required']:
                        st.caption("⚠️ Required")
                    
                    st.write("---")
                
                st.button("Submit Response", disabled=True, use_container_width=True)
                st.markdown("---")
    
    # Publish form
    st.subheader("📤 Publish & Share")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Generate Shareable Link", use_container_width=True):
            st.session_state.current_form['is_published'] = True
            save_form(st.session_state.current_form)
            
            # Generate shareable URL
            base_url = "http://localhost:8501"  # Change this for deployment
            shareable_url = f"{base_url}?form_id={st.session_state.current_form['id']}&mode=fill"
            
            st.success("Form published successfully!")
            
            # Show shareable link
            st.text_input("Shareable Link:", shareable_url, key="shareable_link")
            
            # Copy to clipboard button (simulated)
            if st.button("📋 Copy Link", use_container_width=True):
                st.success("Link copied to clipboard! (Simulated)")
    
    with col2:
        if st.session_state.current_form['is_published']:
            if st.button("📊 View Responses", use_container_width=True):
                st.session_state.mode = 'responses'
                st.rerun()
    
    # Additional sharing options
    if st.session_state.current_form['is_published']:
        with st.expander("🔗 Advanced Sharing Options"):
            base_url = "http://localhost:8501"
            form_url = f"{base_url}?form_id={st.session_state.current_form['id']}&mode=fill"
            
            # QR Code (simulated - in real deployment, you'd generate actual QR codes)
            st.write("**QR Code:**")
            st.info("📱 QR Code would be generated here for easy mobile sharing")
            
            # Embed code
            st.write("**Embed Code:**")
            embed_code = f'''<iframe src="{form_url}" width="100%" height="600" frameborder="0" style="border-radius: 8px;"></iframe>'''
            st.code(embed_code, language="html")
            
            # Social sharing (simulated)
            st.write("**Share on Social Media:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📘 Facebook", use_container_width=True):
                    st.info("Would open Facebook share dialog")
            with col2:
                if st.button("🐦 Twitter", use_container_width=True):
                    st.info("Would open Twitter share dialog")
            with col3:
                if st.button("💼 LinkedIn", use_container_width=True):
                    st.info("Would open LinkedIn share dialog")
            
            # Email template
            st.write("**Email Template:**")
            email_subject = f"Please fill out: {st.session_state.current_form['title']}"
            email_body = f"""Hello,

I would like to invite you to participate in a survey: {st.session_state.current_form['title']}

Please click the link below to access the form:
{form_url}

Thank you for your time!"""
            
            st.text_area("Email Subject:", email_subject, height=50)
            st.text_area("Email Body:", email_body, height=150)

def show_form_filler():
    st.header("📝 Fill Form")
    
    # Get form ID from URL params or user input
    form_id = st.query_params.get('form_id', None)
    
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
        
        # Initialize answers in session state for dynamic form handling
        if f'answers_{form_id}' not in st.session_state:
            st.session_state[f'answers_{form_id}'] = {}
        
        if f'current_question_{form_id}' not in st.session_state:
            st.session_state[f'current_question_{form_id}'] = 0
        
        answers = st.session_state[f'answers_{form_id}']
        
        # Determine which questions to show based on skip logic
        visible_questions = []
        current_idx = 0
        
        while current_idx < len(form_data['questions']):
            question = form_data['questions'][current_idx]
            visible_questions.append((current_idx, question))
            
            # Check if we should skip questions based on previous answers
            if current_idx in answers:
                skip_target = check_skip_logic(question, answers[current_idx], form_data['questions'])
                if skip_target == "end":
                    break
                elif skip_target is not None and skip_target > current_idx:
                    current_idx = skip_target
                    continue
            
            current_idx += 1
        
        # Show progress
        progress = len([i for i in answers.keys() if answers[i]]) / len(form_data['questions']) if form_data['questions'] else 0
        st.progress(progress)
        st.caption(f"Progress: {int(progress * 100)}% ({len([i for i in answers.keys() if answers[i]])}/{len(form_data['questions'])} questions answered)")
        
        # Create form with dynamic questions
        with st.form("response_form"):
            form_changed = False
            
            for question_idx, question in visible_questions:
                st.write(f"**Question {question_idx + 1}:** {question['text']}")
                if question.get('description'):
                    st.caption(question['description'])
                
                q_type = question['type']
                key = f"q_{question_idx}"
                current_answer = answers.get(question_idx, '')
                
                # Handle different question types with dynamic option filtering
                if q_type == 'short-text':
                    new_answer = st.text_input("", value=current_answer, key=key)
                elif q_type == 'paragraph':
                    new_answer = st.text_area("", value=current_answer, key=key)
                elif q_type == 'multiple-choice':
                    # Filter options based on option rules
                    available_options = []
                    for opt in question.get('options', []):
                        if not should_hide_option(question, opt, answers, form_data['questions']):
                            available_options.append(opt)
                    
                    if available_options:
                        try:
                            default_idx = available_options.index(current_answer) if current_answer in available_options else 0
                        except:
                            default_idx = 0
                        new_answer = st.radio("", available_options, index=default_idx, key=key)
                    else:
                        st.info("No options available based on previous answers.")
                        new_answer = ""
                
                elif q_type == 'checkboxes':
                    available_options = []
                    for opt in question.get('options', []):
                        if not should_hide_option(question, opt, answers, form_data['questions']):
                            available_options.append(opt)
                    
                    if available_options:
                        selected = []
                        current_selected = current_answer if isinstance(current_answer, list) else []
                        for opt in available_options:
                            if st.checkbox(opt, value=opt in current_selected, key=f"{key}_{opt}"):
                                selected.append(opt)
                        new_answer = selected
                    else:
                        st.info("No options available based on previous answers.")
                        new_answer = []
                
                elif q_type == 'dropdown':
                    available_options = []
                    for opt in question.get('options', []):
                        if not should_hide_option(question, opt, answers, form_data['questions']):
                            available_options.append(opt)
                    
                    if available_options:
                        options_with_empty = [""] + available_options
                        try:
                            default_idx = options_with_empty.index(current_answer) if current_answer in options_with_empty else 0
                        except:
                            default_idx = 0
                        new_answer = st.selectbox("", options_with_empty, index=default_idx, key=key)
                    else:
                        st.info("No options available based on previous answers.")
                        new_answer = ""
                
                elif q_type == 'number':
                    new_answer = st.number_input("", value=float(current_answer) if current_answer else 0.0, key=key)
                elif q_type == 'email':
                    new_answer = st.text_input("", value=current_answer, key=key, placeholder="email@example.com")
                elif q_type == 'scale':
                    options = question.get('options', [str(i) for i in range(1, 11)])
                    min_val, max_val = int(options[0]), int(options[-1])
                    try:
                        default_val = int(current_answer) if current_answer else min_val
                    except:
                        default_val = min_val
                    new_answer = st.slider("", min_val, max_val, default_val, key=key)
                elif q_type == 'likert-scale':
                    available_options = []
                    for opt in question.get('options', []):
                        if not should_hide_option(question, opt, answers, form_data['questions']):
                            available_options.append(opt)
                    
                    if available_options:
                        try:
                            default_idx = available_options.index(current_answer) if current_answer in available_options else 0
                        except:
                            default_idx = 0
                        new_answer = st.select_slider("", available_options, value=available_options[default_idx], key=key)
                    else:
                        new_answer = ""
                
                # Update answer in session state
                if new_answer != current_answer:
                    answers[question_idx] = new_answer
                    form_changed = True
                
                st.write("---")
            
            # Submit button
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.form_submit_button("💾 Save Progress", use_container_width=True):
                    st.session_state[f'answers_{form_id}'] = answers
                    st.success("Progress saved!")
            
            with col2:
                if st.form_submit_button("🚀 Submit Final Response", use_container_width=True):
                    # Validate required fields for visible questions only
                    valid = True
                    for question_idx, question in visible_questions:
                        if question['required'] and not answers.get(question_idx):
                            st.error(f"Question {question_idx + 1} is required!")
                            valid = False
                    
                    if valid:
                        # Calculate screening status
                        settings = form_data.get('settings', {})
                        if settings.get('enable_screening', False):
                            status = calculate_screening_status(answers, len(form_data['questions']))
                            st.session_state[f'screening_status_{form_id}'] = status
                        
                        save_response(form_id, answers)
                        st.success(settings.get('custom_message', 'Thank you for your response!'))
                        
                        # Show screening status if enabled
                        if settings.get('enable_screening', False):
                            status = st.session_state.get(f'screening_status_{form_id}', 'Unknown')
                            if status == "Passed":
                                st.success(f"✅ Screening Status: {status}")
                            elif status == "Pending":
                                st.warning(f"⏳ Screening Status: {status}")
                            else:
                                st.error(f"❌ Screening Status: {status}")
                        
                        st.balloons()
                        
                        # Clear form data
                        if f'answers_{form_id}' in st.session_state:
                            del st.session_state[f'answers_{form_id}']
                        if f'current_question_{form_id}' in st.session_state:
                            del st.session_state[f'current_question_{form_id}']

def show_responses_viewer():
    st.header("📊 Response Viewer & Analytics")
    
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
        
        # Analytics overview
        st.subheader("📈 Analytics Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Responses", len(responses))
        
        with col2:
            if form_data['settings'].get('enable_screening', False):
                passed = len([r for r in responses if calculate_screening_status(r['answers'], len(form_data['questions'])) == "Passed"])
                st.metric("Passed", passed)
            else:
                complete_responses = len([r for r in responses if len(r['answers']) == len(form_data['questions'])])
                st.metric("Complete", complete_responses)
        
        with col3:
            if responses:
                if form_data['settings'].get('enable_screening', False):
                    passed = len([r for r in responses if calculate_screening_status(r['answers'], len(form_data['questions'])) == "Passed"])
                    pass_rate = (passed / len(responses)) * 100
                    st.metric("Pass Rate", f"{pass_rate:.1f}%")
                else:
                    complete_responses = len([r for r in responses if len(r['answers']) == len(form_data['questions'])])
                    completion_rate = (complete_responses / len(responses)) * 100
                    st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        with col4:
            if responses:
                avg_questions = sum(len(r['answers']) for r in responses) / len(responses)
                st.metric("Avg Questions Answered", f"{avg_questions:.1f}")
        
        # Question-by-question analysis
        if responses and form_data['questions']:
            st.subheader("📊 Question Analysis")
            
            for i, question in enumerate(form_data['questions']):
                with st.expander(f"Question {i+1}: {question['text'][:60]}..."):
                    # Get all answers for this question
                    question_answers = [r['answers'].get(str(i), '') for r in responses if str(i) in r['answers']]
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col2:
                        st.metric("Response Count", len(question_answers))
                        if question['required']:
                            st.metric("Required", "✅ Yes")
                        else:
                            st.metric("Required", "❌ No")
                    
                    with col1:
                        if question['type'] in ['multiple-choice', 'dropdown', 'likert-scale']:
                            # Count frequency of each option
                            answer_counts = {}
                            for ans in question_answers:
                                if ans:
                                    answer_counts[ans] = answer_counts.get(ans, 0) + 1
                            
                            if answer_counts:
                                import pandas as pd
                                df = pd.DataFrame(list(answer_counts.items()), columns=['Option', 'Count'])
                                df['Percentage'] = (df['Count'] / len(question_answers) * 100).round(1)
                                st.dataframe(df, use_container_width=True)
                                
                                # Simple bar chart
                                st.bar_chart(df.set_index('Option')['Count'])
                        
                        elif question['type'] == 'checkboxes':
                            # Handle multiple selections
                            all_options = set()
                            for ans in question_answers:
                                if isinstance(ans, list):
                                    all_options.update(ans)
                                elif ans:
                                    all_options.add(ans)
                            
                            option_counts = {}
                            for option in all_options:
                                count = sum(1 for ans in question_answers 
                                          if (isinstance(ans, list) and option in ans) or ans == option)
                                option_counts[option] = count
                            
                            if option_counts:
                                df = pd.DataFrame(list(option_counts.items()), columns=['Option', 'Count'])
                                df['Percentage'] = (df['Count'] / len(question_answers) * 100).round(1)
                                st.dataframe(df, use_container_width=True)
                                st.bar_chart(df.set_index('Option')['Count'])
                        
                        elif question['type'] in ['number', 'scale']:
                            numeric_answers = [float(ans) for ans in question_answers if ans and str(ans).replace('.','').replace('-','').isdigit()]
                            if numeric_answers:
                                st.metric("Average", f"{sum(numeric_answers) / len(numeric_answers):.2f}")
                                st.metric("Min/Max", f"{min(numeric_answers)} / {max(numeric_answers)}")
                                
                                # Simple histogram using bar chart
                                df = pd.DataFrame({'Values': numeric_answers})
                                st.line_chart(df)
                        
                        else:
                            # Text responses - show word count stats
                            text_lengths = [len(str(ans).split()) for ans in question_answers if ans]
                            if text_lengths:
                                st.metric("Avg Words", f"{sum(text_lengths) / len(text_lengths):.1f}")
                                st.metric("Response Rate", f"{len(text_lengths) / len(responses) * 100:.1f}%")
        
        # Export functionality
        if responses:
            st.subheader("📥 Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Export Responses as CSV", use_container_width=True):
                    # Create detailed DataFrame
                    export_data = []
                    for r in responses:
                        row = {
                            'Response ID': r['id'],
                            'Submitted At': r['submitted_at'],
                        }
                        
                        # Add screening status if enabled
                        if form_data['settings'].get('enable_screening', False):
                            row['Screening Status'] = calculate_screening_status(r['answers'], len(form_data['questions']))
                        
                        # Add answers
                        for i, question in enumerate(form_data['questions']):
                            answer = r['answers'].get(str(i), '')
                            if isinstance(answer, list):
                                answer = ', '.join(answer)
                            row[f"Q{i+1}: {question['text'][:50]}"] = answer
                        
                        export_data.append(row)
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"responses_{form_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("📊 Export Analytics Summary", use_container_width=True):
                    # Create analytics summary
                    summary_data = {
                        'Form Title': [form_data['title']],
                        'Form ID': [form_id],
                        'Total Questions': [len(form_data['questions'])],
                        'Total Responses': [len(responses)],
                        'Screening Enabled': [form_data['settings'].get('enable_screening', False)],
                        'Export Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                    }
                    
                    if form_data['settings'].get('enable_screening', False):
                        passed = len([r for r in responses if calculate_screening_status(r['answers'], len(form_data['questions'])) == "Passed"])
                        summary_data['Passed Responses'] = [passed]
                        summary_data['Pass Rate %'] = [f"{(passed / len(responses) * 100):.1f}" if responses else "0"]
                    
                    df = pd.DataFrame(summary_data)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="💾 Download Summary",
                        data=csv,
                        file_name=f"analytics_{form_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        # Individual responses
        if responses:
            st.subheader("📋 Individual Responses")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                if form_data['settings'].get('enable_screening', False):
                    status_filter = st.selectbox("Filter by status:", ["All", "Passed", "Pending", "Failed"])
                else:
                    status_filter = "All"
            
            with col2:
                sort_order = st.selectbox("Sort by:", ["Newest First", "Oldest First"])
            
            # Apply filters
            filtered_responses = responses.copy()
            
            if status_filter != "All":
                filtered_responses = [
                    r for r in filtered_responses 
                    if calculate_screening_status(r['answers'], len(form_data['questions'])) == status_filter
                ]
            
            if sort_order == "Oldest First":
                filtered_responses.reverse()
            
            # Show responses
            for i, response in enumerate(filtered_responses):
                with st.expander(f"Response #{i+1} - {response['submitted_at'][:16]}"):
                    
                    # Status indicator
                    if form_data['settings'].get('enable_screening', False):
                        status = calculate_screening_status(response['answers'], len(form_data['questions']))
                        
                        if status == "Passed":
                            st.success(f"✅ Status: {status}")
                        elif status == "Pending":
                            st.warning(f"⏳ Status: {status}")
                        else:
                            st.error(f"❌ Status: {status}")
                    
                    # Show answers
                    answered_count = 0
                    for j, question in enumerate(form_data['questions']):
                        answer = response['answers'].get(str(j), 'No answer')
                        
                        if answer and answer != 'No answer':
                            answered_count += 1
                        
                        if isinstance(answer, list):
                            answer = ', '.join(answer) if answer else 'No answer'
                        
                        # Color code based on whether question was answered
                        if answer and answer != 'No answer':
                            st.write(f"**{question['text']}:** {answer}")
                        else:
                            st.write(f"**{question['text']}:** _No answer_")
                    
                    # Response metadata
                    st.caption(f"Answered {answered_count}/{len(form_data['questions'])} questions • Response ID: {response['id']}")
        
        else:
            st.info("No responses received yet. Share your form to start collecting responses!")

if __name__ == "__main__":
    main()

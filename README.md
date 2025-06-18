# 📋 Form Generator with Advanced Logic & Shareable Links

A powerful, feature-rich form generator that creates dynamic, shareable forms with advanced conditional logic, skip patterns, and comprehensive analytics. Available in both standalone HTML and Streamlit versions.

## 🌟 Key Features

### 🏗️ Advanced Form Building
- **Multiple Question Types**: Short text, paragraphs, multiple choice, checkboxes, dropdowns, numbers, emails, scales, Likert scales, and grids
- **Conditional Logic**: Skip logic, conditional question hiding, and dynamic option filtering
- **Smart Validation**: Required field validation with custom error messages
- **Preview Mode**: Test your forms before publishing

### 🔀 Intelligent Flow Control
- **Skip Logic**: Jump to specific questions or end forms based on user responses
- **Conditional Questions**: Show/hide entire questions based on previous answers
- **Dynamic Options**: Hide specific options in multiple choice questions based on user input
- **Adaptive Paths**: Create personalized form experiences for different user types

### 📊 Screening & Analytics
- **Response Screening**: Automatic Pass/Pending/Failed status based on completion criteria
- **Progress Tracking**: Real-time progress indicators during form completion
- **Question Analytics**: Detailed breakdown of responses per question with charts
- **Response Filtering**: Sort and filter responses by status, date, and completion level

### 🔗 Sharing & Distribution
- **Shareable Links**: Generate unique URLs for easy form distribution
- **QR Code Support**: Mobile-friendly access via QR codes
- **Embed Codes**: iframe integration for websites and applications
- **Social Sharing**: Built-in sharing options for social media platforms
- **Email Templates**: Pre-formatted invitation emails

### 📈 Data Management
- **Real-time Dashboard**: Live response monitoring and analytics
- **CSV Export**: Detailed data export with response metadata
- **Analytics Export**: Summary statistics and completion rates
- **Response Management**: Individual response viewing and analysis

## 🚀 Quick Start

### HTML Version (Standalone)
```bash
# Clone the repository
git clone <repository-url>
cd form-generator

# Open in browser
python -m http.server 8000
# Navigate to http://localhost:8000/formgenerator.html
```

### Streamlit Version (Web App)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

## 📖 Usage Examples

### Basic Form Creation
1. **HTML Version**: Open `formgenerator.html` and use the visual form builder
2. **Streamlit Version**: Run the app and select "🛠️ Form Builder"
3. Add questions, configure logic, and publish
4. Share the generated link or embed code

### Advanced Logic Setup

#### Skip Logic Example:
```
Question: "Years of experience?"
Skip Rule: If < 2 years → Skip to Question 8
```

#### Option Hiding Example:
```
Question 1: "Programming languages?" (Checkboxes: JavaScript, Python, Java)
Question 2: "Preferred framework?" (Dropdown: React, Vue, Django, Flask)
Rule: Hide React/Vue if JavaScript not selected, Hide Django/Flask if Python not selected
```

#### Conditional Questions:
```
Question 1: "Are you a student?" (Yes/No)
Question 2: "What grade are you in?" (Only shown if Question 1 = "Yes")
```

## 🗂️ Project Structure

```
form-generator/
├── formgenerator.html          # Main HTML form generator
├── streamlit_app.py           # Streamlit web application
├── wrapper-example.html       # Integration example
├── integration-example.html   # Advanced integration demo
├── workflow-explanation.html  # Workflow documentation
├── wrapper-integration.css    # Styling for integrations
├── requirements.txt           # Python dependencies
├── DEMO_GUIDE.md             # Comprehensive demo scenarios
├── GITHUB_SETUP.md           # Deployment instructions
└── README.md                 # This file
```

## 🎯 Use Cases

### 📝 Surveys & Research
- Customer satisfaction surveys with adaptive questioning
- Academic research with conditional logic
- Market research with targeted follow-ups

### 💼 Business Applications
- Job application screening with skill-based routing
- Lead qualification forms with scoring
- Employee feedback with department-specific questions

### 🎓 Educational Assessment
- Adaptive learning assessments
- Student placement tests
- Course feedback with personalized paths

### 🏥 Healthcare & Screening
- Patient intake forms with symptom-based routing
- Health screening questionnaires
- Mental health assessments with safety protocols

## 🔧 Advanced Configuration

### Form Settings
```javascript
{
  "enable_screening": true,
  "require_full_completion": false,
  "custom_message": "Thank you for your participation!",
  "allow_multiple_submissions": false
}
```

### Skip Logic Configuration
```javascript
{
  "skipLogic": [
    {
      "option": "Yes",
      "target": 5  // Skip to question 5
    },
    {
      "condition": {"operator": "greater", "value": 18},
      "target": "end"  // End form
    }
  ]
}
```

### Option Rules
```javascript
{
  "optionRules": [
    {
      "sourceQuestion": 0,
      "sourceValue": "JavaScript",
      "hiddenOptions": ["Django", "Flask"]
    }
  ]
}
```

## 📊 Analytics Features

### Response Metrics
- Total responses and completion rates
- Pass/fail ratios for screening forms
- Average completion time and dropout points
- Question-specific response rates

### Visual Analytics
- Response distribution charts
- Completion funnel analysis
- Answer frequency graphs
- Screening status breakdown

### Export Options
- **Detailed CSV**: All responses with metadata
- **Analytics Summary**: Key metrics and statistics
- **Filtered Data**: Responses matching specific criteria

## 🔗 Integration Options

### Website Embedding
```html
<iframe src="http://your-domain.com?form_id=FORM_ID&mode=fill" 
        width="100%" height="600" frameborder="0">
</iframe>
```

### API Integration
Both versions provide programmatic access to form data for custom integrations.

### Webhook Support
Configure automatic notifications when forms are submitted (Streamlit version).

## 🛠️ Technical Details

### HTML Version
- **Frontend**: Vanilla JavaScript, CSS3, HTML5
- **Storage**: Browser localStorage
- **Features**: Offline capable, no server required
- **Deployment**: Static hosting (GitHub Pages, Netlify, etc.)

### Streamlit Version
- **Backend**: Python 3.7+, Streamlit, SQLite
- **Features**: Database persistence, advanced analytics
- **Deployment**: Streamlit Cloud, Heroku, Docker
- **Requirements**: See `requirements.txt`

## 🚀 Deployment

### Quick Deploy (Streamlit Cloud)
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy with one click

### Self-Hosted
1. Install Python 3.7+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `streamlit run streamlit_app.py`

### Static Hosting (HTML Version)
1. Upload files to any web server
2. Ensure HTTPS for localStorage access
3. Configure CORS if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

- **Documentation**: See `DEMO_GUIDE.md` for detailed examples
- **Setup Issues**: Check `GITHUB_SETUP.md` for deployment help
- **Integration Help**: Review example files in the repository

## 🔮 Roadmap

- [ ] Real-time collaboration on form building
- [ ] Advanced data visualization dashboard
- [ ] Integration with popular form platforms
- [ ] Mobile app for form management
- [ ] AI-powered form optimization suggestions

---

**Built with ❤️ for creating better forms and user experiences.**

# Form Generator with Shareable Links

A powerful, web-based form generator that creates shareable links for surveys and data collection with built-in screening capabilities.

## 🌟 Features

- **Visual Form Builder**: Drag-and-drop interface for creating forms
- **Multiple Question Types**: Text, multiple choice, checkboxes, dropdowns, scales, grids, and more
- **Shareable Links**: Generate unique URLs for each form
- **Response Collection**: Collect and manage responses with screening status
- **Data Export**: Export responses as CSV files
- **Skip Logic**: Conditional questions based on previous answers
- **Mobile Responsive**: Works on all devices
- **Embed Support**: Generate iframe codes for website integration

## 🚀 Quick Start

### HTML Version
1. Open `formgenerator.html` in your browser
2. Create your form using the visual builder
3. Generate a shareable link
4. Share the link to collect responses

### Streamlit Version
1. Install requirements: `pip install -r requirements.txt`
2. Run the app: `streamlit run streamlit_app.py`
3. Access at `http://localhost:8501`

## 📁 File Structure

```
├── formgenerator.html          # Main form generator (HTML/JS)
├── streamlit_app.py           # Streamlit version
├── requirements.txt           # Python dependencies
├── wrapper-example.html       # Example wrapper integration
├── integration-example.html   # Integration guide
├── workflow-explanation.html  # How-to guide
├── test-debug.html           # Debug version
├── wrapper-integration.css   # CSS for integration
└── README.md                # This file
```

## 💡 How It Works

1. **Create Forms**: Use the visual builder to create surveys
2. **Generate Links**: Each form gets a unique shareable URL
3. **Collect Responses**: People fill out clean, professional forms
4. **Screen Participants**: Automatic screening based on completion
5. **Export Data**: Download responses as CSV for analysis

## 🔗 Integration

### Direct Links
```html
<a href="formgenerator.html?form=YOUR_FORM_ID&mode=fill">Take Survey</a>
```

### Iframe Embedding
```html
<iframe src="formgenerator.html?form=YOUR_FORM_ID&mode=fill" width="100%" height="600"></iframe>
```

## 🛠️ Technical Details

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Storage**: Browser localStorage (HTML version) / SQLite (Streamlit version)
- **Backend**: Python/Streamlit (web app version)
- **Responsive**: Mobile-first design
- **No Dependencies**: HTML version works offline

## 📊 Question Types

- Short Text
- Paragraph Text
- Multiple Choice (Radio)
- Checkboxes
- Dropdown
- Number Input
- Email Input
- Scale (1-10)
- Grid Questions
- Likert Scale
- Multiple Grids

## 🎯 Use Cases

- Customer satisfaction surveys
- Market research
- Product feedback
- Employee surveys
- Event registration
- Lead generation
- Academic research
- User testing

## 🔒 Privacy & Security

- Data stored locally (HTML version)
- No external dependencies
- GDPR compliant design
- Secure form submission
- Response anonymization options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use for personal and commercial projects.

## 🆘 Support

- Check the workflow-explanation.html for detailed usage guide
- Review integration-example.html for embedding instructions
- Open issues for bugs or feature requests

## 🔮 Roadmap

- [ ] Real-time collaboration
- [ ] Advanced analytics
- [ ] API integration
- [ ] Multi-language support
- [ ] Advanced screening algorithms
- [ ] Email notifications
- [ ] Custom themes

---

Made with ❤️ for better data collection and user screening.

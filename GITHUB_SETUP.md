# GitHub Setup Instructions

## 🚀 Push to GitHub

Follow these steps to push your Form Generator to GitHub:

### Step 1: Create a GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name it: `form-generator-shareable-links`
4. Add description: "A powerful form generator with shareable links and screening capabilities"
5. Make it **Public** (so others can use it)
6. **Don't** initialize with README (we already have one)
7. Click "Create repository"

### Step 2: Connect Local Repository to GitHub
Open your terminal and run these commands:

```bash
# Navigate to your project folder
cd "c:\Users\Dell\Desktop\New folder"

# Add GitHub repository as remote origin
git remote add origin https://github.com/YOUR_USERNAME/form-generator-shareable-links.git

# Push your code to GitHub
git push -u origin master
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

### Step 3: Enable GitHub Pages (Optional)
1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Pages"
4. Under "Source", select "Deploy from a branch"
5. Select branch: `master` and folder: `/ (root)`
6. Click "Save"

Your form generator will be available at:
`https://YOUR_USERNAME.github.io/form-generator-shareable-links/formgenerator.html`

## 🔧 Deploy Streamlit App

### Option 1: Streamlit Cloud (Free)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select your repository
5. Set main file: `streamlit_app.py`
6. Click "Deploy"

### Option 2: Heroku
1. Create `Procfile`:
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Deploy to Heroku:
```bash
heroku create your-form-generator
git push heroku master
```

### Option 3: Railway
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect Streamlit
4. Deploy automatically

## 🌐 Update URLs for Production

After deployment, update these URLs in your code:

### In `streamlit_app.py` (line ~200):
```python
base_url = "https://YOUR_DEPLOYED_URL"  # Change from localhost
```

### In `formgenerator.html`:
Update any localhost references to your production URL.

## 📝 Repository Structure

Your GitHub repository will contain:
- `formgenerator.html` - Main HTML form generator
- `streamlit_app.py` - Streamlit web application
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- Example files for integration and testing

## 🎯 Next Steps

1. **Test both versions** (HTML and Streamlit)
2. **Share your repository** with others
3. **Create issues** for bug reports
4. **Add features** and improvements
5. **Build a community** around your form generator

Happy coding! 🚀

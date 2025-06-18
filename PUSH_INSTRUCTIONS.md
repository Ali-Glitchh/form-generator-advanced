# 🚀 GitHub Push Instructions

After creating your GitHub repository, run these commands:

## Step 1: Add Remote Repository
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

## Step 2: Rename Branch to Main (GitHub Standard)
```bash
git branch -M main
```

## Step 3: Push to GitHub
```bash
git push -u origin main
```

## Example (Replace with your actual details):
```bash
git remote add origin https://github.com/johndoe/form-generator-advanced.git
git branch -M main
git push -u origin main
```

## If you get authentication errors:
1. Use GitHub Desktop app, or
2. Set up SSH keys, or  
3. Use GitHub CLI: `gh auth login`

## After successful push:
- Your repository will be live at: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
- HTML version will be accessible via GitHub Pages
- Streamlit version can be deployed to Streamlit Cloud

## Repository Settings:
- **Name**: form-generator-advanced (or your choice)
- **Description**: Advanced form generator with conditional logic, skip patterns, and shareable links
- **Visibility**: Public (recommended for sharing)
- **Initialize**: Don't add README, .gitignore, or license (we have them already)

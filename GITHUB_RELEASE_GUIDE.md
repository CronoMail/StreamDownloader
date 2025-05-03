# GitHub Pre-Release Guide

Follow these steps to publish your Stream Downloader pre-release on GitHub:

## 1. Create a GitHub Repository (if you don't have one already)

1. Go to [GitHub](https://github.com/)
2. Click on the "+" icon in the top right, then "New repository"
3. Enter repository name: "stream-downloader" 
4. Add a description: "A modern application for downloading Twitch and YouTube livestreams"
5. Choose Public or Private repository
6. Select "Add a README file" if you want to start with the README you created
7. Choose an appropriate license (e.g., MIT License)
8. Click "Create repository"

## 2. Upload Your Code to GitHub

If you're using Git from the command line:

```
# Initialize a Git repository in your project folder
git init

# Add all files
git add .

# Commit the files
git commit -m "Initial commit for v1.0.0-beta"

# Link to your GitHub repository
git remote add origin https://github.com/yourusername/stream-downloader.git

# Push to GitHub
git push -u origin main
```

Or you can use GitHub Desktop or another Git client.

## 3. Create a Pre-Release

1. Go to your repository on GitHub
2. Click on "Releases" in the right sidebar
3. Click "Create a new release"
4. Click "Choose a tag" and create a new tag: "v1.0.0-beta"
5. Set the release title: "Stream Downloader v1.0.0-beta"
6. Copy the content from RELEASE_NOTES.md into the description box
7. Check the "This is a pre-release" checkbox
8. Upload the ZIP files you created:
   - `stream-downloader-v1.0.0-beta.zip` (Source code)
   - `stream-downloader-v1.0.0-beta-win64-binary.zip` (Windows binary)
9. Click "Publish release"

## 4. Share Your Pre-Release

Once published, you can share the link to your pre-release with potential testers and users. The link will be in this format:

```
https://github.com/yourusername/stream-downloader/releases/tag/v1.0.0-beta
```

## 5. Gather Feedback

Encourage users to:
- Report bugs through GitHub Issues
- Suggest improvements or feature requests
- Provide feedback on usability

## Next Steps

After the pre-release period and receiving feedback:
1. Fix any identified bugs
2. Implement improvements
3. Create a full 1.0.0 release when ready

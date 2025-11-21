# GitHub Repository Setup Instructions

Your local git repository has been initialized and the initial commit has been created. Follow these steps to create a GitHub repository and push your code.

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the repository details:
   - **Repository name**: `SysArch_V1` (or your preferred name)
   - **Description**: "Python Assembly System Library with GUI for managing hierarchical assembly structures"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

## Step 2: Add Remote and Push

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

### Option A: Using HTTPS (Recommended for beginners)

```powershell
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/SysArch_V1.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Option B: Using SSH (If you have SSH keys set up)

```powershell
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin git@github.com:YOUR_USERNAME/SysArch_V1.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 3: Verify

After pushing, refresh your GitHub repository page. You should see all your files there!

## Troubleshooting

### Authentication Issues (HTTPS)
If you get authentication errors with HTTPS:
- GitHub no longer accepts passwords for HTTPS. You need to use a Personal Access Token.
- Create one at: https://github.com/settings/tokens
- Use the token as your password when prompted

### Branch Name
If you get an error about branch names:
- GitHub uses `main` by default, but your local might be `master`
- Use: `git branch -M main` to rename your branch

### Already Have a Remote?
If you get "remote origin already exists":
```powershell
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/SysArch_V1.git
```

## Future Updates

To push future changes:
```powershell
git add .
git commit -m "Your commit message"
git push
```


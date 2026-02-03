# Deployment Walkthrough: SkyStock Analytics 🚀

Follow these steps to get your premium stock dashboard live on the web.

## Phase 1: Create a GitHub Repository

1.  Open your web browser and go to [github.com/new](https://github.com/new).
2.  **Repository name**: Enter `skystock-analytics`.
3.  **Public/Private**: Keep it **Public** (Streamlit Cloud works best with public repos for the free tier).
4.  **Initialize**: Do **NOT** check "Add a README", "Add .gitignore", or "Choose a license" (we already have these files locally).
5.  Click **Create repository**.

## Phase 2: Push Your Code to GitHub

I have already initialized git and committed your files locally. Now you just need to link it to GitHub and push.

1.  In your terminal/command prompt, copy and paste the commands GitHub shows under **"…or push an existing repository from the command line"**. They should look like this:

    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/skystock-analytics.git
    git branch -M main
    git push -u origin main
    ```
    *(Replace `YOUR_USERNAME` with your actual GitHub username)*

## Phase 3: Deploy to Streamlit Community Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"Continue with GitHub"** and sign in.
3.  Once logged in, click the **"Create app"** button (usually in the top right).
4.  Select **"Repository"** if prompted.
5.  **Repository**: Choose `YOUR_USERNAME/skystock-analytics`.
6.  **Branch**: Select `main`.
7.  **Main file path**: It should automatically detect `app.py`. If not, type `app.py`.
8.  **App URL**: You can customize this (e.g., `my-skystock-dashboard`).
9.  Click **Deploy!**

## Phase 4: Verification

1.  Streamlit will start "cooking" your app (installing dependencies from `requirements.txt`).
2.  Once finished, your app will be live at `https://your-custom-name.streamlit.app`.
3.  Enter a ticker like `NVDA` or `AAPL` in the sidebar to test it!

---
**Need help with any specific step?** Just ask!
